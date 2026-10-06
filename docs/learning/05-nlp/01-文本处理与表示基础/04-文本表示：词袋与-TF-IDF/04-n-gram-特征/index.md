---
article_id: kp-26ab366a13b179d1
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-7afaf09df2e4
learning_sourceId: 7afaf09df2e4
learning_order: 3
learning_objective: 理解并验证：n-gram 特征
---

# n-gram 特征

> **学习目标**：能够解释「n-gram 特征」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 01 篇的文本预处理与 n-gram 特征、第 02 篇的分词、numpy 稀疏矩阵的直观理解、余弦相似度。
>
> **所属主题**：文本表示：词袋与 TF-IDF · 核心概念

## 本次只学这一点

把连续的 $n$ 个 token 组合成一个新特征：

| n | 名称 | 「我 / 爱 / 」的产出 |
|---|------|--------------------------|
| 1 | unigram | 我、爱、 |
| 2 | bi-gram | 我爱、爱 |
| 3 | tri-gram | 我爱 |

实现上一行代码即可：

```python
def add_n_gram(a, n=2):
 return set(zip(*[a[i:] for i in range(n)]))
```

原理：`[a[i:] for i in range(n)]` 得到 `n` 条错位对齐的列表，`zip` 把它们按位置捆成元组。词表为 $V$ 时 bi-gram 理论上界是 $V^2$，因此实际必须用 `min_count`/`min_df` 剪掉低频 n-gram。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/03-文本表示-词袋与TFIDF.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「n-gram 特征」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/03-文本表示-词袋与TFIDF.md)
