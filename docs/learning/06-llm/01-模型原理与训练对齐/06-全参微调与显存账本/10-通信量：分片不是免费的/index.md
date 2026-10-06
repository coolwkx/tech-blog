---
article_id: kp-2fb7de49e5213e5e
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-b5f5d873a117
learning_sourceId: b5f5d873a117
learning_order: 9
learning_objective: 理解并验证：通信量：分片不是免费的
---

# 通信量：分片不是免费的

> **学习目标**：能够解释「通信量：分片不是免费的」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：反向传播与计算图；PyTorch 的优化器状态概念；Transformer 层的结构（注意力矩阵的形状 $b\times a\times s\times s$）；LoRA 的参数量公式（见 [03 篇](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)）。
>
> **所属主题**：全参微调与显存账本 · 关键机制

## 本次只学这一点

| 策略 | 每步通信 | 相对 DDP 的通信放大 |
| --- | --- | --- |
| DDP | 1 次梯度 all-reduce | $1\times$ |
| ZeRO-1 | 梯度 reduce-scatter + 参数 all-gather | 与 DDP 同量级 |
| ZeRO-2 | 梯度 reduce-scatter + 参数 all-gather | 与 DDP 同量级 |
| ZeRO-3 / FSDP | 前向 all-gather + 反向 all-gather + 梯度 reduce-scatter | 约 $1.5\times$ |

ZeRO-3 的通信量随层数放大（每层都要 all-gather 一次），因此**当模型能装下时，ZeRO-2 往往比 ZeRO-3 更快**。这是工程上非常实用的一条经验：**能用小的分片级别就不要用大的**。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「通信量：分片不是免费的」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)
