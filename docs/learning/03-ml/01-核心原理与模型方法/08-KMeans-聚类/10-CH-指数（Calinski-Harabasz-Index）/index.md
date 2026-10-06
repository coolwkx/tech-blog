---
article_id: kp-34d2448292c22668
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-88f79f4f1547
learning_sourceId: 88f79f4f1547
learning_order: 9
learning_objective: 理解并验证：CH 指数（Calinski-Harabasz Index）
---

# CH 指数（Calinski-Harabasz Index）

> **学习目标**：能够解释「CH 指数（Calinski-Harabasz Index）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：欧氏距离与标准化（见 [02-KNN算法](../../../../../03-ml/02-经典算法/02-KNN算法.md)）、`make_blobs` 造数据、pandas 与 matplotlib 基础。
>
> **所属主题**：KMeans 聚类 · 算法细节

## 本次只学这一点

$$\text{CH}(k) = \frac{\text{SSB}/(k-1)}{\text{SSW}/(n-k)}$$

| 符号 | 含义 | 方向 |
| --- | --- | --- |
| **SSW** | 簇内距离平方和（相当于 SSE），即每个样本点到其质心的距离的累加 | **越小越好** |
| **SSB** | 簇间距离平方和：各质心与"全体质心中心点"之间距离的加权和（权重为该簇样本数 $n_j$） | **越大越好** |
| $n$ | 样本数量 | —— |
| $k$ | 质心（类别）个数 | —— |

**CH 要达到的目的**：**用尽量少的类别聚类尽量多的样本，同时获得较好的聚类效果。** $k$ 增大时，分子 $\text{SSB}/(k-1)$ 会因为 $k$ 太大而下降，从而**自动惩罚过多的类别数**。

**方向：分数越高聚类效果越好。** 实验同样在 $k=4$ 时取到最大值。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/04-集成与无监督/07-KMeans聚类.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「CH 指数（Calinski-Harabasz Index）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/04-集成与无监督/07-KMeans聚类.md)
