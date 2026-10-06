---
article_id: kp-5dff5c26d0051d71
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-93c70b02b9e5
learning_sourceId: 93c70b02b9e5
learning_order: 4
learning_objective: 理解并验证：Swish 与 GELU：门控型激活函数
---

# Swish 与 GELU：门控型激活函数

> **学习目标**：能够解释「Swish 与 GELU：门控型激活函数」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性判别函数、Logistic/Softmax 回归、梯度下降、链式法则与反向传播、伯努利分布与交叉熵。
>
> **所属主题**：-激活函数与损失函数 · 算法细节

## 本次只学这一点

**Swish 是自门控（self-gated）激活函数**：$\text{swish}(x)=x\cdot\sigma(\beta x)$，$\beta$ 是可学习参数或固定超参数。$\sigma(\beta x)\in(0,1)$ 是**软性门控**：门开（$\to1$）时输出近似 $x$ 本身，门关（$\to0$）时输出近似 0。$\beta$ 的极限行为（教材 4.1.3 节）：$\beta=0$ 时 $\sigma(0)=0.5$，退化为**线性函数** $x/2$；$\beta=1$ 时 $x>0$ 近似线性、$x<0$ 近似饱和，且有**非单调性**（这是与 ReLU 单调不减的本质区别：Swish 在负半轴先降后升，$x\approx-1.28$ 处取最小值约 $-0.278$）；$\beta\to+\infty$ 时 $\sigma(\beta x)$ 趋向离散 0-1 阶跃，Swish 近似为 **ReLU**。所以 Swish 是**线性函数与 ReLU 之间的非线性插值**。$\beta=1$ 固定时它有个更常见的名字 **SiLU**（PyTorch `nn.SiLU`）。**导数**（教材习题 4-4，乘积法则）：

$$\text{swish}'(x)=\sigma(\beta x)+\beta x\,\sigma(\beta x)\bigl(1-\sigma(\beta x)\bigr).$$

**GELU 与 Swish 类似，但门换成标准正态分布的累积分布函数**：

$$\text{GELU}(x)=x\cdot\Phi(x),\qquad \Phi(x)=P(X\le x),\ X\sim\mathcal{N}(\mu,\sigma^2),$$

一般取 $\mu=0,\sigma=1$。由于正态 CDF 本身是 S 型函数，可写成 $x\cdot\sigma(1.702x)$——此时 GELU **等价于一种特殊的 Swish**。实现中为避免 `erf` 开销常用 tanh 近似：

$$\text{GELU}(x)\approx0.5x\left(1+\tanh\left(\sqrt{\tfrac{2}{\pi}}\left(x+0.044715x^3\right)\right)\right).$$

曲线与 Swish 很像（最小值约 $-0.17$），但它是 Transformer 的事实标准（BERT、GPT 系列）。PyTorch 中 `nn.GELU` 默认用 erf 精确版，`approximate='tanh'` 用上式。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/02-优化与训练/02-激活函数与损失函数.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Swish 与 GELU：门控型激活函数」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/02-优化与训练/02-激活函数与损失函数.md)
