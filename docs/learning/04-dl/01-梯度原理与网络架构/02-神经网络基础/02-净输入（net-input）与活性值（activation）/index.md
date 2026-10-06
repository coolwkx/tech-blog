---
article_id: kp-4794855e9d89494d
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-80865e5a5b8b
learning_sourceId: 80865e5a5b8b
learning_order: 1
learning_objective: 理解并验证：净输入（net input）与活性值（activation）
---

# 净输入（net input）与活性值（activation）

> **学习目标**：能够解释「净输入（net input）与活性值（activation）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性代数（矩阵乘法、转置、Frobenius 范数）、微积分（链式法则、偏导、Taylor 展开）、Logistic 回归与 Softmax 回归、梯度下降与交叉熵损失。
>
> **所属主题**：-神经网络基础 · 核心思想

## 本次只学这一点

这是本主题最容易被含糊过去的两个术语，必须分清：

- **净输入（net input / net activation）** $\boldsymbol z$：输入的**加权和**，是纯线性的量；
- **活性值（activation）** $\boldsymbol a$：净输入经过激活函数之后的输出，是**非线性**的量。

$$\boldsymbol z = \sum_{i=1}^{d} w_i x_i + b = \boldsymbol w^\top \boldsymbol x + b,\qquad a = f(z)$$

**权重与偏置的几何含义**：$\boldsymbol w$ 是该神经元在输入空间中划分超平面的**法向量**，它决定"对哪个方向敏感"；$b$ 是**阈值/平移量**，决定"多容易兴奋"（$b$ 越大越容易激活）。若把 $b$ 写进增广向量（$\boldsymbol x \leftarrow [\boldsymbol x;1]$、$\boldsymbol w\leftarrow[\boldsymbol w;b]$），神经元就退化成纯粹的 $\boldsymbol w^\top\boldsymbol x$，这也是教材里常做的简化。**注意**：正则化时通常只惩罚 $\boldsymbol W$ 不惩罚 $\boldsymbol b$，因为偏置只控制平移、不影响模型复杂度（见 2.6 节）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/01-基础与反向传播/01-神经网络基础.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「净输入（net input）与活性值（activation）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/01-基础与反向传播/01-神经网络基础.md)
