---
article_id: kp-7a8aea445b21dfa0
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-11324cf8be3a
learning_sourceId: 11324cf8be3a
learning_order: 8
learning_objective: 理解并验证：多元线性回归与正规方程
---

# 多元线性回归与正规方程

> **学习目标**：能够解释「多元线性回归与正规方程」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：导数/偏导数与矩阵乘法（本文第 2.1 节会复习）、numpy 数组运算、`train_test_split` 与 `StandardScaler` 的用法（见 [01-机器学习概述与流程](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)）。
>
> **所属主题**：线性回归 · 算法细节

## 本次只学这一点

**Step 1：把样本写成矩阵。** 给 $\boldsymbol{x}_i$ 前拼接一列常数 1（吸收截距 $b$），设

$$\boldsymbol{X} =
\begin{bmatrix}
1 & x_{11} & \cdots & x_{1d}\\
1 & x_{21} & \cdots & x_{2d}\\
\vdots & \vdots & & \vdots\\
1 & x_{n1} & \cdots & x_{nd}
\end{bmatrix}_{n\times(d+1)},
\qquad
\boldsymbol{y} = \begin{bmatrix}y_1\\ \vdots\\ y_n\end{bmatrix},
\qquad
\boldsymbol{w} = \begin{bmatrix}b\\ w_1\\ \vdots\\ w_d\end{bmatrix}
$$

**Step 2：损失函数的矩阵形式。**

$$J(\boldsymbol{w}) = \frac{1}{2}(\boldsymbol{y}-\boldsymbol{X}\boldsymbol{w})^\top(\boldsymbol{y}-\boldsymbol{X}\boldsymbol{w})$$

展开：

$$
\begin{aligned}
J(\boldsymbol{w}) &= \frac12\big(\boldsymbol{y}^\top\boldsymbol{y} - \boldsymbol{y}^\top\boldsymbol{X}\boldsymbol{w} - \boldsymbol{w}^\top\boldsymbol{X}^\top\boldsymbol{y} + \boldsymbol{w}^\top\boldsymbol{X}^\top\boldsymbol{X}\boldsymbol{w}\big)\\
&= \frac12\boldsymbol{y}^\top\boldsymbol{y} - \boldsymbol{w}^\top\boldsymbol{X}^\top\boldsymbol{y} + \frac12\boldsymbol{w}^\top\boldsymbol{X}^\top\boldsymbol{X}\boldsymbol{w}
\end{aligned}
$$

（用到 $\boldsymbol{y}^\top\boldsymbol{X}\boldsymbol{w} = \boldsymbol{w}^\top\boldsymbol{X}^\top\boldsymbol{y}$，二者都是标量。）

**Step 3：对 $\boldsymbol{w}$ 求梯度置零。** 用两条矩阵求导结论：$\nabla_{\boldsymbol w}(\boldsymbol{w}^\top\boldsymbol{a})=\boldsymbol{a}$，$\nabla_{\boldsymbol w}(\boldsymbol{w}^\top\boldsymbol{A}\boldsymbol{w})=2\boldsymbol{A}\boldsymbol{w}$（$\boldsymbol A$ 对称）。于是

$$\frac{\partial J}{\partial \boldsymbol{w}} = -\boldsymbol{X}^\top\boldsymbol{y} + \boldsymbol{X}^\top\boldsymbol{X}\boldsymbol{w} = 0$$

**Step 4：得到正规方程（Normal Equation）。**

$$\boxed{\boldsymbol{X}^\top\boldsymbol{X}\,\boldsymbol{w} = \boldsymbol{X}^\top\boldsymbol{y}}
\quad\Longrightarrow\quad
\boxed{\boldsymbol{w} = (\boldsymbol{X}^\top\boldsymbol{X})^{-1}\boldsymbol{X}^\top\boldsymbol{y}}$$

**每一项的解释**：

| 符号 | 含义 |
| --- | --- |
| $\boldsymbol{X}$ | $n\times(d+1)$ 的设计矩阵（特征矩阵 + 一列 1） |
| $\boldsymbol{X}^\top\boldsymbol{X}$ | $(d+1)\times(d+1)$ 的方阵，反映特征间的二阶统计量 |
| $\boldsymbol{X}^\top\boldsymbol{y}$ | $(d+1)\times1$ 向量，反映特征与标签的相关性 |
| $(\boldsymbol{X}^\top\boldsymbol{X})^{-1}$ | 方阵的逆；**存在的条件是 $\boldsymbol X$ 列满秩（特征不共线）** |

> **重要纠正**：$\boldsymbol{X}^\top\boldsymbol{X}$ **不一定可逆**。当存在完全共线的特征（如"身高(cm)"与"身高(m)"）或 $d>n$ 时它是奇异的。此时 scikit-learn 会用伪逆（`np.linalg.pinv`）得到**最小范数解**，或者应该改用岭回归。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/03-线性回归.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「多元线性回归与正规方程」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/03-线性回归.md)
