---
article_id: kp-1add3ca2e2fa8876
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-7afaf09df2e4
learning_sourceId: 7afaf09df2e4
learning_order: 5
learning_objective: 理解并验证：TF 的三种变体
---

# TF 的三种变体

> **学习目标**：能够解释「TF 的三种变体」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 01 篇的文本预处理与 n-gram 特征、第 02 篇的分词、numpy 稀疏矩阵的直观理解、余弦相似度。
>
> **所属主题**：文本表示：词袋与 TF-IDF · 方法细节

## 本次只学这一点

$$
\text{TF}(t,d) =
\begin{cases}
f_{t,d} & \text{原始计数} \\
\dfrac{f_{t,d}}{\sum_{t' \in d} f_{t',d}} & \text{归一化频率（防长文档占优）} \\
1 + \log f_{t,d} & \text{对数 TF（抑制高频）}
\end{cases}
$$

注意：原始计数会让长文档的所有词得分都更高，因此**归一化或对数化几乎是必须的**。sklearn 里对应 `sublinear_tf=True` 时使用 $1+\log f$。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/03-文本表示-词袋与TFIDF.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「TF 的三种变体」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/03-文本表示-词袋与TFIDF.md)
