---
article_id: kp-e60b26a6e5207b2a
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-0ff9cceb3f3d
learning_sourceId: 0ff9cceb3f3d
learning_order: 5
learning_objective: 理解并验证：反向传播算法三步与伪码
---

# 反向传播算法三步与伪码

> **学习目标**：能够解释「反向传播算法三步与伪码」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：矩阵与向量求导（分母布局、Jacobian）、多元链式法则、Logistic/Tanh/ReLU 的导数、Softmax 与交叉熵、Frobenius 范数与 $\ell_2$ 正则化、凸/非凸优化与局部最优的基本概念。
>
> **所属主题**：-反向传播与梯度下降 · 算法细节

## 本次只学这一点

1. **前馈**：逐层计算并缓存 $\boldsymbol{z}^{(l)}$、$\boldsymbol{a}^{(l)}$，直到输出层得到 $\hat{\boldsymbol{y}}$ 与损失；
2. **反向**：从 $\boldsymbol{\delta}^{(L)}$ 起按公式(4.63)逐层算出每个 $\boldsymbol{\delta}^{(l)}$；
3. **更新**：用 $\nabla_{\boldsymbol{W}^{(l)}}=\boldsymbol{\delta}^{(l)}(\boldsymbol{a}^{(l-1)})^\top$、$\nabla_{\boldsymbol{b}^{(l)}}=\boldsymbol{\delta}^{(l)}$ 做梯度下降。

```text
输入: 训练集 D={(x^(n), y^(n))}, 学习率 eta, 正则化系数 lambda, 网络层数 L
1 随机初始化 W, b
2 repeat
3 对训练集 D 中的样本随机重排序
4 for n = 1 .. N do
5 取出样本 (x^(n), y^(n))
6 前馈: 逐层计算 z^(l) = W^(l)a^(l-1)+b^(l), a^(l) = f(z^(l)), 缓存 a^(l), z^(l)
7 反向: delta^(L) = dL/dz^(L) # Softmax+CE 时为 y_hat - y
8 for l = L-1 down to 1:
9 delta^(l) = f'(z^(l)) ⊙ ((W^(l+1))^T delta^(l+1)) # 公式 (4.63)
10 求梯度: dW^(l) = delta^(l) (a^(l-1))^T ; db^(l) = delta^(l) # 公式 (4.68)(4.69)
11 更新: W^(l) <- W^(l) - eta (dW^(l) + lambda W^(l)) ; b^(l) <- b^(l) - eta db^(l)
12 end for
13 until 模型在验证集上的错误率不再下降
输出: W, b
```

**复杂度**：前馈 $O(C)$，反向也只需一遍图遍历、约 $O(C)$（常数因子约 2～3 倍），每次迭代总代价 $O(C)$，$C$ 是网络中连接/参数总量。相比"对每个参数单独施加数值扰动"的 $O(nC)$，这是数量级的胜利。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/01-基础与反向传播/03-反向传播与梯度下降.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「反向传播算法三步与伪码」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/01-基础与反向传播/03-反向传播与梯度下降.md)
