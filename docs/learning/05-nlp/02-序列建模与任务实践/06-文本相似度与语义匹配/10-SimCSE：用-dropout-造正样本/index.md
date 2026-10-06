---
article_id: kp-f39e491007696fd1
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-ab1dbc27d73f
learning_sourceId: ab1dbc27d73f
learning_order: 9
learning_objective: 理解并验证：SimCSE：用 dropout 造正样本
---

# SimCSE：用 dropout 造正样本

> **学习目标**：能够解释「SimCSE：用 dropout 造正样本」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇的 TF-IDF 与余弦相似度、第 04 篇的词向量、第 08 篇的 attention、第 09 篇的 BERT 与句对任务。
>
> **所属主题**：文本相似度与语义匹配 · 方法细节

## 本次只学这一点

**SimCSE（Simple Contrastive Learning of Sentence Embeddings）** 的洞察非常简洁：**同一个句子过两次 BERT，因为 dropout 的随机性会得到两个略有不同的向量，这两个向量就可以当作正样本对**。

| 设定 | 正样本来源 | 负样本来源 |
|------|-----------|-----------|
| 无监督 SimCSE | 同一句子 + 不同 dropout mask 的两次前向 | 同一个 batch 内的其他句子（in-batch negatives） |
| 有监督 SimCSE | NLI 数据中标注为蕴含的句对 | 标注为矛盾的句对 |

损失用 InfoNCE（对比学习）：

$$
\mathcal{L}_i = -\log\frac{\exp(\cos(u_i, u_i^+)/\tau)}{\sum_{j=1}^{N}\exp(\cos(u_i, u_j)/\tau)}
$$

其中 $\tau$ 是温度系数。工程上有个重要技巧：**去掉 dropout 反而会成为极强的基线**（论文称之为 `unsup-SimCSE` 的「dropout 作为最小数据增强」现象），这也说明 dropout 在句向量学习中起到了隐式正则的作用。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/10-文本相似度与语义匹配.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「SimCSE：用 dropout 造正样本」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/10-文本相似度与语义匹配.md)
