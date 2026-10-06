---
article_id: kp-69bfc721ba27f397
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-d7bbe1de9b00
learning_sourceId: d7bbe1de9b00
learning_order: 6
learning_objective: 理解并验证：完整公式
---

# 完整公式

> **学习目标**：能够解释「完整公式」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 04 篇词向量与 `nn.Embedding`、第 05 篇文本分类流水线、PyTorch `nn.Module` 与 `Dataset/DataLoader`、链式法则与反向传播。
>
> **所属主题**：RNN 与 LSTM 文本建模 · 方法细节

## 本次只学这一点

设 $x_t$ 是当前输入，$h_{t-1}$ 是上一时刻隐状态，$[h_{t-1}, x_t]$ 表示拼接：

$$
\begin{aligned}
f_t &= \sigma\big(W_f \cdot [h_{t-1}, x_t] + b_f\big) &&\text{遗忘门}\\
i_t &= \sigma\big(W_i \cdot [h_{t-1}, x_t] + b_i\big) &&\text{输入门}\\
\tilde{c}_t &= \tanh\big(W_c \cdot [h_{t-1}, x_t] + b_c\big) &&\text{候选细胞状态}\\
c_t &= f_t \odot c_{t-1} + i_t \odot \tilde{c}_t &&\text{更新细胞状态}\\
o_t &= \sigma\big(W_o \cdot [h_{t-1}, x_t] + b_o\big) &&\text{输出门}\\
h_t &= o_t \odot \tanh(c_t) &&\text{输出隐状态}
\end{aligned}
$$

其中 $\sigma$ 是 sigmoid（输出 0–1，充当「开关」），$\odot$ 是逐元素相乘。

**关键在第四条**：$c_t = f_t \odot c_{t-1} + i_t \odot \tilde{c}_t$。当 $f_t \approx 1$ 时，$c_t \approx c_{t-1}$，梯度沿这条路径近似恒等传播（$\partial c_t/\partial c_{t-1} \approx f_t$），不会被反复连乘衰减。这就是「门控缓解梯度消失」的数学本质——**它不是让梯度不衰减，而是给梯度提供了一条衰减更慢的路径**。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/07-RNN与LSTM文本建模.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「完整公式」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/07-RNN与LSTM文本建模.md)
