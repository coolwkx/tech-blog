---
article_id: kp-e5e0034a05aaa3fb
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-7afaf09df2e4
learning_sourceId: 7afaf09df2e4
learning_order: 6
learning_objective: 理解并验证：IDF 与平滑
---

# IDF 与平滑

> **学习目标**：能够解释「IDF 与平滑」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 01 篇的文本预处理与 n-gram 特征、第 02 篇的分词、numpy 稀疏矩阵的直观理解、余弦相似度。
>
> **所属主题**：文本表示：词袋与 TF-IDF · 方法细节

## 本次只学这一点

$$
\text{IDF}(t) = \log\frac{N}{\text{DF}(t)}
$$

其中 $N$ 是文档总数，$\text{DF}(t)$ 是包含词 $t$ 的文档数。两个问题需要平滑处理：

1. 若某词出现在所有文档中（$\text{DF} = N$），则 $\text{IDF} = \log 1 = 0$，该词被完全抹掉。这本身符合预期，但若某词在**整个语料**都没出现（推理时的新词），会除零。
2. 为避免除零并使权重平滑，常用变体：

$$
\text{IDF}(t) = \log\frac{1 + N}{1 + \text{DF}(t)} + 1
$$

这正是 sklearn `TfidfVectorizer` 的**默认行为**（`smooth_idf=True`）：加 1 平滑，并且最后整体加 1，使得「出现在所有文档中的词」IDF 取 1 而不是 0（保证它仍有一点权重、不会完全消失）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/03-文本表示-词袋与TFIDF.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「IDF 与平滑」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/03-文本表示-词袋与TFIDF.md)
