---
article_id: kp-cf8f16e00a95831f
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-5865c55f8aa7
learning_sourceId: 5865c55f8aa7
learning_order: 1
learning_objective: 理解并验证：分布假设
---

# 分布假设

> **学习目标**：能够解释「分布假设」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇的 one-hot 与词袋、softmax 与交叉熵、PyTorch `nn.Embedding` 的基本用法。
>
> **所属主题**：词向量：Word2Vec 与 FastText · 核心概念

## 本次只学这一点

一切词向量方法都建立在一个语言学假设上——**分布式假设（distributional hypothesis）**：一个词的含义由它经常出现的上下文决定。因此，只要让「上下文相似的词」在向量空间里靠近，就等价于学到了语义。

这也解释了为什么词向量是**自监督**的：不需要任何人工标注，只要有大段文本，就能用「预测上下文 / 用上下文预测中心词」这一任务构造出监督信号。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/04-词向量-Word2Vec与FastText.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「分布假设」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/04-词向量-Word2Vec与FastText.md)
