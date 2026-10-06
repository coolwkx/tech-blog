---
article_id: kp-b3eb4d607adaf012
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-11324cf8be3a
learning_sourceId: 11324cf8be3a
learning_order: 6
learning_objective: 理解并验证：损失函数：从"误差和最小"到 MSE
---

# 损失函数：从"误差和最小"到 MSE

> **学习目标**：能够解释「损失函数：从"误差和最小"到 MSE」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：导数/偏导数与矩阵乘法（本文第 2.1 节会复习）、numpy 数组运算、`train_test_split` 与 `StandardScaler` 的用法（见 [01-机器学习概述与流程](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)）。
>
> **所属主题**：线性回归 · 算法细节

## 本次只学这一点

误差定义为 $\text{error}_i = y_i - \hat{y}_i$。**损失函数**（loss / cost / objective function）把所有样本的误差汇成一个可优化的标量。

**为什么不用"误差直接求和"？** 因为正负误差会互相抵消（$-100$ 与 $+100$ 之和为 0，却拟合得很差），所以需要平方或绝对值。

**MSE（均方误差，最小二乘的均值形式）**：

$$J(\boldsymbol{w},b) = \frac{1}{2n}\sum_{i=1}^{n}\big(y_i - (\boldsymbol{w}^\top\boldsymbol{x}_i+b)\big)^2$$

> 加 $\tfrac12$ 只是为了求导后系数变成 1，不影响最优点位置。

**MAE（平均绝对误差）**：

$$J_{\text{MAE}}(\boldsymbol{w},b)=\frac{1}{n}\sum_{i=1}^{n}\lvert y_i-\hat{y}_i\rvert$$

**MSE 与 MAE 的取舍**：MSE 处处可导、是凸函数、能直接解出解析解；MAE 在 0 点不可导，但更抗异常值（等价于中位数回归）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/03-线性回归.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「损失函数：从"误差和最小"到 MSE」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/03-线性回归.md)
