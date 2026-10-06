---
article_id: kp-b0c337ec8ac51150
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-80865e5a5b8b
learning_sourceId: 80865e5a5b8b
learning_order: 8
learning_objective: 理解并验证：前馈网络 = 特征转换 $\phi(\boldsymbol x)$ + 分类器
---

# 前馈网络 = 特征转换 $\phi(\boldsymbol x)$ + 分类器

> **学习目标**：能够解释「前馈网络 = 特征转换 $\phi(\boldsymbol x)$ + 分类器」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性代数（矩阵乘法、转置、Frobenius 范数）、微积分（链式法则、偏导、Taylor 展开）、Logistic 回归与 Softmax 回归、梯度下降与交叉熵损失。
>
> **所属主题**：-神经网络基础 · 算法细节

## 本次只学这一点

多层前馈网络可以看成非线性复合函数 $\phi:\mathbb{R}^{D}\to\mathbb{R}^{D'}$，把原始特征 $\boldsymbol x$ 映射为新的特征 $\phi(\boldsymbol x)$，再接一个分类器 $g(\cdot)$：

$$\hat{\boldsymbol y}=g\big(\phi(\boldsymbol x);\boldsymbol\theta\big)$$

**最后一层的设计（这是把神经网络和线性模型接起来的关键）**：

| 任务 | 最后一层神经元个数 | 激活函数 | 输出含义 | 常用损失 |
| --- | --- | --- | --- | --- |
| 回归 | 1（或输出维度） | 无（恒等） | 实数值 | 平方损失 |
| 二分类 $y\in\{0,1\}$ | 1 | Logistic $\sigma$ | $P(y=1\mid\boldsymbol x)=\sigma(\boldsymbol z^{(L)})$ | 二分类交叉熵 / BCE |
| 多分类 $y\in\{1,\dots,C\}$ | $C$ | Softmax | $\hat{\boldsymbol y}=\mathrm{softmax}(\boldsymbol z^{(L)})$，各维为条件概率 | 多分类交叉熵 |

- **二分类**：最后一层只用一个神经元，激活函数为 Logistic 函数 $\sigma$。即 $P(y=1\mid\boldsymbol x)=a^{(L)}$。
- **多分类**：最后一层放 $C$ 个神经元，激活函数为 Softmax，$\hat{\boldsymbol y}=\mathrm{softmax}(\boldsymbol z^{(L)})$，第 $c$ 维是 $P(y=c\mid\boldsymbol x)$。
- **反向的等价关系同样重要**：既然 Logistic / Softmax 回归可以当成网络的最后一层，那么 **Logistic 回归和 Softmax 回归本身就是只有一层的神经网络**（输入层 → 输出层，无隐藏层）。这也解释了为什么二者的参数学习推导和单层网络的反向传播长得一模一样：$\partial\mathcal{L}/\partial\boldsymbol z=\hat{\boldsymbol y}-\boldsymbol y$。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/01-基础与反向传播/01-神经网络基础.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「前馈网络 = 特征转换 $\phi(\boldsymbol x)$ + 分类器」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/01-基础与反向传播/01-神经网络基础.md)
