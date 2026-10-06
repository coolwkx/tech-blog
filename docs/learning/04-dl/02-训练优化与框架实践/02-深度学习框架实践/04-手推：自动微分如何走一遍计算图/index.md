---
article_id: kp-0520deddc915868f
learning_kind: article
learning_category: 04-dl
learning_direction: practice
learning_topic: topic-ae2a0b64784b
learning_sourceId: ae2a0b64784b
learning_order: 3
learning_objective: 理解并验证：手推：自动微分如何走一遍计算图
---

# 手推：自动微分如何走一遍计算图

> **学习目标**：能够解释「手推：自动微分如何走一遍计算图」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：会 Python（类、`with`、装饰器）；知道张量与矩阵乘法；了解前向传播、损失函数、梯度下降与链式法则（参见本目录 01 反向传播与计算图、02 优化与训练技巧）。
>
> **所属主题**：-深度学习框架实践 · 算法细节

## 本次只学这一点

《神经网络与深度学习》4.5.3 节的例子很适合手推。取 $f(x;w,b)=\dfrac{1}{\exp(-(wx+b))+1}=\sigma(wx+b)$，分解成 6 个基本操作，取 $x=1,\ w=0,\ b=0$：

| 节点 | 表达式 | 前向值 | 局部导数 |
| --- | --- | --- | --- |
| $h_1$ | $w\cdot x$ | $0$ | $\partial h_1/\partial w=x=1$ |
| $h_2$ | $h_1+b$ | $0$ | $\partial h_2/\partial h_1=1$ |
| $h_3$ | $-h_2$ | $0$ | $\partial h_3/\partial h_2=-1$ |
| $h_4$ | $\exp(h_3)$ | $1$ | $\partial h_4/\partial h_3=\exp(h_3)=1$ |
| $h_5$ | $h_4+1$ | $2$ | $\partial h_5/\partial h_4=1$ |
| $h_6$ | $1/h_5$ | $0.5$ | $\partial h_6/\partial h_5=-1/h_5^2=-0.25$ |

**反向模式**从输出出发，沿边把局部导数乘起来（多条路径则相加）：

$$\frac{\partial f}{\partial h_6}=1,\quad \frac{\partial f}{\partial h_5}=1\times(-0.25)=-0.25,\quad \frac{\partial f}{\partial h_1}=(-0.25)\times 1\times 1=-0.25,$$

$$\boxed{\frac{\partial f}{\partial w}=\frac{\partial f}{\partial h_1}\cdot\frac{\partial h_1}{\partial w}=(-0.25)\times 1=-0.25}$$

而直接对 $\sigma(wx+b)$ 求导得 $0.25$：**差异来自书里的计算图实现的其实是 $\sigma\big(-(wx+b)\big)$**（表中 $h_3=-h_2$ 那个 $-1$）——这提醒我们"代码里的公式"与"纸上的公式"必须逐项核对。

**为什么默认用反向模式**：对 $f:\mathbb{R}^n\to\mathbb{R}^m$，前向模式遍历每个**输入**（$n$ 遍），反向模式遍历每个**输出**（$m$ 遍）；损失是标量而参数以百万千万计，所以反向模式一遍就能拿到全部梯度——这就是 autograd 的立足点。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/02-优化与训练/07-深度学习框架实践.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「手推：自动微分如何走一遍计算图」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/02-优化与训练/07-深度学习框架实践.md)
