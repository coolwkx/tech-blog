---
article_id: kp-49e0efc6acdf71f9
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-266564777403
learning_sourceId: '266564777403'
learning_order: 2
learning_objective: 理解并验证：极大似然估计：为什么回归用 MSE
---

# 极大似然估计：为什么回归用 MSE

> **学习目标**：能够解释「极大似然估计：为什么回归用 MSE」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：条件期望 $E[Y\mid X]$、方差、极大似然估计、矩阵最小二乘（正规方程）、训练/验证集切分与交叉验证。
>
> **所属主题**：机器学习核心概念与偏差方差分解 · 核心思想

## 本次只学这一点

设 $y=f_\theta(x)+\varepsilon$，$\varepsilon\sim\mathcal N(0,\sigma^2)$ 独立于 $x$。负对数似然为

$$-\log L(\theta)=\underbrace{\frac{n}{2}\log(2\pi\sigma^2)}_{\text{与 }\theta\text{ 无关}}+\frac{1}{2\sigma^2}\sum_{i=1}^{n}\big(y_i-f_\theta(x_i)\big)^2
\quad\Longrightarrow\quad \arg\max_\theta L(\theta)=\arg\min_\theta \text{MSE}$$

因为 $\frac{1}{2\sigma^2}$ 是正数常数，$\sigma^2$ 只影响似然的尺度而不影响最优参数。**MSE 不是随手选的，它是"高斯噪声假设下的极大似然估计"**。把噪声假设换成拉普拉斯分布 $p(\varepsilon)\propto e^{-|\varepsilon|/b}$，同样的推导得到 $\sum_i|y_i-f_\theta(x_i)|$，即 MAE（对离群点更稳健）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/01-基础与特征工程/01-机器学习核心概念与偏差方差分解.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「极大似然估计：为什么回归用 MSE」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/01-基础与特征工程/01-机器学习核心概念与偏差方差分解.md)
