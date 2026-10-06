---
article_id: kp-bea1ed7dfb88d4c2
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-8321d1237f76
learning_sourceId: 8321d1237f76
learning_order: 5
learning_objective: 理解并验证：距离度量（四种距离的统一视角）
---

# 距离度量（四种距离的统一视角）

> **学习目标**：能够解释「距离度量（四种距离的统一视角）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：向量与距离概念、numpy 数组索引与广播、pandas 基础、`train_test_split` 的使用（见 [01-机器学习概述与流程](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)）。
>
> **所属主题**：KNN 算法 · 算法细节

## 本次只学这一点

设两个 $d$ 维样本 $\boldsymbol{x}=(x_1,\dots,x_d)$、$\boldsymbol{y}=(y_1,\dots,y_d)$。

**（1）欧氏距离（Euclidean Distance）**——最常用，$L_2$ 范数：

$$d(\boldsymbol{x},\boldsymbol{y}) = \sqrt{\sum_{i=1}^{d}(x_i - y_i)^2} = \|\boldsymbol{x}-\boldsymbol{y}\|_2$$

**（2）曼哈顿距离（Manhattan / City Block Distance）**——$L_1$ 范数，只能横平竖直走：

$$d(\boldsymbol{x},\boldsymbol{y}) = \sum_{i=1}^{d}|x_i - y_i| = \|\boldsymbol{x}-\boldsymbol{y}\|_1$$

**（3）切比雪夫距离（Chebyshev Distance）**——$L_\infty$ 范数，取最大的那一维差值：

$$d(\boldsymbol{x},\boldsymbol{y}) = \max_{i} |x_i - y_i| = \|\boldsymbol{x}-\boldsymbol{y}\|_\infty$$

**（4）闵可夫斯基距离（Minkowski Distance）**——以上三者的统一形式：

$$d(\boldsymbol{x},\boldsymbol{y}) = \left(\sum_{i=1}^{d}|x_i - y_i|^{p}\right)^{1/p}$$

| $p$ 的取值 | 得到的距离 |
| --- | --- |
| $p = 1$ | 曼哈顿距离 |
| $p = 2$ | 欧氏距离 |
| $p \to \infty$ | 切比雪夫距离 |

> **注意**：闵氏距离不是一种新距离，而是**一类距离的概括表达式**，$p$ 就是它的"旋钮"。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/02-KNN算法.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「距离度量（四种距离的统一视角）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/02-KNN算法.md)
