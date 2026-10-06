---
article_id: kp-48c00554323b2140
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-0d24db15ec32
learning_sourceId: 0d24db15ec32
learning_order: 4
learning_objective: 理解并验证：归一化（Min-Max Normalization）
---

# 归一化（Min-Max Normalization）

> **学习目标**：能够解释「归一化（Min-Max Normalization）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：pandas 的 `groupby`/`get_dummies`/缺失值处理、numpy 的数组拼接（`hstack`）、距离与量纲的影响（见 [02-KNN算法](../../../../../03-ml/02-经典算法/02-KNN算法.md)）。
>
> **所属主题**：特征工程 · 算法细节

## 本次只学这一点

$$x' = \frac{x - \min(x)}{\max(x) - \min(x)}$$

**API**：`sklearn.preprocessing.MinMaxScaler(feature_range=(0, 1))`

| 方法/属性 | 含义 |
| --- | --- |
| `fit_transform(X_train)` | 学统计量并转换（训练集） |
| `transform(X_test)` | 用训练集的 min/max 转换（测试集） |
| `data_min_` / `data_max_` | 学到的每列最小值 / 最大值 |
| `inverse_transform(X)` | 反变换回原始量纲 |

**特点**：
- 让所有特征落在同一区间，**对量纲差异极其敏感的问题（如 KNN、神经网络）非常有效**；
- **受最大值与最小值的影响，容易受异常数据影响，鲁棒性较差**；
- 适合**传统精确小数据**场景；有异常点时结果会被严重压缩。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「归一化（Min-Max Normalization）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)
