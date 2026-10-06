---
article_id: kp-aefb2c6ad06ab891
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-cbc77f3ab05c
learning_sourceId: cbc77f3ab05c
learning_order: 2
learning_objective: 理解并验证：每个子模块的职责
---

# 每个子模块的职责

> **学习目标**：能够解释「每个子模块的职责」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 07 篇 RNN / LSTM / seq2seq、PyTorch 的 `nn.Linear` 与张量 `view/transpose/matmul`、softmax 与交叉熵。
>
> **所属主题**：Attention 与 Transformer · 核心概念

## 本次只学这一点

| 子模块 | 位置 | 关键点 |
|--------|------|--------|
| Scaled Dot-Product Attention | Encoder / Decoder 内部 | $Q=K=V$ 时是 self-attention；$Q\neq K=V$ 时是 cross-attention |
| Multi-Head Attention | 同上 | 把 $d_{model}$ 切成 $h$ 份并行做 attention 再 concat，多个子空间关注不同信息 |
| Feed Forward | 每个 Block 内 | 两个线性层夹一个 ReLU，$d_{model}\to d_{ff}\to d_{model}$，增强拟合能力 |
| Add & Norm | 每个子层之后 | Add = 残差连接（信息无损耗地传得更深）；Norm = LayerNorm（防参数过大过小、收敛变慢） |
| Positional Encoding | 输入部分 | 三角函数计算，周期函数不受长度限制，值域 $[-1,1]$ 有助于梯度计算 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/08-Attention与Transformer.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「每个子模块的职责」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/08-Attention与Transformer.md)
