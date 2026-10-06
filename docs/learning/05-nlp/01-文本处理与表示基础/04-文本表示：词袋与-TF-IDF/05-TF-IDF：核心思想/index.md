---
article_id: kp-936fa4083c2aba6d
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-7afaf09df2e4
learning_sourceId: 7afaf09df2e4
learning_order: 4
learning_objective: 理解并验证：TF-IDF：核心思想
---

# TF-IDF：核心思想

> **学习目标**：能够解释「TF-IDF：核心思想」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 01 篇的文本预处理与 n-gram 特征、第 02 篇的分词、numpy 稀疏矩阵的直观理解、余弦相似度。
>
> **所属主题**：文本表示：词袋与 TF-IDF · 核心概念

## 本次只学这一点

TF-IDF 用两个因子相乘来衡量一个词对一篇文档的重要性：

| 因子 | 含义 | 直觉 |
|------|------|------|
| TF（Term Frequency） | 词在**本篇**文档中出现的频率 | 出现越多，越可能反映本篇主题 |
| IDF（Inverse Document Frequency） | 词在**整个语料**中有多稀有 | 越稀有越有区分度，越常见越没用 |

$$
\text{TF-IDF}(t, d) = \text{TF}(t, d) \times \text{IDF}(t)
$$

一句话记忆：**TF 看「这篇里有多少」，IDF 看「全语料里有多稀」**。"的」TF 很高但 IDF 极低（几乎每篇都有），乘积很小；「量子计算」TF 可能只有 1，但 IDF 很高，乘积反而大。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/03-文本表示-词袋与TFIDF.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「TF-IDF：核心思想」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/03-文本表示-词袋与TFIDF.md)
