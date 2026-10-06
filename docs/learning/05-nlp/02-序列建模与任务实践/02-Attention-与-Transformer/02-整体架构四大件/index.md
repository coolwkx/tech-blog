---
article_id: kp-1963a6f7af2acd62
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-cbc77f3ab05c
learning_sourceId: cbc77f3ab05c
learning_order: 1
learning_objective: 理解并验证：整体架构四大件
---

# 整体架构四大件

> **学习目标**：能够解释「整体架构四大件」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 07 篇 RNN / LSTM / seq2seq、PyTorch 的 `nn.Linear` 与张量 `view/transpose/matmul`、softmax 与交叉熵。
>
> **所属主题**：Attention 与 Transformer · 核心概念

## 本次只学这一点

| 部分 | 组成 | 作用 |
|------|------|------|
| 输入部分 | Word Embedding + Positional Encoding | 把 token 变成向量并注入位置信息 |
| 编码器部分 | $N$ 个 Encoder Layer 堆叠 | 每层 2 个子层：多头自注意力、前馈全连接 |
| 解码器部分 | $N$ 个 Decoder Layer 堆叠 | 每层 3 个子层：掩码多头自注意力、Encoder-Decoder 注意力、前馈全连接 |
| 输出部分 | Linear + softmax（实现上用 `log_softmax`） | 把 $d_{model}$ 维隐状态映射到词表维度 |

论文 base 配置：$N=6$、$d_{model}=512$、$d_{ff}=2048$、$head=8$、$dropout=0.1$。注意 $d_{ff}=4\times d_{model}$ 是经验上的 4 倍关系。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/08-Attention与Transformer.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「整体架构四大件」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/08-Attention与Transformer.md)
