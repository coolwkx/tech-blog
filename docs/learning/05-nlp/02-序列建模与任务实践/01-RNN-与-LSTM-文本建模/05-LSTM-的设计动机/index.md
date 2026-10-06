---
article_id: kp-c0a620a8cb1d085a
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-d7bbe1de9b00
learning_sourceId: d7bbe1de9b00
learning_order: 4
learning_objective: 理解并验证：LSTM 的设计动机
---

# LSTM 的设计动机

> **学习目标**：能够解释「LSTM 的设计动机」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 04 篇词向量与 `nn.Embedding`、第 05 篇文本分类流水线、PyTorch `nn.Module` 与 `Dataset/DataLoader`、链式法则与反向传播。
>
> **所属主题**：RNN 与 LSTM 文本建模 · 核心概念

## 本次只学这一点

梯度问题的数学根源：反向传播时，梯度要沿时间步连乘

$$
\frac{\partial h_t}{\partial h_{t-1}} = W_{hh}^\top \operatorname{diag}\big(1-\tanh^2(\cdot)\big)
$$

连乘 $T$ 次后，若 $W_{hh}$ 的谱半径小于 1，梯度按指数衰减（消失）；大于 1 则指数增长（爆炸）。tanh 的导数最大为 1，也在持续衰减。

LSTM（Long Short-Term Memory, 1997）的思路是：**开一条几乎恒等的「高速公路」让梯度直通**，并用门控决定「写什么、忘什么、读什么」。这条通道就是细胞状态 $c_t$。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/07-RNN与LSTM文本建模.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「LSTM 的设计动机」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/07-RNN与LSTM文本建模.md)
