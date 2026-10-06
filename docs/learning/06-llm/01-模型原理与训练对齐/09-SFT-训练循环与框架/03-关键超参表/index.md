---
article_id: kp-329a7387c1b172e6
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-b7b8e8f583cb
learning_sourceId: b7b8e8f583cb
learning_order: 2
learning_objective: 理解并验证：关键超参表
---

# 关键超参表

> **学习目标**：能够解释「关键超参表」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：因果语言模型的训练目标；tokenizer 与特殊 token（BOS/EOS/PAD）；交叉熵损失；LoRA 的注入方式（见 [03 篇](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)）与显存账本（见 [02 篇](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)）。
>
> **所属主题**：SFT 训练循环与框架 · 核心概念

## 本次只学这一点

| 超参 | 全参 SFT 经验区间 | LoRA SFT 经验区间 | 说明 |
| --- | --- | --- | --- |
| learning rate | $1\times10^{-5}$～$5\times10^{-5}$ | $1\times10^{-4}$～$3\times10^{-4}$ | LoRA 只训少量参数，需要更大步长 |
| epochs | 2～3 | 2～5 | 超过 3 轮在指令数据上极易过拟合/复读 |
| per_device_batch_size | 受显存限制 | 同左 | 与 `max_seq_len` 强耦合 |
| gradient_accumulation_steps | 使有效 batch $\approx$ 32～128 | 同左 | 有效 batch = micro × accum × 卡数 |
| warmup_ratio | 0.03～0.1 | 0.03～0.1 | 防早期发散 |
| lr_scheduler | cosine | cosine | linear 也可 |
| weight_decay | 0.0～0.1 | 0.0 | 指令数据上通常 0 或很小 |
| max_grad_norm | 1.0 | 1.0 | 梯度裁剪 |
| max_seq_len | 1024～4096 | 同左 | 超过训练长度会静默截断 |
| gradient_checkpointing | 长序列必开 | 长序列必开 | 换时间省显存 |
| bf16 | 推荐 | 推荐 | 比 fp16 稳，无需 loss scaling |
| packing | 视情况 | 视情况 | 提升吞吐，但需 attention mask 正确 |

> 上表是**社区与官方文档中的常见取值区间**，不是普适最优值。任何超参都应通过小规模扫描（例如 3 个学习率 × 2 个 epoch）在自建评测集上确定。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/05-SFT训练循环与框架.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「关键超参表」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/05-SFT训练循环与框架.md)
