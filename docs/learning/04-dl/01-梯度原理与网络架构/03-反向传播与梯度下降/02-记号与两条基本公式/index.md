---
article_id: kp-afe8f102ede5271d
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-0ff9cceb3f3d
learning_sourceId: 0ff9cceb3f3d
learning_order: 1
learning_objective: 理解并验证：记号与两条基本公式
---

# 记号与两条基本公式

> **学习目标**：能够解释「记号与两条基本公式」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：矩阵与向量求导（分母布局、Jacobian）、多元链式法则、Logistic/Tanh/ReLU 的导数、Softmax 与交叉熵、Frobenius 范数与 $\ell_2$ 正则化、凸/非凸优化与局部最优的基本概念。
>
> **所属主题**：-反向传播与梯度下降 · 算法细节

## 本次只学这一点

考虑 $L$ 层前馈网络（输入层记作第 0 层，激活函数 $f_l$ 按位作用）：$\boldsymbol{z}^{(l)}=\boldsymbol{W}^{(l)}\boldsymbol{a}^{(l-1)}+\boldsymbol{b}^{(l)}$，$\boldsymbol{a}^{(l)}=f_l(\boldsymbol{z}^{(l)})$，$\boldsymbol{a}^{(0)}=\boldsymbol{x}$。对样本 $(\boldsymbol{x},\boldsymbol{y})$ 损失为 $\mathcal{L}(\boldsymbol{y},\hat{\boldsymbol{y}})$，目标就是求 $\partial\mathcal{L}/\partial w^{(l)}_{ij}$。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/01-基础与反向传播/03-反向传播与梯度下降.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「记号与两条基本公式」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/01-基础与反向传播/03-反向传播与梯度下降.md)
