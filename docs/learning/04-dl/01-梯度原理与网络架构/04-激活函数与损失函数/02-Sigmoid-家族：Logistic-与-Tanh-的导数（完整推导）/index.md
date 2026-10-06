---
article_id: kp-e819f63c39af626b
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-93c70b02b9e5
learning_sourceId: 93c70b02b9e5
learning_order: 1
learning_objective: 理解并验证：Sigmoid 家族：Logistic 与 Tanh 的导数（完整推导）
---

# Sigmoid 家族：Logistic 与 Tanh 的导数（完整推导）

> **学习目标**：能够解释「Sigmoid 家族：Logistic 与 Tanh 的导数（完整推导）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性判别函数、Logistic/Softmax 回归、梯度下降、链式法则与反向传播、伯努利分布与交叉熵。
>
> **所属主题**：-激活函数与损失函数 · 算法细节

## 本次只学这一点

$$\sigma(x)=\frac{1}{1+e^{-x}}=(1+e^{-x})^{-1}.$$

链式法则（令 $u=1+e^{-x}$）得 $\dfrac{d\sigma}{dx}=-(1+e^{-x})^{-2}\cdot(-e^{-x})=\dfrac{e^{-x}}{(1+e^{-x})^2}$。把分子 $e^{-x}$ 写成 $(1+e^{-x})-1$：

$$\frac{e^{-x}}{(1+e^{-x})^2}=\frac{(1+e^{-x})-1}{(1+e^{-x})^2}=\frac{1}{1+e^{-x}}-\frac{1}{(1+e^{-x})^2}=\sigma(x)-\sigma(x)^2
\quad\Longrightarrow\quad \boxed{\sigma'(x)=\sigma(x)\bigl(1-\sigma(x)\bigr)\in(0,\,0.25].}$$

**导数可由自身表示**，反向传播时无需重算 $\exp$；最大值 0.25 在 $x=0$ 处取到，意味着**梯度每穿过一层 Logistic 至多缩水到 1/4**，10 层即 $0.25^{10}\approx10^{-6}$——梯度消失的定量解释。$\sigma$ 的两个工程含义（教材 4.1.1 节）：①**输出可看作概率**，直接当后验概率 $P(y=1\mid x)=\sigma(w^Tx)$ 用；②**可看作软性门（soft gate）**，$\sigma\in(0,1)$ 作 0/1 之间的连续开关控制信息通过量——LSTM 的三个门、GRU 的更新门、Swish/GELU 的门控都是这一思想。

**Tanh** 定义为 $\tanh(x)=\dfrac{e^{x}-e^{-x}}{e^{x}+e^{-x}}$。由 $\sigma(2x)=\dfrac{1}{1+e^{-2x}}=\dfrac{e^{2x}}{e^{2x}+1}$ 得

$$2\sigma(2x)-1=\frac{2e^{2x}}{e^{2x}+1}-1=\frac{e^{2x}-1}{e^{2x}+1}\ \xrightarrow{\ \times e^{-x}/e^{-x}\ }\ \frac{e^{x}-e^{-x}}{e^{x}+e^{-x}}=\tanh(x)\quad\Longrightarrow\quad\boxed{\tanh(x)=2\sigma(2x)-1.}$$

**导数**：$\tanh'(x)=2\cdot\sigma'(2x)\cdot2=4\sigma(2x)\bigl(1-\sigma(2x)\bigr)$。代入 $\sigma(2x)=\frac{1+\tanh x}{2}$、$1-\sigma(2x)=\frac{1-\tanh x}{2}$，得 $\tanh'(x)=1-\tanh^2(x)\in(0,1]$。上限是 **1** 而非 0.25，故同分布下 Tanh 的梯度比 Logistic 大最多 4 倍。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/02-优化与训练/02-激活函数与损失函数.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Sigmoid 家族：Logistic 与 Tanh 的导数（完整推导）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/02-优化与训练/02-激活函数与损失函数.md)
