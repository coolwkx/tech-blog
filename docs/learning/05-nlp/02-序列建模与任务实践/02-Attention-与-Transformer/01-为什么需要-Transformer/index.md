---
article_id: kp-616ba15f7ca1dcd5
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-cbc77f3ab05c
learning_sourceId: cbc77f3ab05c
learning_order: 0
learning_objective: 理解并验证：为什么需要 Transformer
---

# 为什么需要 Transformer

> **学习目标**：能够解释「为什么需要 Transformer」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 07 篇 RNN / LSTM / seq2seq、PyTorch 的 `nn.Linear` 与张量 `view/transpose/matmul`、softmax 与交叉熵。
>
> **所属主题**：Attention 与 Transformer · 核心概念

## 本次只学这一点

2017 年 Transformer 被提出，2018 年 BERT 让它成为主流。它的两大优势正是 seq2seq + RNN 两大缺陷的对症药：

| seq2seq（RNN 版）的缺陷 | 后果 | Transformer 的改进 |
|---|---|---|
| Encoder 把整个源句压缩成一个固定长度向量 | 长句信息严重损耗 | Multi-Head Attention 让解码器直接看到编码器每个位置，不再依赖单一向量 |
| 时间步必须串行递归 | 训练慢，长序列尤其慢 | Encoder 端可完全并行（矩阵运算一次算完所有时间步） |

「并行」有两个层次：**结构层面** Encoder 可并行、Decoder 只在训练时并行（预测时第 $t$ 步依赖第 $t-1$ 步输出，天然串行）；**算子实现层面** self-attention 通过矩阵乘法一次算完所有 token，但 token 之间仍有计算依赖，并非各 token 独立。Embedding、Feed Forward、Add & Norm 都是逐位置独立的，可完全并行。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/08-Attention与Transformer.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「为什么需要 Transformer」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/08-Attention与Transformer.md)
