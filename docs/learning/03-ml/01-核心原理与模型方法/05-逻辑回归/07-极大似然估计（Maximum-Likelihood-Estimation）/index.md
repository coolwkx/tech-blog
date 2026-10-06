---
article_id: kp-e425c79a657826d2
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-f80e625a8f58
learning_sourceId: f80e625a8f58
learning_order: 6
learning_objective: 理解并验证：极大似然估计（Maximum Likelihood Estimation）
---

# 极大似然估计（Maximum Likelihood Estimation）

> **学习目标**：能够解释「极大似然估计（Maximum Likelihood Estimation）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性回归与梯度下降（见 [03-线性回归](../../../../../03-ml/02-经典算法/03-线性回归.md)）、概率的基本概念（条件概率、独立事件）、对数运算、混淆矩阵的基本直觉。
>
> **所属主题**：逻辑回归 · 算法细节

## 本次只学这一点

**核心思想**：设模型中含有待估参数 $w$，它可能取很多值。既然已经观测到了样本 $D$，那就从 $w$ 的所有可能值中，**选出使观测结果出现概率最大的那个值**作为估计值。

**抛硬币例子**：一枚不均匀硬币，正面概率为 $\theta$，抛 6 次得到 $D=\{$正, 反, 反, 正, 正, 正$\}$，各次独立，则

$$P(D\mid\theta)=\theta\cdot(1-\theta)\cdot(1-\theta)\cdot\theta\cdot\theta\cdot\theta = \theta^4(1-\theta)$$

问题转化为：**求使 $P(D\mid\theta)$ 最大的 $\theta$**。

- 取对数（把连乘变连加，单调变换不改变极值点）：$\ln L(\theta)=4\ln\theta+\ln(1-\theta)$
- 求导置零：$\dfrac{4}{\theta}-\dfrac{1}{1-\theta}=0 \Rightarrow 4(1-\theta)=\theta \Rightarrow \theta^\star=\dfrac{4}{5}=0.8$

**直观验证**：6 次里 4 次正面，"正面概率 = 4/6 = 0.8"确实就是最合理的猜测。

**为什么要取对数？**

| 原因 | 说明 |
| --- | --- |
| 把连乘变连加 | $\ln\prod p_i=\sum\ln p_i$，避免大量小数连乘导致**下溢为 0** |
| 求导更方便 | 对数的导数形式简单（$(\ln x)'=1/x$） |
| 不改变极值 | $\ln$ 是单调递增函数，$\arg\max L = \arg\max \ln L$ |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/04-逻辑回归.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「极大似然估计（Maximum Likelihood Estimation）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/04-逻辑回归.md)
