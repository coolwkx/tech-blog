---
article_id: kp-838bab98e6257df6
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-88f79f4f1547
learning_sourceId: 88f79f4f1547
learning_order: 4
learning_objective: 理解并验证：KMeans 的优化目标
---

# KMeans 的优化目标

> **学习目标**：能够解释「KMeans 的优化目标」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：欧氏距离与标准化（见 [02-KNN算法](../../../../../03-ml/02-经典算法/02-KNN算法.md)）、`make_blobs` 造数据、pandas 与 matplotlib 基础。
>
> **所属主题**：KMeans 聚类 · 算法细节

## 本次只学这一点

给定样本集 $\{x_1,\dots,x_n\}$ 与簇数 $K$，KMeans 要最小化**簇内平方误差和（SSE / inertia）**：

$$\boxed{\ J = \sum_{k=1}^{K}\sum_{x\in C_k}\|x - \mu_k\|_2^2\ },\qquad \mu_k = \frac{1}{|C_k|}\sum_{x\in C_k}x$$

这是一个**NP-hard** 的组合优化问题（要枚举所有划分），所以 KMeans 用**交替迭代**求局部最优。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/04-集成与无监督/07-KMeans聚类.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「KMeans 的优化目标」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/04-集成与无监督/07-KMeans聚类.md)
