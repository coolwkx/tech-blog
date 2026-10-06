---
article_id: kp-184a4272b2ee27bb
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-b5f5d873a117
learning_sourceId: b5f5d873a117
learning_order: 10
learning_objective: 理解并验证：其他省显存手段的关系
---

# 其他省显存手段的关系

> **学习目标**：能够解释「其他省显存手段的关系」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：反向传播与计算图；PyTorch 的优化器状态概念；Transformer 层的结构（注意力矩阵的形状 $b\times a\times s\times s$）；LoRA 的参数量公式（见 [03 篇](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)）。
>
> **所属主题**：全参微调与显存账本 · 关键机制

## 本次只学这一点

| 手段 | 省的是哪一项 | 对吞吐的影响 | 是否改变有效 batch |
| --- | --- | --- | --- |
| `bf16=True`（AMP） | 权重、梯度 | 加快 | 否 |
| gradient accumulation | 激活（允许更小 micro-batch） | 略微变慢（多几次前向反向） | 保持有效 batch 不变 |
| gradient checkpointing | 激活 | 训练变慢 20%～40% | 否 |
| ZeRO-1/2/3 | 优化器状态 / 梯度 / 参数 | 通信增加 | 否 |
| CPU offload | 优化器状态（甚至参数） | 明显变慢 | 否 |
| 8-bit Adam | 优化器状态 | 略慢 | 否 |
| LoRA / QLoRA | 梯度 + 优化器状态（只对少数参数） | 通常更快 | 否 |

**梯度累积与有效 batch 的关系**（常被问）：

$$
B_{\text{有效}} = b_{\text{micro}} \times n_{\text{accum}} \times N_{\text{卡数}}
$$

梯度累积的显存收益来自"可以放心把 $b_{\text{micro}}$ 调小"，本身并不减少单次前向的激活。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「其他省显存手段的关系」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)
