---
article_id: kp-e40b2c8c27d1b868
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-93c70b02b9e5
learning_sourceId: 93c70b02b9e5
learning_order: 6
learning_objective: 理解并验证：损失函数：平方、交叉熵、负对数似然、Hinge
---

# 损失函数：平方、交叉熵、负对数似然、Hinge

> **学习目标**：能够解释「损失函数：平方、交叉熵、负对数似然、Hinge」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性判别函数、Logistic/Softmax 回归、梯度下降、链式法则与反向传播、伯努利分布与交叉熵。
>
> **所属主题**：-激活函数与损失函数 · 算法细节

## 本次只学这一点

**平方损失**（用于回归）：$\mathcal{L}=\frac12(y-f(x;\theta))^2$。教材明确指出**平方损失一般不适用于分类问题**（习题 2-1）。

**交叉熵**（用于分类）：设 $y\in\{1,\dots,C\}$，one-hot 标签 $y$，模型输出 $\hat y_c=P(y=c\mid x;\theta)$，

$$\mathcal{L}(y,\hat y)=-y^T\log\hat y=-\sum_{c=1}^{C}y_c\log\hat y_c\ \overset{\text{one-hot}}{=}\ -\log\hat y_{y}.$$

$\hat y_y$ 就是真实类别的预测概率，也即该样本的**似然**，所以**交叉熵损失就是负对数似然损失（Negative Log-Likelihood, NLL）**：最小化交叉熵等价于最大化对数似然（最大似然估计）；又因 $H(p,q)=H(p)+\mathrm{KL}(p\|q)$ 且 $H(p)$ 与参数无关，它也等价于最小化 $\mathrm{KL}(p\|q)$。

**二分类交叉熵（BCE）**：$y\in\{0,1\}$，$\hat y=\sigma(z)$，$\mathcal{L}=-[y\log\hat y+(1-y)\log(1-\hat y)]$。

**Hinge 损失**（最大间隔分类／SVM）：$y\in\{-1,+1\}$，判别值 $f=w^Tx+b$，$\mathcal{L}_{\text{hinge}}=\max\bigl(0,1-yf\bigr)=[1-yf]_+$。它只惩罚间隔不足 1 的样本，$yf\ge1$ 时梯度为 0，故解**只由支持向量决定**，天然稀疏；感知器用的则是 $\max(0,-yf)$（间隔固定为 0）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/02-优化与训练/02-激活函数与损失函数.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「损失函数：平方、交叉熵、负对数似然、Hinge」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/02-优化与训练/02-激活函数与损失函数.md)
