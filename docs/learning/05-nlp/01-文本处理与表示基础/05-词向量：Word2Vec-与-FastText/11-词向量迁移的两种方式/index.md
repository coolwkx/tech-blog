---
article_id: kp-e55229681e7e1b04
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-5865c55f8aa7
learning_sourceId: 5865c55f8aa7
learning_order: 10
learning_objective: 理解并验证：词向量迁移的两种方式
---

# 词向量迁移的两种方式

> **学习目标**：能够解释「词向量迁移的两种方式」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇的 one-hot 与词袋、softmax 与交叉熵、PyTorch `nn.Embedding` 的基本用法。
>
> **所属主题**：词向量：Word2Vec 与 FastText · 方法细节

## 本次只学这一点

训练好的词向量可以作为下游模型的初始化：

| 方式 | 做法 | 适用 |
|------|------|------|
| 冻结（freeze） | 加载预训练向量到 `nn.Embedding`，`requires_grad=False`，只训练后续层 | 下游数据很少（防止 embedding 被小数据带偏） |
| 微调（fine-tune） | 加载后继续参与训练，可全部或部分解冻 | 下游数据充足、领域与预训练语料有差异 |

工业上的折中做法：**分层学习率**——embedding 层用很小的学习率（如 1e-5），上层用正常学习率。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/04-词向量-Word2Vec与FastText.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「词向量迁移的两种方式」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/04-词向量-Word2Vec与FastText.md)
