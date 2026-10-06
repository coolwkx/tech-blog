---
article_id: kp-89d7d2b2b7c860c4
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-ab1dbc27d73f
learning_sourceId: ab1dbc27d73f
learning_order: 3
learning_objective: 理解并验证：三种度量与「归一化」的关系
---

# 三种度量与「归一化」的关系

> **学习目标**：能够解释「三种度量与「归一化」的关系」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇的 TF-IDF 与余弦相似度、第 04 篇的词向量、第 08 篇的 attention、第 09 篇的 BERT 与句对任务。
>
> **所属主题**：文本相似度与语义匹配 · 核心概念

## 本次只学这一点

| 度量 | 公式 | 关注 | 对向量的要求 |
|------|------|------|-------------|
| 点积（Dot） | $\mathbf{a}\cdot\mathbf{b}=\sum_i a_i b_i$ | 方向 + 长度 | 无 |
| 余弦相似度（Cosine） | $\cos=\dfrac{\mathbf{a}\cdot\mathbf{b}}{\lVert\mathbf a\rVert\lVert\mathbf b\rVert}$ | 只关注方向 | 无（自动除模长） |
| 欧氏距离（L2） | $\lVert\mathbf a-\mathbf b\rVert_2$ | 绝对位置 | 需同量纲 |

三者之间的关键关系（工程上非常重要）：

$$
\lVert \mathbf a - \mathbf b\rVert^2 = \lVert\mathbf a\rVert^2 + \lVert\mathbf b\rVert^2 - 2\,\mathbf a\cdot\mathbf b
$$

当 $\lVert\mathbf a\rVert=\lVert\mathbf b\rVert=1$（向量已 L2 归一化）时：

$$
\lVert\mathbf a-\mathbf b\rVert^2 = 2 - 2\cos(\mathbf a,\mathbf b),\qquad \mathbf a\cdot\mathbf b=\cos(\mathbf a,\mathbf b)
$$

结论：**归一化之后，余弦相似度、内积、欧氏距离是等价的排序**。这就是为什么向量检索库（Faiss、Milvus、Elasticsearch 的 dense vector）普遍要求先把向量归一化，然后用内积（IP）做度量——这样做能把余弦计算简化为一次内积，速度更快且可直接用矩阵乘法。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/10-文本相似度与语义匹配.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「三种度量与「归一化」的关系」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/10-文本相似度与语义匹配.md)
