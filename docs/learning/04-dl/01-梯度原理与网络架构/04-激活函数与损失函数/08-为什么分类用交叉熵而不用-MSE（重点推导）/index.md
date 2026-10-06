---
article_id: kp-a1185ad197b47584
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-93c70b02b9e5
learning_sourceId: 93c70b02b9e5
learning_order: 7
learning_objective: 理解并验证：为什么分类用交叉熵而不用 MSE（重点推导）
---

# 为什么分类用交叉熵而不用 MSE（重点推导）

> **学习目标**：能够解释「为什么分类用交叉熵而不用 MSE（重点推导）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性判别函数、Logistic/Softmax 回归、梯度下降、链式法则与反向传播、伯努利分布与交叉熵。
>
> **所属主题**：-激活函数与损失函数 · 算法细节

## 本次只学这一点

**(A) Logistic + MSE：梯度里多出一个 $\sigma'$ 因子。** 设 $\hat y=\sigma(z)$，$\mathcal{L}_{\text{MSE}}=\frac12(\hat y-y)^2$，

$$\frac{\partial\mathcal{L}}{\partial z}=(\hat y-y)\cdot\underbrace{\sigma(z)(1-\sigma(z))}_{\le0.25}.$$

当模型"自信地错"（$y=1,z=-6$，$\hat y\approx0.0025$）时误差 $(\hat y-y)\approx-1$ 很大，但 $\sigma'(z)\approx0.0025$ 几乎为 0，乘积仅 $\approx-0.0025$：**误差越大梯度越小**，最需要纠正的地方反而几乎不动。

**(B) Logistic + 交叉熵：梯度化简为 $\hat y-y$。** $\mathcal{L}=-y\log\hat y-(1-y)\log(1-\hat y)$。逐项对 $z$ 求导：

$$\frac{\partial}{\partial z}\bigl(-y\log\sigma(z)\bigr)=-y\cdot\frac{\sigma'(z)}{\sigma(z)}=-y\bigl(1-\sigma(z)\bigr),$$

$$\frac{\partial}{\partial z}\bigl(-(1-y)\log(1-\sigma(z))\bigr)=-(1-y)\cdot\frac{-\sigma'(z)}{1-\sigma(z)}=(1-y)\sigma(z).$$

两项相加：

$$\boxed{\frac{\partial\mathcal{L}_{\text{CE}}}{\partial z}=\sigma(z)-y=\hat y-y.}$$

$\sigma'$ **被完全约掉**，梯度就是"预测减真值"，误差多大梯度就多大，饱和区也不会被压制——这就是分类任务用交叉熵的根本原因。教材 3.2.1 节把同一结论写成凸性语言（$\mathcal{R}(w)$ 连续可导且为凸函数），而 4.6.1 节用 $\hat y=\sigma(w_2\sigma(w_1x))$ 说明深层网络上两种损失都是非凸的，但交叉熵的梯度性质更好。

**(C) 多分类：Softmax + 交叉熵同样干净。** 用 $\partial\hat y_c/\partial z_j=\hat y_c(\delta_{cj}-\hat y_j)$ 代入 $\mathcal{L}=-\sum_c y_c\log\hat y_c$：

$$\frac{\partial\mathcal{L}}{\partial z_j}=-\sum_c\frac{y_c}{\hat y_c}\hat y_c(\delta_{cj}-\hat y_j)=-\sum_c y_c(\delta_{cj}-\hat y_j)=-y_j+\hat y_j\sum_c y_c=\hat y_j-y_j .$$

（末步用 one-hot 的 $\sum_c y_c=1$。）Softmax 还有两个注意点：①**平移不变性**——各分量同加常数输出不变，故 $C$ 组权重冗余（教材 3.3.1 节指出需用正则化约束参数），工程上据此做数值稳定：计算前先减 $\max_j z_j$；②正因平移不变，Softmax + 交叉熵的 Hessian 奇异，需权重衰减定解。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/02-优化与训练/02-激活函数与损失函数.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「为什么分类用交叉熵而不用 MSE（重点推导）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/02-优化与训练/02-激活函数与损失函数.md)
