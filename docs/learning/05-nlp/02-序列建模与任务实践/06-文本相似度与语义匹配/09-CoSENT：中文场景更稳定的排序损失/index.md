---
article_id: kp-df2239f091f9b3ba
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-ab1dbc27d73f
learning_sourceId: ab1dbc27d73f
learning_order: 8
learning_objective: 理解并验证：CoSENT：中文场景更稳定的排序损失
---

# CoSENT：中文场景更稳定的排序损失

> **学习目标**：能够解释「CoSENT：中文场景更稳定的排序损失」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇的 TF-IDF 与余弦相似度、第 04 篇的词向量、第 08 篇的 attention、第 09 篇的 BERT 与句对任务。
>
> **所属主题**：文本相似度与语义匹配 · 方法细节

## 本次只学这一点

SBERT 常用的回归损失是 $\text{MSE}(\cos(u,v), \text{label})$，其中 label 是人工相似度分数（如 0–5）。这在中文数据集（LCQMC、BQ Corpus、STS-B 中文版）上有个问题：**不同标注者的相似度尺度不一致**，回归到绝对分数很困难，而且 MSE 损失会把大量算力花在「把 4.0 拟合到 4.2」这种无意义的边际上。

CoSENT（Cosine Sentence）把问题从「回归分数」改成「**排序**」：只要保证「标注分数更高的句子对，其余弦相似度也更高」即可。损失形式为

$$
\mathcal{L} = \log\Big(1 + \sum_{(i,j)\in\Omega,\ \text{label}_i > \text{label}_j}
\exp\big(\lambda(\cos_j - \cos_i)\big)\Big)
$$

其中 $\Omega$ 是一个 batch 内所有可比较的句子对，$\lambda$ 是缩放系数。直觉：只要 $\cos_i > \cos_j$（顺序正确），指数项就小于 1，损失趋近于 $\log 2$；一旦顺序反了，指数项迅速放大，产生大梯度。

CoSENT 在中文句相似度上通常比 SBERT 的 MSE 损失更稳定，因为它不依赖标注分数的绝对尺度，只依赖**相对顺序**——而相对顺序恰恰是人工标注最可靠的部分。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/10-文本相似度与语义匹配.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「CoSENT：中文场景更稳定的排序损失」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/10-文本相似度与语义匹配.md)
