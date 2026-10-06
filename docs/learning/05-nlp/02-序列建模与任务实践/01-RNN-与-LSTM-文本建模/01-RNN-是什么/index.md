---
article_id: kp-04f55770f06801fb
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-d7bbe1de9b00
learning_sourceId: d7bbe1de9b00
learning_order: 0
learning_objective: 理解并验证：RNN 是什么
---

# RNN 是什么

> **学习目标**：能够解释「RNN 是什么」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 04 篇词向量与 `nn.Embedding`、第 05 篇文本分类流水线、PyTorch `nn.Module` 与 `Dataset/DataLoader`、链式法则与反向传播。
>
> **所属主题**：RNN 与 LSTM 文本建模 · 核心概念

## 本次只学这一点

循环神经网络（Recurrent Neural Network, RNN）接收一个**序列**作为输入，输出也是一个序列（或它的某种归约）。它擅长处理连续语言文本，典型应用：机器翻译、文本生成、文本分类、摘要生成。

核心思想：**在所有时间步共享同一套权重**，并用一个隐藏状态 $h_t$ 充当「记忆」，把历史信息向后传递。

$$
h_t = \tanh(W_{xh}x_t + W_{hh}h_{t-1} + b_h),\qquad o_t = W_{ho}h_t + b_o
$$

注意在一个时间步内，输出 $h_t$ 与 $o_t$ 的数值相同（$o_t$ 是 $h_t$ 的线性变换），工程实现里通常只暴露 $h_t$。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/07-RNN与LSTM文本建模.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「RNN 是什么」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/07-RNN与LSTM文本建模.md)
