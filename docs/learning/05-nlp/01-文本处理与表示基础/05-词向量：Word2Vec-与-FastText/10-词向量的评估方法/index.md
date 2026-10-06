---
article_id: kp-d27ade694f4c159b
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-5865c55f8aa7
learning_sourceId: 5865c55f8aa7
learning_order: 9
learning_objective: 理解并验证：词向量的评估方法
---

# 词向量的评估方法

> **学习目标**：能够解释「词向量的评估方法」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇的 one-hot 与词袋、softmax 与交叉熵、PyTorch `nn.Embedding` 的基本用法。
>
> **所属主题**：词向量：Word2Vec 与 FastText · 方法细节

## 本次只学这一点

评估分两类，缺一不可：

| 类型 | 做法 | 优点 | 缺点 |
|------|------|------|------|
| 内在评估（intrinsic） | 相似度任务（WordSim-353、Spearman 相关）；类比任务（king − man + woman = ?） | 快、无需下游任务、直接反映语义质量 | 与下游性能不完全一致 |
| 外在评估（extrinsic） | 把词向量接入具体任务（分类、NER）看指标 | 直接反映实用价值 | 慢，且受下游模型影响 |

词向量类比的标准形式：$v_a - v_b + v_c$ 的最近邻（排除 $a,b,c$ 本身）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/04-词向量-Word2Vec与FastText.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「词向量的评估方法」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/04-词向量-Word2Vec与FastText.md)
