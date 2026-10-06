---
article_id: kp-f5b7944039a667da
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-f80e625a8f58
learning_sourceId: f80e625a8f58
learning_order: 7
learning_objective: 理解并验证：从似然到交叉熵损失（完整手推）
---

# 从似然到交叉熵损失（完整手推）

> **学习目标**：能够解释「从似然到交叉熵损失（完整手推）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性回归与梯度下降（见 [03-线性回归](../../../../../03-ml/02-经典算法/03-线性回归.md)）、概率的基本概念（条件概率、独立事件）、对数运算、混淆矩阵的基本直觉。
>
> **所属主题**：逻辑回归 · 算法细节

## 本次只学这一点

**Step 1：单个样本的"分类正确概率"。** 设某样本被分为 1 类的概率为 $p$，则分为 0 类的概率为 $1-p$。真实标签为 $y\in\{0,1\}$，则**分类正确的概率**可以写成一个统一的式子：

$$P(y\mid\boldsymbol{x}) = p^{\,y}\,(1-p)^{\,1-y}$$

验证：$y=1$ 时得 $p$；$y=0$ 时得 $1-p$。✓

**Step 2：$n$ 个样本的联合概率（似然函数）。** 假设样本独立：

$$L(\boldsymbol{w}) = \prod_{i=1}^{n} p_i^{\,y_i}(1-p_i)^{\,1-y_i},\qquad p_i = \sigma(\boldsymbol{w}^\top\boldsymbol{x}_i)$$

**Step 3：取对数（对数似然）。**

$$\ln L(\boldsymbol{w}) = \sum_{i=1}^{n}\Big[y_i\ln p_i + (1-y_i)\ln(1-p_i)\Big]$$

**Step 4：极大化 → 极小化。** 习惯上取负号，得到**对数似然损失（交叉熵损失，log loss）**：

$$\boxed{J(\boldsymbol{w}) = -\sum_{i=1}^{n}\Big[y_i\ln p_i + (1-y_i)\ln(1-p_i)\Big]},\qquad p_i=\sigma(\boldsymbol{w}^\top\boldsymbol{x}_i)$$

**Step 5：手工验证损失函数的行为。** 假设阈值为 0.6，三个样本的预测与真实如下：

| 样本 | 真实 $y$ | 预测 $p$ | 该样本损失 $-[y\ln p+(1-y)\ln(1-p)]$ |
| --- | --- | --- | --- |
| 1 | 1 | 0.4 | $-\ln 0.4 = 0.916$ |
| 2 | 0 | 0.6 | $-\ln 0.4 = 0.916$ |
| 3 | 1 | 0.41 | $-\ln 0.41 = 0.892$ |

原式的写法正是逐样本展开：`1*log0.4 + (1-1)*log(1-0.4) + 0*log0.6 + (1-0)*log(1-0.6) + ...`

**损失函数的直觉**：

> 每个样本的预测值有 A、B 两个类别，**真实类别对应的那个位置，概率值越大越好**。
> - 当 $y=1$ 时，损失是 $-\ln p$：$p\to 1$ 时损失 → 0；$p\to 0$ 时损失 → $+\infty$。
> - 当 $y=0$ 时，损失是 $-\ln(1-p)$：$p\to 0$ 时损失 → 0；$p\to 1$ 时损失 → $+\infty$。

**为什么不用平方损失？** 因为 $J=\sum(y-p)^2$ 加上 sigmoid 后**非凸**，梯度下降容易陷在局部极小；而交叉熵损失是**凸函数**，有唯一全局最优，且梯度形式极简。

**Step 6：求梯度（手推，很有价值）。** 对单个样本，$p=\sigma(z)$、$z=\boldsymbol{w}^\top\boldsymbol{x}$：

$$
\begin{aligned}
\frac{\partial}{\partial z}\Big[-\big(y\ln p+(1-y)\ln(1-p)\big)\Big]
&= -\left(\frac{y}{p} - \frac{1-y}{1-p}\right)\cdot\frac{\partial p}{\partial z}\\
&= -\left(\frac{y}{p} - \frac{1-y}{1-p}\right)\cdot p(1-p)\\
&= -\Big(y(1-p) - (1-y)p\Big)\\
&= -(y - yp - p + yp)\\
&= p - y
\end{aligned}
$$

再用链式法则 $\dfrac{\partial J}{\partial w_j} = \dfrac{\partial J}{\partial z}\cdot\dfrac{\partial z}{\partial w_j} = (p-y)\,x_j$，于是

$$\boxed{\frac{\partial J}{\partial w_j} = \big(h_w(\boldsymbol{x}) - y\big)\,x_j},\qquad \frac{\partial J}{\partial b} = h_w(\boldsymbol{x}) - y$$

**结论**：梯度 = **（预测概率 − 真实标签）× 特征值**。这与线性回归的梯度形式**完全一致**——这是广义线性模型（GLM）的一个漂亮性质。

**Step 7：参数更新。**

$$w_j := w_j - \alpha\sum_{i=1}^{n}\big(h_w(\boldsymbol{x}_i)-y_i\big)x_{ij}$$

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/04-逻辑回归.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「从似然到交叉熵损失（完整手推）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/04-逻辑回归.md)
