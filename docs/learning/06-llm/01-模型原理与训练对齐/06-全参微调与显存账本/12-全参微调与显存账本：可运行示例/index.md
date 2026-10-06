---
article_id: kp-f7e249a0901909b5
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-b5f5d873a117
learning_sourceId: b5f5d873a117
learning_order: 11
learning_objective: 理解并验证：全参微调与显存账本：可运行示例
---

# 全参微调与显存账本：可运行示例

> **学习目标**：能够解释「全参微调与显存账本：可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：反向传播与计算图；PyTorch 的优化器状态概念；Transformer 层的结构（注意力矩阵的形状 $b\times a\times s\times s$）；LoRA 的参数量公式（见 [03 篇](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)）。
>
> **所属主题**：全参微调与显存账本 · 可运行示例

## 本次只学这一点

下面的脚本只依赖标准库：输入模型参数量和训练配置，输出显存估算明细。它实现的是本篇 2.2～2.5 的公式，因此结果**是推导值而非实测值**。注意：全参微调的权重/梯度/优化器状态用 AMP+Adam 的 16 B/参数；LoRA 场景下只对可训练参数计梯度与优化器状态。

依赖：Python 3.8+（仅标准库）。

```python
# -*- coding: utf-8 -*-
"""
全参微调 / PEFT 显存估算器

实现公式（全部为本篇推导）：
  模型状态（AMP + Adam）= 16 字节/可训练参数
      = 2(bf16 权重) + 2(bf16 梯度) + 4(fp32 主权重) + 4(m) + 4(v)
  激活（fp16，无重计算，Megatron-LM 估算式）：
      每层 = s*b*h*(34 + 5*a*s/h) 字节；总 = 每层 * L
  梯度检查点：每层只存输入，约 2*s*b*h 字节
  ZeRO 分片：见 shard_model_state()

注意：本机无 GPU，脚本只做算术，不代表任何真实硬件的实测结果。
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

GiB = 1024 ** 3
GB = 10 ** 9


@dataclass
class ModelSpec:
    name: str
    params: float          # 总参数量（个），例如 7e9
    hidden: int            # 隐藏维度 h
    layers: int            # 层数 L
    heads: int             # 注意力头数 a


@dataclass
class TrainSpec:
    seq_len: int = 2048
    micro_batch: int = 1
    grad_accum: int = 1
    num_gpus: int = 1
    zero_stage: int = 0            # 0=DDP, 1/2/3
    gradient_checkpointing: bool = False
    trainable_ratio: float = 1.0   # 1.0 = 全参；0.001 = LoRA 可训练 0.1%
    optimizer_state_bytes: int = 8  # 纯 Adam(fp32) 的 m+v；AMP 场景由脚本另加 4 字节主权重
    amp: bool = True


def model_state_bytes_per_param(train: TrainSpec) -> tuple:
    """返回 (权重字节, 梯度字节, 优化器字节) 每可训练参数。

    AMP + Adam：2(bf16 权重) + 2(bf16 梯度) + 4(fp32 主权重) + 8(m,v)
    非 AMP：4(权重) + 4(梯度) + 8(m,v)
    """
    if train.amp:
        return 2, 2, 4 + train.optimizer_state_bytes
    return 4, 4, train.optimizer_state_bytes


def shard_model_state(trainable_bytes: dict, train: TrainSpec) -> dict:
    """按 ZeRO 阶段计算每卡显存。

    trainable_bytes 是"全量可训练参数下"的 (权重, 梯度, 优化器) 字节总量。
    为避免复杂化，这里假设：权重分片只在 ZeRO-3 发生；梯度分片在 ZeRO-2/3；
    优化器状态分片在 ZeRO>=1。
    """
    w, g, o = trainable_bytes["weight"], trainable_bytes["grad"], trainable_bytes["opt"]
    n = max(1, train.num_gpus)
    stage = train.zero_stage
    w_p = w / n if stage >= 3 else w
    g_p = g / n if stage >= 2 else g
    o_p = o / n if stage >= 1 else o
    return {"weight": w_p, "grad": g_p, "opt": o_p, "sum": w_p + g_p + o_p}


def activation_bytes(model: ModelSpec, train: TrainSpec) -> float:
    """激活值估算（字节）。"""
    b, s, h, a, L = train.micro_batch, train.seq_len, model.hidden, model.heads, model.layers
    if train.gradient_checkpointing:
        # 只保存每层输入
        return L * 2 * s * b * h
    per_layer = s * b * h * (34 + 5 * a * s / h)
    return L * per_layer


def estimate(model: ModelSpec, train: TrainSpec) -> dict:
    trainable = model.params * train.trainable_ratio
    bw, bg, bo = model_state_bytes_per_param(train)
    total = {
        "weight": trainable * bw,
        "grad": trainable * bg,
        "opt": trainable * bo,
    }
    per_gpu = shard_model_state(total, train)
    act = activation_bytes(model, train)
    # 临时缓冲按激活的 5% 粗估（经验修正项，非实测）
    buffer_bytes = 0.05 * act
    return {
        "trainable_params": trainable,
        "full_model_state": per_gpu,
        "activation": act,
        "buffer": buffer_bytes,
        "per_gpu_total": per_gpu["sum"] + act + buffer_bytes,
    }


def fmt(x: float) -> str:
    return f"{x / GB:8.2f} GB | {x / GiB:8.2f} GiB"


def report(model: ModelSpec, train: TrainSpec) -> None:
    r = estimate(model, train)
    print(f"=== {model.name} | 参数量 {model.params / 1e9:.1f}B | "
          f"可训练 {r['trainable_params'] / 1e9:.4f}B "
          f"({100 * train.trainable_ratio:.3f}%) ===")
    print(f"  序列长度 s={train.seq_len}, micro-batch={train.micro_batch}, "
          f"grad_accum={train.grad_accum}, 卡数={train.num_gpus}, "
          f"ZeRO-{train.zero_stage}, ckpt={train.gradient_checkpointing}, amp={train.amp}")
    eff_batch = train.micro_batch * train.grad_accum * train.num_gpus
    print(f"  有效 batch = {train.micro_batch} × {train.grad_accum} × {train.num_gpus} = {eff_batch}")
    ms = r["full_model_state"]
    print("  --- 模型状态（每卡） ---")
    print(f"    权重        : {fmt(ms['weight'])}")
    print(f"    梯度        : {fmt(ms['grad'])}")
    print(f"    优化器状态  : {fmt(ms['opt'])}")
    print(f"    小计        : {fmt(ms['sum'])}")
    print("  --- 激活与缓冲（每卡） ---")
    print(f"    激活值      : {fmt(r['activation'])}")
    print(f"    临时缓冲~5% : {fmt(r['buffer'])}")
    print(f"  ===> 每卡合计估算 : {fmt(r['per_gpu_total'])}")
    print()


def main() -> None:
    ap = argparse.ArgumentParser(description="显存估算器（推导值，非实测）")
    ap.add_argument("--params-b", type=float, default=7.0, help="总参数量（B）")
    ap.add_argument("--hidden", type=int, default=4096)
    ap.add_argument("--layers", type=int, default=32)
    ap.add_argument("--heads", type=int, default=32)
    ap.add_argument("--seq-len", type=int, default=2048)
    ap.add_argument("--micro-batch", type=int, default=1)
    ap.add_argument("--grad-accum", type=int, default=1)
    ap.add_argument("--gpus", type=int, default=1)
    ap.add_argument("--zero", type=int, default=0, choices=[0, 1, 2, 3])
    ap.add_argument("--ckpt", action="store_true", help="启用 gradient checkpointing")
    ap.add_argument("--trainable-ratio", type=float, default=1.0,
                    help="可训练参数占比，全参=1.0，LoRA(r=8) 约 0.001")
    args = ap.parse_args()

    model = ModelSpec("自定义模型", args.params_b * 1e9,
                      args.hidden, args.layers, args.heads)
    train = TrainSpec(seq_len=args.seq_len, micro_batch=args.micro_batch,
                      grad_accum=args.grad_accum, num_gpus=args.gpus,
                      zero_stage=args.zero, gradient_checkpointing=args.ckpt,
                      trainable_ratio=args.trainable_ratio)

    # 场景 A：单卡全参，无 checkpoing
    report(model, TrainSpec(train.seq_len, train.micro_batch, train.grad_accum,
                            1, 0, False, 1.0))
    # 场景 B：8 卡 ZeRO-3 + 梯度检查点
    report(model, TrainSpec(train.seq_len, train.micro_batch, train.grad_accum,
                            8, 3, True, 1.0))
    # 场景 C：单卡 LoRA（可训练 0.1%）
    report(model, TrainSpec(train.seq_len, 4, 8, 1, 0, False, 0.001))


if __name__ == "__main__":
    main()
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「全参微调与显存账本：可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)
