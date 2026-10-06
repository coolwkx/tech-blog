---
article_id: kp-5e0ce9ddaa8cff68
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-11324cf8be3a
learning_sourceId: 11324cf8be3a
learning_order: 7
learning_objective: 理解并验证：一元线性回归的解析解（手推）
---

# 一元线性回归的解析解（手推）

> **学习目标**：能够解释「一元线性回归的解析解（手推）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：导数/偏导数与矩阵乘法（本文第 2.1 节会复习）、numpy 数组运算、`train_test_split` 与 `StandardScaler` 的用法（见 [01-机器学习概述与流程](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)）。
>
> **所属主题**：线性回归 · 算法细节

## 本次只学这一点

**Step 1：写出一元损失函数并展开。** 取 $J(k,b)=\sum_i (y_i - kx_i - b)^2$（常数系数不影响极值点）：

$$
\begin{aligned}
J(k,b) &= \sum_i \big(y_i - kx_i - b\big)^2\\
&= \sum_i y_i^2 - 2k\sum_i x_i y_i - 2b\sum_i y_i + k^2\sum_i x_i^2 + 2kb\sum_i x_i + nb^2
\end{aligned}
$$

**Step 2：分别对 $k$、$b$ 求偏导并置零。**

$$
\frac{\partial J}{\partial k} = 2k\sum_i x_i^2 + 2b\sum_i x_i - 2\sum_i x_i y_i = 0
\quad\Longrightarrow\quad
k\sum_i x_i^2 + b\sum_i x_i = \sum_i x_i y_i
\tag{1}
$$

$$
\frac{\partial J}{\partial b} = 2k\sum_i x_i + 2nb - 2\sum_i y_i = 0
\quad\Longrightarrow\quad
k\sum_i x_i + nb = \sum_i y_i
\tag{2}
$$

> 推导细节：对 $k$ 求偏导时，$k$ 出现在 $k^2\sum x_i^2$（导数 $2k\sum x_i^2$）、$2kb\sum x_i$（导数 $2b\sum x_i$）、$-2k\sum x_iy_i$（导数 $-2\sum x_iy_i$）三项中；对 $b$ 求偏导时，$b$ 出现在 $2kb\sum x_i$（导数 $2k\sum x_i$）、$nb^2$（导数 $2nb$）、$-2b\sum y_i$（导数 $-2\sum y_i$）三项中。其余项与待求参数无关，导数为 0。

**Step 3：代入数据求解。** 数据为 $x=\{160,166,172,174,180\}$，$y=\{56.3,60.6,65.1,68.5,75\}$，先算五个统计量：

| 统计量 | 值 |
| --- | --- |
| $\sum x$ | $852$ |
| $\sum y$ | $325.5$ |
| $\sum x^2$ | $145416$ |
| $\sum xy$ | $55683.8$ |
| $n$ | $5$ |

代入 (1)(2) 得到给出的方程组：

$$
\begin{cases}
145416\,k + 852\,b - 55683.8 = 0\\
852\,k + 5\,b - 325.5 = 0
\end{cases}
$$

解之（与 `np.linalg.lstsq` 结果一致）：

$$k = 0.9294,\qquad b = -93.2735$$

**Step 4：预测。**

$$y(176) = 0.9294\times 176 - 93.2735 = 70.30$$

> **另一个更简单的演示**：把 $b$ 固定为 $-100$（相当于强行让直线经过 $(0,-100)$），损失函数退化为一元二次函数
> $$L(k) = 145416k^2 - 281671.6k + 136496.32$$
> 求导置零：$k^\star = \dfrac{281671.6}{2\times 145416} = 0.9685$，预测 $y = 0.9685\times176 - 100 = 70.46$。
> 两次预测差 0.16，说明**截距的取值对结果影响有限**，但自由求解 $b$ 才是正确的做法。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/03-线性回归.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「一元线性回归的解析解（手推）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/03-线性回归.md)
