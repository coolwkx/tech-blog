---
article_id: kp-e509552f5366e3f6
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-0d24db15ec32
learning_sourceId: 0d24db15ec32
learning_order: 5
learning_objective: 理解并验证：标准化（Z-Score Standardization）
---

# 标准化（Z-Score Standardization）

> **学习目标**：能够解释「标准化（Z-Score Standardization）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：pandas 的 `groupby`/`get_dummies`/缺失值处理、numpy 的数组拼接（`hstack`）、距离与量纲的影响（见 [02-KNN算法](../../../../../03-ml/02-经典算法/02-KNN算法.md)）。
>
> **所属主题**：特征工程 · 算法细节

## 本次只学这一点

$$x' = \frac{x - \mu}{\sigma},\qquad \mu = \frac{1}{N}\sum_i x_i,\qquad \sigma=\sqrt{\frac{1}{N}\sum_i(x_i-\mu)^2}$$

**API**：`sklearn.preprocessing.StandardScaler`

| 属性 | 含义 |
| --- | --- |
| `mean_` | 每列均值 $\mu$ |
| `var_` | 每列方差 $\sigma^2$ |
| `scale_` | 每列标准差 $\sigma$（含 `ddof=0` 的修正） |

**特点**：
- 变换后均值 0、标准差 1，**不保证落在 $[0,1]$**；
- "如果出现异常点，由于具有一定数据量，**少量的异常点对于平均值的影响并不大**"，因此比归一化稳健；
- **工程开发中一般倾向使用标准化**。

**为什么 $\mu$ 与 $\sigma$ 用"有偏"估计？** sklearn 使用 $\sigma=\sqrt{\frac1N\sum(x_i-\mu)^2}$（`ddof=0`）而非样本标准差 $\sqrt{\frac1{N-1}\sum(\cdot)}$。数据量大时二者差异可忽略。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「标准化（Z-Score Standardization）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)
