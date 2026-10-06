---
article_id: kp-12090eaa0c0ef662
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-d8ba07ef6cec
learning_sourceId: d8ba07ef6cec
learning_order: 9
learning_objective: 理解并验证：从「词袋 + 树」到「Embedding + 网络」
---

# 从「词袋 + 树」到「Embedding + 网络」

> **学习目标**：能够解释「从「词袋 + 树」到「Embedding + 网络」」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 02 篇分词、第 03 篇 TF-IDF 与稀疏矩阵、第 04 篇词向量与 FastText、sklearn 的基本用法。
>
> **所属主题**：文本分类实战 · 方法细节

## 本次只学这一点

`ag_news` 案例的浅层网络是理解后续所有模型的起点：

```python
self.embedding = nn.Embedding(vocab_size, embed_dim, sparse=True)
self.fc = nn.Linear(embed_dim, num_class)
```

配合 `F.avg_pool2d` / 对时间维求平均得到句向量，再接线性层。三点值得注意：

- `sparse=True`：对 embedding 求梯度时只更新被激活的行。词表大时能显著省内存与计算，**前提是优化器支持稀疏梯度**（`SparseAdam` / `Adagrad`，普通 `Adam` 不支持）。
- 这里的 embedding 是**随机初始化、随任务训练**的（第 3 代表示），与第 1 档的 TF-IDF（第 2 代）是本质不同的表示。
- 这个结构与 FastText 分类头几乎等价：**词向量平均 + 线性层**。差别在于 FastText 用子词合成向量，且训练目标/正则更成熟。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/05-文本分类实战.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「从「词袋 + 树」到「Embedding + 网络」」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/05-文本分类实战.md)
