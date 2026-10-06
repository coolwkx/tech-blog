---
article_id: kp-f8a2462225aa92ec
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-80865e5a5b8b
learning_sourceId: 80865e5a5b8b
learning_order: 6
learning_objective: 理解并验证：手推：一个 2-1-1 网络的完整前向展开
---

# 手推：一个 2-1-1 网络的完整前向展开

> **学习目标**：能够解释「手推：一个 2-1-1 网络的完整前向展开」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性代数（矩阵乘法、转置、Frobenius 范数）、微积分（链式法则、偏导、Taylor 展开）、Logistic 回归与 Softmax 回归、梯度下降与交叉熵损失。
>
> **所属主题**：-神经网络基础 · 算法细节

## 本次只学这一点

取输入 $\boldsymbol x=[x_1;x_2]$，隐藏层 1 个神经元（激活 $f_1$），输出层 1 个神经元（Logistic $f_2=\sigma$）：

**手推步骤 1**：隐藏层净输入

$$z^{(1)}=w_1^{(1)}x_1+w_2^{(1)}x_2+b^{(1)}$$

**手推步骤 2**：隐藏层活性值

$$a^{(1)}=f_1\big(z^{(1)}\big)$$

**手推步骤 3**：输出层净输入与输出（$M_2=1$，故 $\boldsymbol W^{(2)}$ 退化成标量 $w^{(2)}$）

$$z^{(2)}=w^{(2)}a^{(1)}+b^{(2)},\qquad \hat y=\sigma\big(z^{(2)}\big)=\frac{1}{1+\exp\big(-\big(w^{(2)}f_1(w_1^{(1)}x_1+w_2^{(1)}x_2+b^{(1)})+b^{(2)}\big)\big)}$$

**手推步骤 4（为什么必须有非线性）**：假设隐藏层也是线性的，即 $f_1(z)=z$，则

$$\boldsymbol a^{(2)}=\boldsymbol W^{(2)}\big(\boldsymbol W^{(1)}\boldsymbol x+\boldsymbol b^{(1)}\big)+\boldsymbol b^{(2)}=\underbrace{\big(\boldsymbol W^{(2)}\boldsymbol W^{(1)}\big)}_{\boldsymbol W'}\boldsymbol x+\underbrace{\big(\boldsymbol W^{(2)}\boldsymbol b^{(1)}+\boldsymbol b^{(2)}\big)}_{\boldsymbol b'}$$

结果仍然是**一个仿射变换**，与单层的 Logistic/Softmax 回归完全等价。所以"深度"带来的表达能力**全部来自激活函数的非线性**：没有非线性，$L$ 层和 1 层没有区别（这也是 XOR 问题单层线性模型解不出来的原因，见 3 节示例）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/01-基础与反向传播/01-神经网络基础.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「手推：一个 2-1-1 网络的完整前向展开」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/01-基础与反向传播/01-神经网络基础.md)
