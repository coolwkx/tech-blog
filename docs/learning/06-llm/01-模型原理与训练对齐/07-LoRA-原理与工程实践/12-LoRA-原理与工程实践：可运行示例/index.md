---
article_id: kp-b8d5967e7e7252af
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-968a88f3144b
learning_sourceId: 968a88f3144b
learning_order: 11
learning_objective: 理解并验证：LoRA 原理与工程实践：可运行示例
---

# LoRA 原理与工程实践：可运行示例

> **学习目标**：能够解释「LoRA 原理与工程实践：可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性层与矩阵乘法；反向传播；Transformer 里 $W_q/W_k/W_v/W_o$ 的形状；显存账本中"梯度 + 优化器状态随可训练参数增长"（见 [02 篇](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)）。
>
> **所属主题**：LoRA 原理与工程实践 · 可运行示例

## 本次只学这一点

下面这份代码**不依赖 `peft`**，从零手写 LoRA 线性层，并演示参数量对比与合并一致性检验。

> **说明**：本机没有 GPU 也没有安装 PyTorch，下面的代码**未在本机执行**，其正确性来自对公式的推导与实现的逐行审查；请在有 `torch` 的环境里运行验证。

依赖：`torch>=2.0`（CPU 或 GPU 均可运行；无 GPU 时会自动使用 CPU）。

```python
# -*- coding: utf-8 -*-
"""
手写 LoRA 线性层：不依赖 peft。

功能：
  1. LoRALinear：把预训练 Linear 包装成带低秩旁路的版本
  2. merge() / unmerge()：合并与反合并，并验证输出一致性
  3. 参数账本：打印 LoRA 分支参数量、占比、以及缩放因子

运行：
  python lora_manual.py
"""

from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F


class LoRALinear(nn.Module):
    """把 nn.Linear 包装为 W0 x + (alpha/r) * B A x。

    约定：
      - self.base : 冻结的原始 Linear（requires_grad=False）
      - self.lora_A: (in_features, r)，kaiming 均匀初始化
      - self.lora_B: (r, out_features)，零初始化 -> 训练起点恒等
      - self.scaling = alpha / r
    """

    def __init__(
        self,
        base: nn.Linear,
        r: int = 8,
        alpha: int = 16,
        dropout: float = 0.0,
        merge_on_init: bool = False,
    ) -> None:
        super().__init__()
        if r <= 0:
            raise ValueError("r 必须为正整数")
        self.r = r
        self.alpha = alpha
        self.scaling = alpha / r
        self.base = base
        for p in self.base.parameters():
            p.requires_grad = False

        self.lora_A = nn.Parameter(torch.empty(base.in_features, r))
        self.lora_B = nn.Parameter(torch.empty(r, base.out_features))
        self.lora_dropout = nn.Dropout(dropout) if dropout > 0 else nn.Identity()
        self.merged = False

        self.reset_lora_parameters()
        if merge_on_init:
            self.merge()

    # ---------- 初始化 ----------
    def reset_lora_parameters(self) -> None:
        nn.init.kaiming_uniform_(self.lora_A, a=math.sqrt(5))
        nn.init.zeros_(self.lora_B)          # 关键：B=0 => 起点 dW=0

    def _delta_weight(self) -> torch.Tensor:
        """返回 (in_features, out_features) 形状的 dW = scaling * A B。"""
        return self.scaling * (self.lora_A @ self.lora_B)

    # ---------- 前向 ----------
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.base(x)                    # frozen 分支
        if self.merged:
            return out
        xd = self.lora_dropout(x)
        # 两次小矩阵乘，避免显式构造 dW（dW 是 d×k 的大矩阵）
        delta = (xd @ self.lora_A) @ self.lora_B * self.scaling
        return out + delta

    # ---------- 合并 / 反合并 ----------
    @torch.no_grad()
    def merge(self) -> None:
        """W0 <- W0 + scaling * A B，并停止使用旁路。"""
        if self.merged:
            return
        self.base.weight.add_(self._delta_weight().t())   # weight: (out, in)
        self.merged = True

    @torch.no_grad()
    def unmerge(self) -> None:
        """回滚合并。"""
        if not self.merged:
            return
        self.base.weight.sub_(self._delta_weight().t())
        self.merged = False

    def extra_repr(self) -> str:
        return (f"in={self.base.in_features}, out={self.base.out_features}, "
                f"r={self.r}, alpha={self.alpha}, scaling={self.scaling:.3f}, "
                f"merged={self.merged}")


def wrap_lora(
    module: nn.Module,
    r: int = 8,
    alpha: int = 16,
    dropout: float = 0.0,
    target_suffixes: tuple = ("q_proj", "v_proj"),
) -> nn.Module:
    """按名字后缀把子模块替换为 LoRALinear（就地修改）。"""
    replaced = []
    for name, child in list(module.named_children()):
        if isinstance(child, nn.Linear) and name.endswith(target_suffixes):
            setattr(module, name, LoRALinear(child, r=r, alpha=alpha, dropout=dropout))
            replaced.append(name)
        else:
            wrap_lora(child, r, alpha, dropout, target_suffixes)
    return module


def param_report(model: nn.Module, label: str) -> None:
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[{label}] 总参数 {total:,} | 可训练 {trainable:,} "
          f"({100.0 * trainable / total:.4f}%)")


class TinyLM(nn.Module):
    """一个用于演示的最小模型：两层含 q_proj/ v_proj/ o_proj 的块。"""

    def __init__(self, hidden: int = 512, n_layers: int = 2) -> None:
        super().__init__()
        self.layers = nn.ModuleList()
        for _ in range(n_layers):
            block = nn.Module()
            block.q_proj = nn.Linear(hidden, hidden, bias=False)
            block.k_proj = nn.Linear(hidden, hidden, bias=False)
            block.v_proj = nn.Linear(hidden, hidden, bias=False)
            block.o_proj = nn.Linear(hidden, hidden, bias=False)
            block.mlp_up = nn.Linear(hidden, 4 * hidden, bias=False)
            self.layers.append(block)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for block in self.layers:
            q = block.q_proj(x)
            v = block.v_proj(x)
            x = block.o_proj(q * v) + block.mlp_up(x)[..., : x.shape[-1]]
        return x


def main() -> None:
    torch.manual_seed(0)
    hidden = 512
    model = TinyLM(hidden=hidden, n_layers=2)
    param_report(model, "原始模型")

    lora_model = TinyLM(hidden=hidden, n_layers=2)
    lora_model.load_state_dict(model.state_dict())
    wrap_lora(lora_model, r=8, alpha=16, dropout=0.05,
              target_suffixes=("q_proj", "v_proj"))
    n_replaced = sum(1 for m in lora_model.modules() if isinstance(m, LoRALinear))
    print(f"替换了 {n_replaced} 个 Linear 为 LoRALinear（每层 q_proj/v_proj，共 2 层）")
    param_report(lora_model, "LoRA(r=8, alpha=16)")

    # --- 参数账本：单个矩阵 2*r*d vs d*d ---
    for r in (4, 8, 16, 32, 64):
        full = hidden * hidden
        lowrank = 2 * r * hidden
        print(f"  r={r:<3} 单个 {hidden}x{hidden} 矩阵：LoRA={lowrank:>8,} "
              f"全参={full:>8,} 占比={100.0 * lowrank / full:6.3f}%")

    # --- 一致性检验：merge 前后输出一致 ---
    x = torch.randn(4, 7, hidden)
    lora_model.eval()
    with torch.no_grad():
        out_before = lora_model(x)
        # 先给 B 一个非零扰动，否则 dW=0，检验没有意义
        for m in lora_model.modules():
            if isinstance(m, LoRALinear):
                nn.init.normal_(m.lora_B, std=0.02)
        out_lora = lora_model(x)
        for m in lora_model.modules():
            if isinstance(m, LoRALinear):
                m.merge()
        out_merged = lora_model(x)
        for m in lora_model.modules():
            if isinstance(m, LoRALinear):
                m.unmerge()
        out_unmerged = lora_model(x)

    print("merge 前后最大绝对误差 :", (out_lora - out_merged).abs().max().item())
    print("unmerge 后与原始差    :", (out_lora - out_unmerged).abs().max().item())
    print("构造 dW 的开销对比     : dW 需", hidden * hidden,
          "个元素；BAx 路径只需中间激活", 4 * 7 * 8, "个元素")


if __name__ == "__main__":
    main()
```

**代码里的几个要点**：

1. `_delta_weight()` 只在 merge 时调用，前向走的是"先降维再升维"的两步乘法（$x\to Ax\in\mathbb{R}^{r}\to BAx$），**不显式构造 $d\times k$ 的 $\Delta W$**，因此训练时显存开销只有 $O(r)$ 级别。
2. `merge()` 里用了 `.t()`：`nn.Linear.weight` 的形状是 `(out_features, in_features)`，而我们的 $A$、$B$ 约定按 `(in, r)`、`(r, out)` 组织，所以 $\Delta W$ 的转置才对应 `weight`。
3. `merge()` 必须放在 `@torch.no_grad()` 下并先判断 `self.merged`，否则重复合并会叠加两次。
4. 一致性检验前手动给 `lora_B` 加了扰动；否则 $\Delta W = 0$，误差恒为 0，检验没有意义。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「LoRA 原理与工程实践：可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)
