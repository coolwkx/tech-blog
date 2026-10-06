---
article_id: kp-d474c226b0d30423
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-cbc77f3ab05c
learning_sourceId: cbc77f3ab05c
learning_order: 3
learning_objective: 理解并验证：掩码（mask）与注意力类型
---

# 掩码（mask）与注意力类型

> **学习目标**：能够解释「掩码（mask）与注意力类型」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 07 篇 RNN / LSTM / seq2seq、PyTorch 的 `nn.Linear` 与张量 `view/transpose/matmul`、softmax 与交叉熵。
>
> **所属主题**：Attention 与 Transformer · 核心概念

## 本次只学这一点

| 掩码类型 | 防的问题 | 使用位置 |
|------|----------|----------|
| Padding Mask | 补齐用的 PAD 参与注意力，稀释真实信息 | Encoder/Decoder 的 self-attention 与 cross-attention |
| Sequence / Look-ahead Mask | 解码时提前看到未来 token，训练与预测行为不一致 | 仅 Decoder 的 self-attention |

约定：mask 由 0/1 组成，用 `masked_fill(mask == 0, -1e9)` 把被掩位置的分数压成负无穷，softmax 后权重归零；目标端两种 mask 要**按位与**合并。

按 $Q,K,V$ 的来源区分三种注意力，这是最容易混的地方：

| | Q | K | V | mask |
|---|---|---|---|---|
| Encoder self-attention | Encoder 上一层输出 | 同 Q | 同 Q | 仅 padding mask |
| Decoder masked self-attention | Decoder 上一层输出 | 同 Q | 同 Q | padding + look-ahead |
| Decoder cross-attention | Decoder 上一层输出 | Encoder 输出 memory | 同 K | 仅 source padding mask |

一句话：self-attention 是 $Q=K=V$，cross-attention 是 $Q\neq K=V$。cross-attention 是编码器信息流向解码器的唯一通道，取代了 seq2seq 中固定长度的 context vector，因此无需 look-ahead mask——目标端尚未生成的部分与源端无关，源端信息整体可见。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/08-Attention与Transformer.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「掩码（mask）与注意力类型」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/08-Attention与Transformer.md)
