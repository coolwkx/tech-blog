---
article_id: kp-26cfa2c608955464
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-80865e5a5b8b
learning_sourceId: 80865e5a5b8b
learning_order: 4
learning_objective: 理解并验证："每一层 = 仿射变换 + 非线性变换"
---

# "每一层 = 仿射变换 + 非线性变换"

> **学习目标**：能够解释「"每一层 = 仿射变换 + 非线性变换"」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性代数（矩阵乘法、转置、Frobenius 范数）、微积分（链式法则、偏导、Taylor 展开）、Logistic 回归与 Softmax 回归、梯度下降与交叉熵损失。
>
> **所属主题**：-神经网络基础 · 核心思想

## 本次只学这一点

前馈网络逐层迭代两条公式即可：

$$\boldsymbol z^{(l)}=\boldsymbol W^{(l)}\boldsymbol a^{(l-1)}+\boldsymbol b^{(l)},\qquad \boldsymbol a^{(l)}=f_l(\boldsymbol z^{(l)})$$

- 第一步是**仿射变换（affine transformation）**：先线性组合再平移；
- 第二步是**非线性变换**：逐元素（element-wise）作用激活函数。

只有这两步**同时存在**，堆叠才有意义。若去掉非线性，$L$ 层网络会塌缩成一层线性模型（证明见 2.2 节）。整网因此是一个复合函数 $\boldsymbol{\hat y}=\phi(\boldsymbol x;\boldsymbol W,\boldsymbol b)$，参数 $\boldsymbol W,\boldsymbol b$ 就是所有层的权重与偏置。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/01-基础与反向传播/01-神经网络基础.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「"每一层 = 仿射变换 + 非线性变换"」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/01-基础与反向传播/01-神经网络基础.md)
