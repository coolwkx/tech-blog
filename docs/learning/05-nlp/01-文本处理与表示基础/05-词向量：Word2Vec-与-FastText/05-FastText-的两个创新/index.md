---
article_id: kp-825e1ff3ab1a8050
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-5865c55f8aa7
learning_sourceId: 5865c55f8aa7
learning_order: 4
learning_objective: 理解并验证：FastText 的两个创新
---

# FastText 的两个创新

> **学习目标**：能够解释「FastText 的两个创新」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇的 one-hot 与词袋、softmax 与交叉熵、PyTorch `nn.Embedding` 的基本用法。
>
> **所属主题**：词向量：Word2Vec 与 FastText · 核心概念

## 本次只学这一点

FastText 由 Facebook 提出，是一个「词向量 + 文本分类」的开源工具，与原版 word2vec 相比有两处关键改动：

**创新一：子词（subword）表示。** 每个词不只用一个向量，而是「词向量 + 其所有字符 n-gram 向量」之和。例如 `where`（设 $n=3$）会被拆成 `<wh, whe, her, ere, re>` 加上整词 `<where>`，词向量为：

$$
v_{\text{where}} = \frac{1}{|G|}\sum_{g \in G} z_g
$$

其中 $G$ 是整词与所有 n-gram 的集合。带来的直接好处是**OOV 也能有向量**：训练时见过「肾结石」「胆结石」，遇到未见过的「尿结石」，可以用共享的子词（尿、结、石）拼出一个合理向量。

**创新二：分类头结构极简。** 文本分类时，FastText = 「所有词的向量取平均」+「一层线性分类器」+「softmax」：

$$
\hat{y} = \text{softmax}\big(W \cdot \tfrac{1}{n}\sum_{i=1}^{n} v_{w_i} + b\big)
$$

没有卷积、没有循环、没有注意力，只有一层隐式表示。但正因为简单，它训练极快（几分钟到几十分钟）、推理极快（毫秒级）、模型文件小，在文本分类上常能超过同期的复杂模型，是性价比极高的基线。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/04-词向量-Word2Vec与FastText.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「FastText 的两个创新」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/04-词向量-Word2Vec与FastText.md)
