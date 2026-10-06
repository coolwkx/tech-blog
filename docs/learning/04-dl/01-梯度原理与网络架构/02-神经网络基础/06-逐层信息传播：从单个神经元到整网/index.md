---
article_id: kp-c72bed79dc84399a
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-80865e5a5b8b
learning_sourceId: 80865e5a5b8b
learning_order: 5
learning_objective: 理解并验证：逐层信息传播：从单个神经元到整网
---

# 逐层信息传播：从单个神经元到整网

> **学习目标**：能够解释「逐层信息传播：从单个神经元到整网」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性代数（矩阵乘法、转置、Frobenius 范数）、微积分（链式法则、偏导、Taylor 展开）、Logistic 回归与 Softmax 回归、梯度下降与交叉熵损失。
>
> **所属主题**：-神经网络基础 · 算法细节

## 本次只学这一点

**步骤 1（单神经元）**：神经元接收 $d$ 个输入 $\boldsymbol x=[x_1;\dots;x_d]$，权重 $\boldsymbol w=[w_1;\dots;w_d]$，偏置 $b$：

$$z=\sum_{i=1}^{d}w_i x_i+b=\boldsymbol w^\top\boldsymbol x+b,\qquad a=f(z)$$

**步骤 2（一层的向量化）**：第 $l$ 层有 $M_l$ 个神经元，每个神经元对应 $\boldsymbol W^{(l)}$ 的一行：

$$\boldsymbol z^{(l)}=\boldsymbol W^{(l)}\boldsymbol a^{(l-1)}+\boldsymbol b^{(l)}\in\mathbb{R}^{M_l},\qquad \boldsymbol a^{(l)}=f_l(\boldsymbol z^{(l)})$$

维度校验：$(M_l\times M_{l-1})\cdot(M_{l-1}\times1)+(M_l\times1)\to M_l\times1$，一致。

**步骤 3（合并写法和整网展开）**：两条公式可合并为 $\boldsymbol a^{(l)}=f_l\big(\boldsymbol W^{(l)}\boldsymbol a^{(l-1)}+\boldsymbol b^{(l)}\big)$。整网就是一个复合函数：

$$\boldsymbol x=\boldsymbol a^{(0)}\to\boldsymbol z^{(1)}\to\boldsymbol a^{(1)}\to\boldsymbol z^{(2)}\to\cdots\to\boldsymbol z^{(L)}\to\boldsymbol a^{(L)}=\phi(\boldsymbol x;\boldsymbol W,\boldsymbol b)$$

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/01-基础与反向传播/01-神经网络基础.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「逐层信息传播：从单个神经元到整网」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/01-基础与反向传播/01-神经网络基础.md)
