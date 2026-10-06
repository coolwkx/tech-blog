---
article_id: kp-56c1298b6303163e
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-fcedd0430c9c
learning_sourceId: fcedd0430c9c
learning_order: 7
learning_objective: 理解并验证：偏差-方差分解（为什么会有过拟合）
---

# 偏差-方差分解（为什么会有过拟合）

> **学习目标**：能够解释「偏差-方差分解（为什么会有过拟合）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 基础语法、numpy 数组与 pandas DataFrame 的基本操作、一点点高中函数与坐标系概念。
>
> **所属主题**：机器学习概述与流程 · 算法细节

## 本次只学这一点

对任意测试点 $\boldsymbol{x}$，期望泛化误差可以分解为三项：

$$\mathbb{E}\big[(y - \hat{f}(\boldsymbol{x}))^2\big] = \underbrace{\text{Bias}^2[\hat{f}(\boldsymbol{x})]}_{\text{偏差}^2} + \underbrace{\text{Var}[\hat{f}(\boldsymbol{x})]}_{\text{方差}} + \underbrace{\sigma^2}_{\text{不可约噪声}}$$

**手推思路（不用严格证明，抓住直觉）**：设 $y = f^*(\boldsymbol{x}) + \varepsilon$，$\mathbb{E}[\varepsilon]=0$，$\text{Var}[\varepsilon]=\sigma^2$。记 $\bar{f}(\boldsymbol{x}) = \mathbb{E}[\hat{f}(\boldsymbol{x})]$，则

$$
\begin{aligned}
\mathbb{E}[(y-\hat f)^2]
&= \mathbb{E}\big[(f^*+\varepsilon-\hat f)^2\big]\\
&= \mathbb{E}\big[(f^*-\hat f)^2\big] + 2\underbrace{\mathbb{E}[\varepsilon]}_{=0}\mathbb{E}[f^*-\hat f] + \mathbb{E}[\varepsilon^2]\\
&= \mathbb{E}\big[(f^*-\bar f + \bar f - \hat f)^2\big] + \sigma^2\\
&= (f^*-\bar f)^2 + \mathbb{E}[(\hat f-\bar f)^2] + \sigma^2
\end{aligned}
$$

**三项的含义与调参方向**：

| 项 | 含义 | 模型复杂度 ↑ 时 | 怎么降 |
| --- | --- | --- | --- |
| $\text{Bias}^2$ | 模型假设与真实规律的偏离 | 下降 | 加特征、加复杂度 |
| $\text{Var}$ | 模型对训练集扰动的敏感度 | 上升 | 正则化、加数据、bagging |
| $\sigma^2$ | 数据本身的噪声 | 不变 | 只能改善数据质量 |

**结论**：总误差是一条 U 形曲线，最优点在"偏差与方差平衡"处——这就是为什么**过拟合与欠拟合是同一枚硬币的两面**。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「偏差-方差分解（为什么会有过拟合）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)
