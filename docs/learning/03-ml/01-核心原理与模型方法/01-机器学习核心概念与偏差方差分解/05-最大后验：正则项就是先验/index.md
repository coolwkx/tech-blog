---
article_id: kp-0544b4c463ae7b96
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-266564777403
learning_sourceId: '266564777403'
learning_order: 4
learning_objective: 理解并验证：最大后验：正则项就是先验
---

# 最大后验：正则项就是先验

> **学习目标**：能够解释「最大后验：正则项就是先验」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：条件期望 $E[Y\mid X]$、方差、极大似然估计、矩阵最小二乘（正规方程）、训练/验证集切分与交叉验证。
>
> **所属主题**：机器学习核心概念与偏差方差分解 · 核心思想

## 本次只学这一点

取负对数后，最大化后验（MAP）等价于最小化

$$-\log p(\theta\mid D)=\frac{1}{2\sigma^2}\sum_i\big(y_i-f_\theta(x_i)\big)^2\underbrace{-\log p(\theta)}_{\text{正则项}}+\text{const}$$

- 先验为高斯 $\theta\sim\mathcal N(0,\tau^2 I)$ 时 $-\log p(\theta)=\frac{1}{2\tau^2}\|\theta\|_2^2$，得到 **L2 / Ridge**，且 $\lambda=\sigma^2/\tau^2$：噪声越大或先验越强，正则越重；
- 先验为拉普拉斯 $p(\theta_j)\propto e^{-|\theta_j|/b}$ 时 $-\log p(\theta)=\frac{1}{b}\|\theta\|_1$，得到 **L1 / Lasso**。拉普拉斯先验在 0 处有尖峰，后验众数容易正好落在坐标轴上，这就是稀疏性的来源。

MLE 是 MAP 在均匀先验下的特例；MAP 是**有偏估计**——它主动引入偏差换取方差下降，这正是第 4 节要量化的交易。

| 数据假设（似然） | 等价损失 | 参数先验 | 等价正则项 | sklearn 对应 |
| --- | --- | --- | --- | --- |
| $y=f_\theta(x)+\mathcal N(0,\sigma^2)$ | MSE | 无（MLE） | 无 | `LinearRegression` |
| 高斯噪声 | MSE | 高斯 $\mathcal N(0,\tau^2)$ | $\lambda\|\theta\|_2^2$ | `Ridge` |
| 拉普拉斯噪声 | MAE | 无 | 无 | `QuantileRegressor(quantile=0.5)` |
| 高斯噪声 | MSE | 拉普拉斯 | $\lambda\|\theta\|_1$ | `Lasso` |
| 伯努利 $y\in\{0,1\}$ | 二元交叉熵 | 高斯 / 拉普拉斯 | L2 / L1 | `LogisticRegression(penalty=...)` |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/01-基础与特征工程/01-机器学习核心概念与偏差方差分解.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「最大后验：正则项就是先验」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/01-基础与特征工程/01-机器学习核心概念与偏差方差分解.md)
