---
article_id: kp-ff47cf82b1de6866
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-0ff9cceb3f3d
learning_sourceId: 0ff9cceb3f3d
learning_order: 4
learning_objective: 理解并验证：参数梯度
---

# 参数梯度

> **学习目标**：能够解释「参数梯度」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：矩阵与向量求导（分母布局、Jacobian）、多元链式法则、Logistic/Tanh/ReLU 的导数、Softmax 与交叉熵、Frobenius 范数与 $\ell_2$ 正则化、凸/非凸优化与局部最优的基本概念。
>
> **所属主题**：-反向传播与梯度下降 · 算法细节

## 本次只学这一点

把三个偏导数代回链式法则：$\dfrac{\partial \mathcal{L}}{\partial w^{(l)}_{ij}}=\sum_k\delta^{(l)}_k\mathbb{1}[k=i]a^{(l-1)}_j=\delta^{(l)}_i a^{(l-1)}_j=\big[\boldsymbol{\delta}^{(l)}(\boldsymbol{a}^{(l-1)})^\top\big]_{ij}$，写成矩阵形式即

$$\nabla_{\boldsymbol{W}^{(l)}}\mathcal{L}=\boldsymbol{\delta}^{(l)}\big(\boldsymbol{a}^{(l-1)}\big)^\top\in\mathbb{R}^{M_l\times M_{l-1}},\qquad \nabla_{\boldsymbol{b}^{(l)}}\mathcal{L}=\boldsymbol{\delta}^{(l)}\in\mathbb{R}^{M_l}.\tag{4.68, 4.69}$$

（推导中的 $\delta^{(l)}_i a^{(l-1)}_j$ 正是两向量外积的元素。）加入 $\ell_2$ 正则化后的实际更新为 $\boldsymbol{W}^{(l)}\leftarrow\boldsymbol{W}^{(l)}-\eta\big(\nabla_{\boldsymbol{W}^{(l)}}\mathcal{L}+\lambda\boldsymbol{W}^{(l)}\big)$、$\boldsymbol{b}^{(l)}\leftarrow\boldsymbol{b}^{(l)}-\eta\nabla_{\boldsymbol{b}^{(l)}}\mathcal{L}$——注意教材明确指出**正则项只包含权重参数、不包含偏置**。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/01-基础与反向传播/03-反向传播与梯度下降.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「参数梯度」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/01-基础与反向传播/03-反向传播与梯度下降.md)
