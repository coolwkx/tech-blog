---
article_id: kp-fa5351dbaee10e42
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-88f79f4f1547
learning_sourceId: 88f79f4f1547
learning_order: 8
learning_objective: 理解并验证：轮廓系数 SC（Silhouette Coefficient）
---

# 轮廓系数 SC（Silhouette Coefficient）

> **学习目标**：能够解释「轮廓系数 SC（Silhouette Coefficient）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：欧氏距离与标准化（见 [02-KNN算法](../../../../../03-ml/02-经典算法/02-KNN算法.md)）、`make_blobs` 造数据、pandas 与 matplotlib 基础。
>
> **所属主题**：KMeans 聚类 · 算法细节

## 本次只学这一点

**结合簇内的内聚程度（Cohesion）与簇间的分离程度（Separation）**。

**单样本 $i$ 的计算过程**：
1. $a_i$：样本 $i$ 到**同簇内其他样本**的平均距离。$a_i$ 越小，簇内相似度越大；
2. $b_i$：样本 $i$ 到**最近的那个其他簇 $j$** 内所有样本的平均距离。$b_i$ 越大，说明样本越不属于其他簇；
3. 该样本的轮廓系数：

$$s_i = \frac{b_i - a_i}{\max(a_i,\ b_i)}$$

4. 全体样本的轮廓系数取平均：$\text{SC} = \dfrac1n\sum_i s_i$。

| $s_i$ 取值 | 含义 |
| --- | --- |
| 接近 **1** | 簇内很紧、离其他簇很远，**聚类效果很好** |
| 接近 **0** | 处在两个簇的边界上 |
| 接近 **−1** | 可能被分错了簇 |

**范围 $[-1, 1]$，值越大聚类效果越好。** 注意 **SC 要求簇数 ≥ 2**（只有 1 个簇时无法计算簇间距离）。

**实验**：把 $k$ 从 2 遍历到 99 计算 SC，观察到 **$k=4$ 时取到最大值**，与肘部法结论一致。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/04-集成与无监督/07-KMeans聚类.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「轮廓系数 SC（Silhouette Coefficient）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/04-集成与无监督/07-KMeans聚类.md)
