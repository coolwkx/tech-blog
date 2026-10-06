---
article_id: kp-563aa36e59b2e272
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-9bc2a0f8b073
learning_sourceId: 9bc2a0f8b073
learning_order: 12
learning_objective: 理解并验证：微调基础与决策：可运行示例
---

# 微调基础与决策：可运行示例

> **学习目标**：能够解释「微调基础与决策：可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer 与注意力机制；预训练语言模型的 MLM / CLM 目标；LoRA 的公式（见《03-LoRA原理与工程实践》）；基本的 PyTorch 训练循环概念。
>
> **所属主题**：微调基础与决策 · 可运行示例

## 本次只学这一点

下面的脚本**不依赖 torch/transformers**，只用标准库：它把你对任务的描述转成一个决策结论，并顺带估算三种范式的可训练参数量。它验证的是本篇的决策逻辑，而不是模型效果。

依赖：Python 3.8+（仅标准库）。

```python
# -*- coding: utf-8 -*-
"""
微调决策器 + 可训练参数量估算器

用法：
    python finetune_decision.py            # 跑内置示例
    python finetune_decision.py --demo      # 同上

不依赖 torch / transformers，只做决策规则与参数量算术。
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field


@dataclass
class TaskProfile:
    """描述你要解决的问题。"""

    goal: str                      # "knowledge" | "format" | "style" | "capability"
    n_samples: int                 # 可用标注样本量
    has_eval_set: bool = True      # 是否有独立评测集
    facts_change_frequently: bool = False
    base_can_do_it: bool = True    # 换更强的基座是否能解决
    requests_per_day: int = 1000   # 预计线上调用量
    privacy_sensitive: bool = False


@dataclass
class Decision:
    route: str
    reasons: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


def decide(p: TaskProfile) -> Decision:
    """规则式决策。规则来自本篇 1.2 / 1.4 的决策表。"""
    reasons, warnings = [], []

    if not p.has_eval_set:
        warnings.append("没有独立评测集：先建 100~300 条评测集，否则无法判断微调是否变好。")

    if p.privacy_sensitive:
        warnings.append("数据含敏感信息：优先 RAG（条目可删），或先脱敏再训练。")

    if p.facts_change_frequently or p.goal == "knowledge":
        reasons.append("目标是注入/更新事实，且事实可能变化 → 用 RAG 而非微调。")
        return Decision("RAG", reasons, warnings)

    if p.goal == "format" and p.n_samples < 500:
        reasons.append("目标是格式约束且样本不足 → 先 few-shot prompt + 约束解码。")
        return Decision("Prompt(few-shot) ± 约束解码", reasons, warnings)

    if not p.base_can_do_it:
        reasons.append("基座本身不具备该能力（微调不注入新算法）→ 换更强基座或接工具。")
        return Decision("换基座 / 工具调用", reasons, warnings)

    if p.n_samples < 50:
        reasons.append(f"样本仅 {p.n_samples} 条，远低于 LoRA 的经验下限 → 先 ICL。")
        return Decision("Prompt(ICL)", reasons, warnings)

    if p.n_samples < 500:
        reasons.append(f"{p.n_samples} 条样本属于{'格式/风格' if p.goal in ('format', 'style') else '偏少'}区间 → LoRA 只做格式/风格对齐。")
        route = "LoRA（小 r，强正则，密切监控验证集）"
        if p.goal == "capability":
            warnings.append("样本量对能力改造偏少，预期只能小幅提升。")
        return Decision(route, reasons, warnings)

    if p.n_samples <= 5000:
        reasons.append(f"{p.n_samples} 条落在 LoRA 甜点区（500~5000）→ 优先 LoRA / QLoRA。")
        if p.requests_per_day < 200:
            warnings.append("线上调用量很低：微调的一次性成本可能不划算，先算经济账。")
        return Decision("LoRA / QLoRA", reasons, warnings)

    if p.n_samples <= 50000:
        reasons.append(f"{p.n_samples} 条：LoRA 与全参都可，看显存与迭代速度。")
        return Decision("LoRA（先验证）→ 全参（数据够时）", reasons, warnings)

    reasons.append(f"{p.n_samples} 条：数据量已足以支撑全参 SFT。")
    return Decision("全参 SFT", reasons, warnings)


def trainable_params_estimate(
    total_params_b: float,
    hidden: int = 4096,
    n_layers: int = 32,
    targets_per_layer: int = 4,
    lora_rank: int = 8,
    prompt_len: int = 20,
    prefix_layers: int = 0,
) -> dict:
    """估算三种范式的可训练参数量（单位：百万参数, M）。

    推导：
      - LoRA 每个被适配的 d×d 矩阵新增 r*(d+d) = 2*r*d 个参数；
        全参对应 d*d 个参数。
      - Prompt Tuning 只在输入层加 prompt_len 个 d 维向量。
      - Prefix-Tuning 在 prefix_layers 层的 K/V 两处各加 prefix 个 d 维向量（近似 2 倍）。
    """
    d = hidden
    per_matrix_full = d * d
    per_matrix_lora = 2 * lora_rank * d

    lora_total = n_layers * targets_per_layer * per_matrix_lora
    full_total = int(total_params_b * 1e9)
    prompt_tuning_total = prompt_len * d
    prefix_total = prefix_layers * 2 * prompt_len * d

    return {
        "full_M": full_total / 1e6,
        "lora_M": lora_total / 1e6,
        "lora_ratio_pct": 100.0 * lora_total / full_total,
        "prompt_tuning_M": prompt_tuning_total / 1e6,
        "prefix_M": prefix_total / 1e6,
        "per_matrix_full_M": per_matrix_full / 1e6,
        "per_matrix_lora_param": per_matrix_lora,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="微调决策器")
    parser.add_argument("--demo", action="store_true", help="跑内置示例任务")
    parser.parse_args()

    demos = [
        TaskProfile(goal="knowledge", n_samples=0, facts_change_frequently=True),
        TaskProfile(goal="format", n_samples=300),
        TaskProfile(goal="style", n_samples=2000),
        TaskProfile(goal="capability", n_samples=12000),
        TaskProfile(goal="style", n_samples=30),
    ]

    for idx, profile in enumerate(demos, 1):
        d = decide(profile)
        print(f"[示例 {idx}] goal={profile.goal:<10} n={profile.n_samples:<6} -> 路线: {d.route}")
        for r in d.reasons:
            print(f"    理由: {r}")
        for w in d.warnings:
            print(f"    注意: {w}")
        print()

    print("== 7B 模型（d=4096, L=32, 每层 4 个目标矩阵, r=8）可训练参数估算 ==")
    est = trainable_params_estimate(7000.0, hidden=4096, n_layers=32,
                                    targets_per_layer=4, lora_rank=8,
                                    prompt_len=20, prefix_layers=32)
    print(f"  全参            : {est['full_M']:.0f} M (100%)")
    print(f"  LoRA(r=8)       : {est['lora_M']:.2f} M ({est['lora_ratio_pct']:.3f}%)")
    print(f"  Prompt Tuning   : {est['prompt_tuning_M']:.3f} M")
    print(f"  Prefix-Tuning   : {est['prefix_M']:.3f} M")
    print(f"  单个 d×d 矩阵全参 {est['per_matrix_full_M']:.2f} M，LoRA 新增 {est['per_matrix_lora_param']} 个参数")


if __name__ == "__main__":
    main()
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/01-微调基础与决策.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「微调基础与决策：可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/01-微调基础与决策.md)
