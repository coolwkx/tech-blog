---
article_id: kp-573be5d82df129b4
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-c3d60ecbbf7d
learning_sourceId: c3d60ecbbf7d
learning_order: 3
learning_objective: 理解并验证：Q/K/V 与多头拆分的形状流转
---

# Q/K/V 与多头拆分的形状流转

> **学习目标**：能够解释「Q/K/V 与多头拆分的形状流转」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性代数（矩阵乘法、转置、reshape/transpose）；概率（softmax、期望与方差、熵）；微积分（链式法则、梯度消失）；本仓库 [Transformer 架构总览](../../../../../06-llm/01-架构与预训练/README.md)。
>
> **所属主题**：Attention 机制详解 · 核心思想

## 本次只学这一点

```text
x : [B, n, d_model] B=batch, n=序列长度, d_model=隐藏维度
 |-- x@Wq -> Q : [B,n,d_model] --|
 |-- x@Wk -> K : [B,n,d_model] --| 三者同源 => "自"注意力
 |-- x@Wv -> V : [B,n,d_model] --|
 | reshape(B,n,h,d_head).transpose(0,2,1,3) 拆头
 v
 Q,K,V : [B, h, n, d_head] h = 头数, d_head = d_model / h
 | scores = Q @ K^T / sqrt(d_head)
 v
 scores : [B, h, n, n] 每个头一张 n×n 相关度矩阵
 | causal mask: 下三角(含对角)保留, 右上角置 -inf
 v
 P = softmax(scores, axis=-1) : [B, h, n, n] 每行和 = 1
 | ctx = P @ V
 v
 ctx : [B, h, n, d_head]
 | transpose(0,2,1,3).reshape(B, n, h*d_head) 拼头, h*d_head == d_model
 v
 ctx : [B, n, d_model] --@Wo--> out : [B, n, d_model] 输出投影融合各头
```

**记住三个形状就能读懂所有注意力代码**：

| 张量 | 形状 | 含义 |
| --- | --- | --- |
| $Q,K,V$ | `[B, h, n, d_head]` | 拆头后，每个头独立算注意力 |
| scores / $P$ | `[B, h, n, n]` | 每个头一张 $n\times n$ 矩阵，**显存杀手** |
| out | `[B, n, d_model]` | 拼接并投影回输入维度，可残差相加 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/01-Attention机制详解.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Q/K/V 与多头拆分的形状流转」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/01-Attention机制详解.md)
