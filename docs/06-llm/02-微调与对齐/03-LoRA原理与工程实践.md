# LoRA 原理与工程实践

> **一句话总结**：LoRA 冻结预训练权重 $W$，只训练一对低秩矩阵 $B\in\mathbb{R}^{d\times r}$、$A\in\mathbb{R}^{r\times k}$，把更新写成 $h = Wx + \frac{\alpha}{r}BAx$，参数量从 $dk$ 降到 $r(d+k)$；它的工程价值在于**可合并**（推理零延迟）、**可插拔**（一份基座挂多份 adapter）、**可低精度训练**（配合 QLoRA）。
> **前置知识**：线性层与矩阵乘法；反向传播；Transformer 里 $W_q/W_k/W_v/W_o$ 的形状；显存账本中"梯度 + 优化器状态随可训练参数增长"（见 [02 篇](02-全参微调与显存账本.md)）。
> **学完能做到**：
> 1. 自己手写一个 LoRA 线性层，包括零初始化、前向公式、merge/unmerge，并验证合并前后输出一致。
> 2. 根据任务类型选择 $r$、$\alpha$、dropout 与 `target_modules`，并说明每个超参的作用。
> 3. 判断什么场景该合并权重、什么场景该保留 adapter，以及为什么。

## 1. 核心概念

### 1.1 LoRA 在 PEFT 家族里的位置

| 方法 | 可训练参数加在哪 | 是否占用序列长度 | 推理是否引入延迟 | 是否可合并 | 典型可训练参数占比 |
| --- | --- | --- | --- | --- | --- |
| **LoRA** | 线性层旁的旁路 $BA$ | 否 | 合并后无；不合并有 | **是** | 0.01%～1% |
| Adapter | 层间插入小 MLP | 否 | 有（多了一层串行） | 否 | 0.5%～5% |
| Prefix-Tuning | 每层注意力的 K/V 前缀 | **是** | 有 | 否 | 0.1%～1% |
| Prompt Tuning | 输入层伪 token 嵌入 | **是** | 有（可忽略） | 否 | 0.001%～0.1% |
| P-Tuning v2 | 每层的前缀 | **是** | 有 | 否 | 0.1%～3% |
| BitFit | 只训 bias | 否 | 无 | 是 | <0.1% |
| DoRA | 权重分解为幅度 + 方向，只训方向 | 否 | 合并后无 | 是 | 同 LoRA 量级 |

LoRA 之所以成为事实标准，正是上表最后三列的联合结果：**不占序列长度、可合并成零额外延迟、且实现足够简单**。

### 1.2 超参速查表

| 超参 | 作用 | 推荐取值 | 调大后的影响 |
| --- | --- | --- | --- |
| $r$（rank） | 低秩子空间维度，决定容量 | 通用 8～16；风格/格式 4～8；复杂任务 32～64；代码/数学 64～128 | 容量上升、显存上升、过拟合风险上升、可能学得更慢 |
| $\alpha$（lora_alpha） | 缩放因子，与 $r$ 共同决定有效尺度 $\alpha/r$ | 常用取 $\alpha = r$（即 $\alpha/r = 1$）或 $\alpha = 2r$ | 等效于放大 LoRA 分支的学习率，过大会不稳定 |
| $\alpha/r$（缩放比） | 实际的更新幅度 | 1～2 | 过大：训练震荡；过小：LoRA 学不动 |
| dropout | LoRA 分支上的 dropout | 0.05～0.1 | 正则更强，小数据上防过拟合，过大则欠拟合 |
| `target_modules` | 把 LoRA 加到哪些线性层 | 起步 `q_proj`,`v_proj`；效果好再扩到 `k_proj`,`o_proj`,`gate_proj`,`up_proj`,`down_proj` | 覆盖越广参数越多、效果上限越高、显存与存储上升 |
| `bias` | 是否训练 bias | `none`（默认） | `all` 会略微提升效果但增加参数 |
| 学习率 | —— | $1\times10^{-4}$～$3\times10^{-4}$（通常是全参的 10 倍量级） | 过大直接发散；过小几乎学不动 |
| LR scheduler | —— | cosine + warmup 3%～10% | —— |

> **一条实用经验**：先固定 $r=8$、$\alpha=16$（$\alpha/r=2$）、dropout 0.05，只调 `target_modules` 和学习率。等目标模块确定后再调 $r$ 与 $\alpha$。反过来先调 $r$ 往往是在浪费算力。

### 1.3 合并与不合并：部署方式的取舍

| 维度 | 合并（`merge_and_unload`） | 不合并（保留 adapter） |
| --- | --- | --- |
| 推理延迟 | 与原始模型完全相同 | 每个被适配的线性层多两次小矩阵乘（$d\times r$ 与 $r\times k$），通常增加 5%～20% |
| 显存 | 只有合并后的权重 | 权重 + 少量 adapter 参数 |
| 多任务 | 要 N 份完整权重 | 一份基座 + N 个 adapter，可热插拔 |
| 切换任务 | 需要重新加载整份权重 | 秒级切换，适合多租户 |
| 精度影响 | 合并会在原权重上做一次加法，若基座被量化过则需先反量化（QLoRA 场景不能直接合并进 nf4 权重） | 无精度损失 |
| 适用场景 | 单任务生产部署、追求极限延迟 | 多任务服务、A/B 实验、需要随时回滚 |

**一个容易忽略的点**：合并后的产物是**一份完整模型权重**，其体积与基座相同。如果你管理 50 个下游任务，合并方案要存 50 份 7B 权重（约 50×14 GB），而不合并只要 1 份基座 + 50 个小文件。

### 1.4 常见应用形态

| 形态 | 做法 | 典型用途 |
| --- | --- | --- |
| 单任务 LoRA | 一个任务训一个 adapter | 垂直场景微调 |
| 多 adapter 服务 | 基座常驻，按请求路由 adapter | 多租户 SaaS |
| LoRA 集合加权 | 推理时对多个 adapter 的 $BA$ 做加权求和（如 `add_weighted_adapter`） | 能力混合、模型融合 |
| 继续预训练 + LoRA | 在领域语料上用 LoRA 做 DAPT | 领域适配（比全参便宜） |
| QLoRA | nf4 量化基座 + LoRA | 单卡 24 GB 内微调 7B～13B |
| LoRA + 蒸馏 | 学生模型学 LoRA 后的教师输出 | 压缩 |

## 2. 关键机制

### 2.1 核心公式与参数量推导

对一个预训练权重矩阵 $W_0\in\mathbb{R}^{d\times k}$（$d$ 为输出维度，$k$ 为输入维度），LoRA 把更新约束为低秩分解：

$$
W = W_0 + \Delta W = W_0 + \frac{\alpha}{r}\,B A,
\qquad B\in\mathbb{R}^{d\times r},\ A\in\mathbb{R}^{r\times k}
$$

前向传播为：

$$
h = W_0 x + \Delta W x = W_0 x + \frac{\alpha}{r}\,B A x,\qquad x\in\mathbb{R}^{k}
$$

训练时 $W_0$ 冻结（`requires_grad=False`），只有 $A$、$B$ 参与梯度更新。

**参数量推导**：

$$
\underbrace{dk}_{\text{全参更新}} \;\longrightarrow\; \underbrace{dr + rk}_{A \text{ 与 } B} = r(d+k)
$$

当代入典型的方阵 $d=k$ 时：

$$
r(d+d) = 2dr \quad\text{vs}\quad d^2
$$

压缩比为：

$$
\frac{2dr}{d^2} = \frac{2r}{d}
$$

**数值例（推导）**：$d=k=4096$、$r=8$ 时

$$
2dr = 2\times8\times4096 = 65{,}536,\qquad d^2 = 16{,}777{,}216
$$

$$
\frac{65536}{16777216} = 0.3906\%
$$

即单个 $4096\times4096$ 矩阵的 LoRA 参数只占该矩阵的 **0.39%**。整个 7B 模型上（$r=8$，只适配 $W_q,W_v$，32 层）新增参数为

$$
32 \times 2 \times 65{,}536 = 4{,}194{,}304 \approx 4.19\text{M}
$$

占 7B 的 $0.0599\%$。若把六个投影矩阵全部适配（$q,k,v,o,\text{gate},\text{up},\text{down}$ 共 7 个），新增约 $14.7$ M，占 $0.21\%$。

### 2.2 初始化：为什么 $B$ 必须为零

LoRA 的初始化是：

$$
A \sim \mathcal{N}(0,\sigma^2)\ \text{或 Kaiming 均匀},\qquad B = \mathbf{0}
$$

于是训练开始时 $\Delta W = \frac{\alpha}{r}BA = 0$，模型输出与预训练模型**完全一致**。

这个性质带来三个好处：

1. **训练起点无损**。不会像随机初始化的 Adapter 那样在开始时破坏基座表征。
2. **梯度不会一开始就爆炸**。$\frac{\partial \mathcal{L}}{\partial A} = \frac{\alpha}{r}B^{\top}\frac{\partial\mathcal{L}}{\partial h}x^{\top}$，由于 $B=0$，第一步 $A$ 的梯度为 0，只有 $B$ 先动；等 $B$ 非零后 $A$ 才开始有效更新。这实际上起到了一个"软启动"的作用。
3. **可以安全地给任意层加 LoRA**，不会因为加得太多而破坏前向。

注意：两个矩阵都初始化为零是不行的（梯度永远为零）；只把 $B$ 置零、$A$ 随机是标准做法。

### 2.3 梯度推导

设 $\tilde{h} = \frac{\alpha}{r}BAx$，损失对输出的梯度记为 $g = \frac{\partial \mathcal{L}}{\partial h}\in\mathbb{R}^{d}$，则

$$
\frac{\partial \mathcal{L}}{\partial B} = \frac{\alpha}{r}\,g\,(Ax)^{\top}\in\mathbb{R}^{d\times r},
\qquad
\frac{\partial \mathcal{L}}{\partial A} = \frac{\alpha}{r}\,(B^{\top}g)\,x^{\top}\in\mathbb{R}^{r\times k}
$$

两个关键观察：

- **梯度只经过 $A$、$B$**，$W_0$ 完全没有梯度，因此**没有优化器状态**，这是 LoRA 省显存的根本原因（对比 [02 篇](02-全参微调与显存账本.md) 的 16 B/参数）。
- 计算 $\frac{\partial \mathcal{L}}{\partial A}$ 需要 $B^{\top}g$，计算 $\frac{\partial \mathcal{L}}{\partial B}$ 需要 $Ax$，所以**前向时必须缓存 $Ax$**（$r$ 维，很小）和 $x$（$k$ 维）。这一点决定了一个实现细节：如果你的 LoRA 层要在 `merge` 之后继续训练，必须能重新拿到 $Ax$。

**缩放因子的梯度效应**：$\alpha/r$ 同时出现在两个梯度里，所以它等价于**缩放 LoRA 分支的学习率**。这就是"改 $r$ 时要同步改 $\alpha$"的原因——如果只把 $r$ 从 8 调到 32 而 $\alpha$ 不变，$\alpha/r$ 从 2 掉到 0.5，等效学习率降了 4 倍，你会误以为"增大 $r$ 没用"。

### 2.4 低秩假设的直觉

LoRA 能工作的前提是 $\Delta W$ 近似低秩。三个层面的直觉解释：

1. **奇异值谱层面**。LoRA 原论文（[arXiv:2106.09685](https://arxiv.org/abs/2106.09685)）做了对照实验：把微调得到的 $\Delta W$ 直接投影到 $r=8$ 的子空间（取前 8 个奇异向量），性能与完整 LoRA 相当接近；这说明**微调真正用到的方向很少**。
2. **本征维度层面**。*Measuring the Intrinsic Dimension of Objective Landscapes*（[arXiv:1804.00792](https://arxiv.org/abs/1804.00792)）指出，很多任务的优化景观存在一个远小于参数量的**本征维度**，在低维子空间里优化就能达到不错的效果，LoRA 是这一思想的直接应用。
3. **信息层面**。微调数据通常只有几千到几万条，每条样本携带的"新信息量"有限，能改变模型行为的方向数量自然受数据规模约束，不可能用满 $d^2$ 个自由度。

反过来，这也解释了 LoRA 失效的边界：**当任务是"学一门新技能"而不是"调整已有技能的表达方式"时，$\Delta W$ 的秩会显著上升**，此时需要更大的 $r$ 甚至全参微调。经验上的信号是：训练 loss 降不下去，且增大 $r$ 收益饱和得很慢。

### 2.5 该加在哪些层：原论文的消融

LoRA 原论文报告的一个重要结论是：**在相同参数预算下，把可训练参数集中在 $W_q$ 和 $W_v$ 上，比集中在单个矩阵（如只有 $W_q$）或只放 $W_k$ 效果更好**（参见 [arXiv:2106.09685](https://arxiv.org/abs/2106.09685) 的消融章节）。

工程上的分层策略：

| 阶段 | target_modules | 新增参数（7B，$r=8$，$L=32$） | 适用 |
| --- | --- | --- | --- |
| 最小验证 | `q_proj`, `v_proj` | ≈ 4.19 M | 快速验证任务是否可学 |
| 常规 | `q_proj`,`k_proj`,`v_proj`,`o_proj` | ≈ 8.39 M | 大多数风格/格式任务 |
| 全线性层 | 再加 `gate_proj`,`up_proj`,`down_proj` | ≈ 14.7 M | 复杂任务、数据量较大 |
| 含 MLP 扩维比 | 注意 `down_proj` 是 $h\times d_{\text{ff}}$（$d_{\text{ff}}$ 常为 $h$ 的 2.7～3.5 倍），参数量比注意力层更大 | —— | 需要按实际形状计算 |

> 上表的参数量按 $d=k=h=4096$ 的方阵近似估算（**推导**）；真实实现中 `down_proj` 的输入维度是 FFN 中间维度，因此实际值略大于表中数字。最可靠的做法是用 `model.print_trainable_parameters()` 读真实值。

### 2.6 合并的数学等价性与精度问题

**等价性**：因为加法对线性映射是分配的，

$$
h = W_0x + \frac{\alpha}{r}BAx = \left(W_0 + \frac{\alpha}{r}BA\right)x = W_{\text{merged}}\,x
$$

所以合并后**输出完全一致**（在浮点意义上是"接近一致"，见下）。

**精度问题**：合并时会执行一次加法 $W_0 + \frac{\alpha}{r}BA$。如果 $W_0$ 是 bf16/fp16，$BA$ 项又很小（$\alpha/r$ 缩放后常常量级很小），直接相加会有**有效位丢失**——小量被大数的舍入吃掉。工程做法是：

- 先升到 fp32 做加法，再决定是否降回 fp16（会多花显存）；
- 或者在**不合并**模式下部署，避免任何舍入；
- **QLoRA 场景不能把 adapter 合并回 nf4 权重**：nf4 是分块量化的，加法的结果无法用同一套量化常量表示。正确做法是先把基座反量化到 bf16/fp16，再做合并。

### 2.7 相关的后续改进

> **说明**：本节内容超出你提供的课程资料范围，基于公开文档与论文整理。

| 方法 | 核心改动 | 论文 |
| --- | --- | --- |
| DoRA | 把 $W$ 分解为幅度 $m$ 与方向 $V/\|V\|$，只对方向做 LoRA 更新，幅度单独训练 | [arXiv:2402.09353](https://arxiv.org/abs/2402.09353) |
| LoRA+ | 给 $A$ 和 $B$ 用不同学习率（$B$ 的学习率更大） | [arXiv:2402.12354](https://arxiv.org/abs/2402.12354) |
| rsLoRA | 把缩放从 $\alpha/r$ 改为 $\alpha/\sqrt{r}$，使大 $r$ 时训练更稳定 | [arXiv:2312.03732](https://arxiv.org/abs/2312.03732) |
| VeRA / LoHa 等 | 用共享随机基 + 极小可训练向量进一步压参数 | 见各自论文 |

## 3. 可运行示例

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

## 4. 常见坑

| 现象 | 原因 | 解决 |
| --- | --- | --- |
| 训练 loss 完全不降 | `target_modules` 一个都没匹配上（名字不对，例如模型用 `W_pack` 或 `query_key_value`），或学习率太低 | 先打印 `model.named_modules()` 确认真实层名；`print_trainable_parameters()` 确认可训练参数不为 0 |
| 增大 $r$ 效果反而变差 | $\alpha$ 没跟着调，$\alpha/r$ 变小导致等效学习率下降 | 保持 $\alpha = 2r$ 或固定 $\alpha/r$；或改用 rsLoRA 的 $\alpha/\sqrt{r}$ 缩放 |
| 训练一开始就发散 | 学习率沿用全参的 $2\times10^{-5}$ 却把 $\alpha/r$ 设得很大，或 dropout=0 且数据很少 | LoRA 学习率用 $1\times10^{-4}$～$3\times10^{-4}$；先跑 20 步看 loss |
| 忘了 merge，线上延迟比预期高 | 部署时仍走旁路分支 | 单任务部署前 `merge_and_unload()`；量化基座要先反量化再合并 |
| 多 adapter 冲突，输出变乱 | 同时激活了多个 adapter 或加权系数和为 0 | 明确 `set_adapter()`；加权融合时检查权重；`disable_adapter()` 做基线对比 |
| 合并后效果比不合并差一截 | fp16 加法精度损失（小量被吞掉） | 用 fp32 合并后再降精度；或干脆不合并部署 |
| LoRA 训完通用能力下降 | 学习率偏大或 epoch 过多（虽然比全参轻，但仍会遗忘） | 降学习率/epoch；混入少量通用数据 |
| 保存的 adapter 加载后无效 | 只存了 adapter 权重但推理时用基座创建模型却未 `PeftModel` 包装 | 用 `PeftModel.from_pretrained(base, adapter_dir)`；同时保存 tokenizer |
| `down_proj` 加上后参数量暴涨 | FFN 中间维度通常是 $h$ 的 2.7～3.5 倍，是非方阵 | 单独核算每个矩阵的 `in/out`；必要时只给 MLP 的 `up_proj` 加 |
| 从 checkpoint 恢复训练后 loss 跳变 | `lora_B` 零初始化被覆盖，或优化器状态未一起保存 | 保存/加载 `optimizer.pt` 与 `scheduler.pt`；确认 `resume_from_checkpoint` |
| 两阶段 LoRA（先 A 任务再 B 任务）互相遗忘 | 用同一份 adapter 顺序训练 | 每个任务一个 adapter 目录，或做数据混合 |

## 5. 面试问答

**Q1：LoRA 为什么能省显存？省的是哪一部分？**

<details>
<summary>参考答案</summary>

省的是**梯度与优化器状态**这两部分，而不是激活值。

全参微调时每个参数都要存梯度（bf16 下 2 字节）以及 Adam 的 $m$、$v$（fp32 各 4 字节）和 fp32 主权重（4 字节），合计 16 字节/参数。LoRA 把 $W_0$ 冻结，只有 $A$（$k\times r$）和 $B$（$r\times d$）需要这些开销，参数量从 $dk$ 降到 $r(d+k)$，因此在 $d=k=4096,r=8$ 时约为原来的 0.39%。

权重本身并没有变小（$W_0$ 仍在显存里），激活值也不会因为 LoRA 而减少（除非同时配合 gradient checkpointing）。所以 LoRA 的显存收益与 $r$ 成正比，$r$ 越大收益越小。

</details>

**Q2：$\alpha$ 和 $r$ 到底是什么关系？为什么推荐 $\alpha = 2r$ 这类比例写法？**

<details>
<summary>参考答案</summary>

前向是 $h = W_0x + \frac{\alpha}{r}BAx$，$\frac{\alpha}{r}$ 是乘在 LoRA 分支上的缩放。由于它同时乘在 $\frac{\partial\mathcal{L}}{\partial A}$ 与 $\frac{\partial\mathcal{L}}{\partial B}$ 上，**它实际上等价于缩放 LoRA 分支的学习率**。

因此只调 $r$ 而不调 $\alpha$ 会同时改变两件事：容量（$r$）和有效学习率（$\alpha/r$），实验结论会被混淆。固定比例（例如 $\alpha = 2r$）的意义是让"扫描 $r$"变成只改变容量的单变量实验。

补充一点：有工作指出用 $\alpha/\sqrt{r}$（rsLoRA）在大 $r$ 时更稳定，因为 $\alpha/r$ 会让大 $r$ 的有效更新幅度衰减太快。

</details>

**Q3：什么情况下你会选择不合并 LoRA 权重？**

<details>
<summary>参考答案</summary>

三类场景：

1. **多任务/多租户服务**：一份基座常驻显存，按请求加载不同 adapter，切换成本是毫秒级；合并则要为每个任务加载一份完整权重，显存和时间都不划算，而且会破坏基座的共享。
2. **需要高频切换或 A/B 实验**：不合并可以动态启用/禁用适配器（`disable_adapter()` 直接得到基座输出作为对照）。
3. **基座是量化权重（QLoRA）**：nf4 权重无法直接与 bf16 的 $\Delta W$ 相加，合并前必须先反量化，代价大且可能损失精度。

反之，单任务、追求最低推理延迟的生产部署应该合并，因为合并后与原模型结构完全相同，**零额外延迟**。

</details>

## 6. 自测题

**1. $d=4096$、$k=4096$、$r=16$，LoRA 新增参数量与占比是多少？若 $r$ 改成 64 呢？**

<details>
<summary>参考答案</summary>

$r=16$：$r(d+k) = 16\times8192 = 131{,}072$，占比 $131072/16{,}777{,}216 = 0.7813\%$。
$r=64$：$64\times8192 = 524{,}288$，占比 $3.125\%$。
可见占比随 $r$ **线性**增长，而容量（子空间维度）也线性增长——这也是"$r$ 不是越大越好"的原因：收益递减但成本线性。

</details>

**2. 为什么 $B$ 要零初始化而 $A$ 要随机初始化？两个都零会怎样？**

<details>
<summary>参考答案</summary>

$B=0$ 使 $\Delta W = BA = 0$，训练起点与预训练模型完全一致，不破坏基座表征，也让训练更稳定。$A$ 必须随机，否则梯度恒为 0：$\frac{\partial\mathcal{L}}{\partial B} = \frac{\alpha}{r}g(Ax)^{\top}$ 在 $A=0$ 时为 0，$\frac{\partial\mathcal{L}}{\partial A}$ 在 $B=0$ 时也为 0，两者都零就永远学不动。

顺带一个值得说的细节：因为 $B_0=0$，第一步 $A$ 的梯度为 0，只有 $B$ 更新；等 $B$ 非零后 $A$ 才被激活，形成一个自然的"软启动"。

</details>

**3. 写出 LoRA 前向的两种等价实现，并说明训练时该用哪一种。**

<details>
<summary>参考答案</summary>

实现一（显式构造 $\Delta W$）：$h = W_0x + \frac{\alpha}{r}(BA)x$，先算 $d\times k$ 的矩阵 $BA$ 再与 $x$ 相乘。
实现二（两步低秩乘）：$h = W_0x + \frac{\alpha}{r}B(Ax)$，先降维到 $r$ 再升维。

训练时必须用实现二，因为实现一每次前向都要物化 $d\times k$ 的中间矩阵，显存与计算都不划算。合并（merge）时才用实现一的思想，把 $\frac{\alpha}{r}BA$ 一次性加到 $W_0$ 上。两者数学等价但开销差一个数量级。

</details>

**4. 合并 LoRA 时如果用 fp16 直接相加，可能出现什么问题？**

<details>
<summary>参考答案</summary>

$\Delta W$ 经 $\alpha/r$ 缩放后数值通常远小于 $W_0$ 的元素量级。fp16 只有 10 位尾数，当 $|W_0|\gg|\Delta W|$ 时，相加会发生**有效位丢失**（swamping），$\Delta W$ 的大部分信息被舍入掉，导致合并后效果比不合并差。

解决：先在 fp32 下计算 $W_0 + \frac{\alpha}{r}BA$，再决定是否降回 fp16；或者直接以不合并的方式部署。QLoRA 场景更严格：nf4 基座必须先反量化才能合并。

</details>

**5. 你的 LoRA 训练 loss 一直停在 2.1 附近不降，列出排查顺序。**

<details>
<summary>参考答案</summary>

① 先 `print_trainable_parameters()`——如果可训练参数是 0，说明 `target_modules` 根本没匹配上（层名不对，很多模型用 `W_pack`、`c_attn`、`query_key_value` 等）。② 打印一个 batch 的 label，确认 label 没有全被 mask 成 -100（见 [05 篇](05-SFT训练循环与框架.md)）。③ 检查学习率是否过低（LoRA 通常需要 $1\times10^{-4}$ 以上）。④ 检查 $\alpha/r$ 是否过小。⑤ 检查数据本身是否有信号（把 loss 换成"直接记住 5 条样本"的过拟合测试，若连 5 条都记不住，问题在代码而非超参）。⑥ 尝试把 $r$ 从 8 提到 32，若出现下降说明是容量问题。

</details>

## 7. 延伸阅读

- [LoRA: Low-Rank Adaptation of Large Language Models (arXiv:2106.09685)](https://arxiv.org/abs/2106.09685) —— 原始论文，含秩消融与 $W_q/W_v$ 的对比实验。
- [HuggingFace PEFT — LoRA 指南](https://huggingface.co/docs/peft/developer_guides/lora) —— `LoraConfig` 全部字段、`merge_and_unload`、多 adapter 管理。
- [HuggingFace PEFT — 概念与模型指南](https://huggingface.co/docs/peft/package_reference/lora) —— API 参考。
- [Measuring the Intrinsic Dimension of Objective Landscapes (arXiv:1804.00792)](https://arxiv.org/abs/1804.00792) —— 低维子空间优化的理论直觉。
- [DoRA: Weight-Decomposed Low-Rank Adaptation (arXiv:2402.09353)](https://arxiv.org/abs/2402.09353)。
- [LoRA+: Efficient Low Rank Adaptation of Large Models (arXiv:2402.12354)](https://arxiv.org/abs/2402.12354)。
- [A Rank Stabilization Scaling Factor for Fine-Tuning with LoRA (arXiv:2312.03732)](https://arxiv.org/abs/2312.03732) —— rsLoRA 的 $\alpha/\sqrt{r}$ 缩放。
- [Adapter: Parameter-Efficient Transfer Learning for NLP (arXiv:1902.00751)](https://arxiv.org/abs/1902.00751) —— Adapter 的原始工作与推理延迟问题。
- [Prefix-Tuning: Optimizing Continuous Prompts for Generation (arXiv:2101.00190)](https://arxiv.org/abs/2101.00190) —— 前缀方法占用序列长度的问题来源。
- [QLoRA: Efficient Finetuning of Quantized LLMs (arXiv:2305.14314)](https://arxiv.org/abs/2305.14314) —— 与 LoRA 的组合，见 [04 篇](04-QLoRA与量化微调.md)。

---

[⬅️ 返回本章目录](README.md)
