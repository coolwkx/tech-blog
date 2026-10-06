---
article_id: kp-46c2c4bae527b9d4
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-fcedd0430c9c
learning_sourceId: fcedd0430c9c
learning_order: 6
learning_objective: 理解并验证：监督学习的数学形式
---

# 监督学习的数学形式

> **学习目标**：能够解释「监督学习的数学形式」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 基础语法、numpy 数组与 pandas DataFrame 的基本操作、一点点高中函数与坐标系概念。
>
> **所属主题**：机器学习概述与流程 · 算法细节

## 本次只学这一点

给定训练集 $D = \{(\boldsymbol{x}_i, y_i)\}_{i=1}^{N}$，其中 $\boldsymbol{x}_i \in \mathbb{R}^{d}$ 是特征向量，$y_i$ 是标签：

- **分类任务**：$y_i \in \{c_1, c_2, \dots, c_K\}$，目标是学一个映射 $f: \mathbb{R}^d \to \{c_1,\dots,c_K\}$；
- **回归任务**：$y_i \in \mathbb{R}$，目标是学 $f: \mathbb{R}^d \to \mathbb{R}$。

学习的过程就是在一个**假设空间** $\mathcal{H}$ 中找 $f$，使得某个损失函数最小：

$$\hat{f} = \arg\min_{f \in \mathcal{H}} \frac{1}{N}\sum_{i=1}^{N} L\big(y_i,\ f(\boldsymbol{x}_i)\big)$$

**无监督学习**没有 $y$，只能优化"簇内紧、簇间散"这类**内部准则**（如 KMeans 的 SSE）：

$$\hat{C} = \arg\min_{C} \sum_{k=1}^{K}\sum_{\boldsymbol{x}\in C_k} \|\boldsymbol{x} - \boldsymbol{\mu}_k\|_2^2,\qquad \boldsymbol{\mu}_k = \frac{1}{|C_k|}\sum_{\boldsymbol{x}\in C_k}\boldsymbol{x}$$

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「监督学习的数学形式」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)
