---
article_id: kp-433afab6f0f89200
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-8321d1237f76
learning_sourceId: 8321d1237f76
learning_order: 7
learning_objective: 理解并验证：标准化：为什么 KNN 一定要做
---

# 标准化：为什么 KNN 一定要做

> **学习目标**：能够解释「标准化：为什么 KNN 一定要做」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：向量与距离概念、numpy 数组索引与广播、pandas 基础、`train_test_split` 的使用（见 [01-机器学习概述与流程](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)）。
>
> **所属主题**：KNN 算法 · 算法细节

## 本次只学这一点

假设两个特征：`每月工资`（6000~13000）与 `房产面积`（55~90）。计算欧氏距离时：

$$d^2 = (6000-8000)^2 + (55-65)^2 = 4{,}000{,}000 + 100$$

第二项被完全淹没。**距离由量纲大的特征单独支配**，量纲小的特征等于没参与。

**归一化（Min-Max Normalization）**：

$$x' = \frac{x - \min(x)}{\max(x) - \min(x)}$$

API：`sklearn.preprocessing.MinMaxScaler(feature_range=(0, 1))`

**标准化（Z-Score Standardization）**：

$$x' = \frac{x - \mu}{\sigma},\qquad \mu = \frac{1}{N}\sum_i x_i,\quad \sigma=\sqrt{\frac{1}{N}\sum_i (x_i-\mu)^2}$$

API：`sklearn.preprocessing.StandardScaler()`，属性 `mean_`、`var_`、`scale_`。

| 对比项 | 归一化 MinMaxScaler | 标准化 StandardScaler |
| --- | --- | --- |
| 输出范围 | $[0,1]$（可指定） | 无固定范围，大致 $[-3,3]$ |
| 是否受异常值影响 | **大** | 小 |
| 适用场景 | 传统精确小数据、图像像素（除 255） | 通用首选；KNN、SVM、逻辑回归、PCA |

> 结论：**"一般倾向使用标准化"**。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/02-KNN算法.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「标准化：为什么 KNN 一定要做」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/02-KNN算法.md)
