---
article_id: kp-f65093f610cf7936
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-cbc77f3ab05c
learning_sourceId: cbc77f3ab05c
learning_order: 6
learning_objective: 理解并验证：Multi-Head Attention 的计算方式
---

# Multi-Head Attention 的计算方式

> **学习目标**：能够解释「Multi-Head Attention 的计算方式」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 07 篇 RNN / LSTM / seq2seq、PyTorch 的 `nn.Linear` 与张量 `view/transpose/matmul`、softmax 与交叉熵。
>
> **所属主题**：Attention 与 Transformer · 方法细节

## 本次只学这一点

设 $h$ 个头、$d_{model}\%h==0$，则 $d_k=d_{model}/h$。

1. 用 3 个独立线性层把 $Q,K,V$ 投影到 $d_{model}$。
2. 切头：$[B,L,d_{model}]\to[B,L,h,d_k]\to[B,h,L,d_k]$（`view` + `transpose(1,2)`），让句长与每头特征维度相邻，更利于捕捉特征。
3. 每个头独立做 Scaled Dot-Product Attention，得 $[B,h,L,d_k]$。
4. 合并：`transpose(1,2).contiguous.view(B,-1,h*d_k)` 回到 $[B,L,d_{model}]$。
5. 过第 4 个线性层 $W^O$ 融合输出。

为什么要多头：单个 head 只有一种相似度度量，多个 head 相当于把表示投影到多个子空间，可同时关注不同方面（如一个头关注句法、一个头关注指代），最后综合。多头并不显著增加计算量，因为总维度固定、每头维度缩小为 $d_{model}/h$。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/08-Attention与Transformer.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Multi-Head Attention 的计算方式」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/08-Attention与Transformer.md)
