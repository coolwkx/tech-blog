---
article_id: kp-afe5cc580f6a0e66
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-94a81d666c0a
learning_sourceId: 94a81d666c0a
learning_order: 4
learning_objective: 理解并验证：BERT 的优缺点
---

# BERT 的优缺点

> **学习目标**：能够解释「BERT 的优缺点」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 08 篇的 Transformer Encoder 与 self-attention、第 04 篇的静态词向量局限、Python 类与 PyTorch 训练循环。
>
> **所属主题**：BERT 与预训练模型 · 核心概念

## 本次只学这一点

| 优点 | 缺点 |
|------|------|
| 预训练 + 微调在 11 项 NLP 任务上取得最优结果 | 模型庞大（110M 起），不利于资源紧张场景与实时上线 |
| 基于 Transformer，比 RNN 高效，可并行且能捕捉长距离依赖 | 中文模型是**字级** token，很多需要词向量的应用无法直接使用；生僻词只能以 `UNK` 代替 |
| 真正的双向上下文，为下游微调留出足够空间 | MLM 的 `[MASK]` 只在训练出现，预测时不出现，存在信息偏差（exposure bias） |
| — | 每个 batch 只有 15% 的 token 参与训练，**收敛比 left-to-right 模型慢很多** |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「BERT 的优缺点」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)
