---
article_id: kp-d26091c962fa4fd2
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-94a81d666c0a
learning_sourceId: 94a81d666c0a
learning_order: 7
learning_objective: 理解并验证：BERT 处理长文本
---

# BERT 处理长文本

> **学习目标**：能够解释「BERT 处理长文本」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 08 篇的 Transformer Encoder 与 self-attention、第 04 篇的静态词向量局限、Python 类与 PyTorch 训练循环。
>
> **所属主题**：BERT 与预训练模型 · 方法细节

## 本次只学这一点

BERT 预训练时接收的最大序列长度是 **512**。超长文本需要特殊截断策略：

| 策略 | 做法 | 适用 |
|------|------|------|
| head-only | 只保留前 510 个 token（留 2 个位置给 `[CLS]` 和 `[SEP]`） | 关键信息在开头（新闻导语） |
| tail-only | 只保留最后 510 个 token | 关键信息在结尾（结论、判决书尾部） |
| head+tail | 文本 ≤ 800 时取前 128 + 后 382；> 800 时取前 256 + 后 254 | 关键信息两端都有（长评论、病历） |

工程上还有两条路：**分块（chunking）** 后对多块结果聚合（投票/求平均），或改用 Longformer / BigBird 这类支持长序列的稀疏注意力模型。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「BERT 处理长文本」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)
