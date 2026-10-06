---
article_id: kp-26c9b52b7d855c86
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-5865c55f8aa7
learning_sourceId: 5865c55f8aa7
learning_order: 3
learning_objective: 理解并验证：输出层的两种加速方案
---

# 输出层的两种加速方案

> **学习目标**：能够解释「输出层的两种加速方案」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇的 one-hot 与词袋、softmax 与交叉熵、PyTorch `nn.Embedding` 的基本用法。
>
> **所属主题**：词向量：Word2Vec 与 FastText · 核心概念

## 本次只学这一点

词表 $V$ 有几万时，每次预测都要在 $V$ 维上做 softmax，代价高到不可接受。两种经典加速：

| 方案 | 思路 | 单步复杂度 | 特点 |
|------|------|-----------|------|
| 层次 Softmax（Hierarchical Softmax） | 用 Huffman 树组织词表，把「$V$ 分类」变成「从根走到叶」的一系列二分类 | $O(\log V)$ | 无近似、数学精确；Huffman 树让高频词路径更短 |
| 负采样（Negative Sampling） | 把「$V$ 分类」改成「真样本 vs $k$ 个噪声样本」的二分类 | $O(k)$，$k$ 常取 5–20 | 更简单更快，NEG 是 word2vec 论文的推荐方案 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/04-词向量-Word2Vec与FastText.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「输出层的两种加速方案」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/04-词向量-Word2Vec与FastText.md)
