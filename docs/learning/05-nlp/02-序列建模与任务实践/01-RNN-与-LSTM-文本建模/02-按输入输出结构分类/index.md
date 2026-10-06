---
article_id: kp-a2e28b518f954dd6
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-d7bbe1de9b00
learning_sourceId: d7bbe1de9b00
learning_order: 1
learning_objective: 理解并验证：按输入输出结构分类
---

# 按输入输出结构分类

> **学习目标**：能够解释「按输入输出结构分类」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 04 篇词向量与 `nn.Embedding`、第 05 篇文本分类流水线、PyTorch `nn.Module` 与 `Dataset/DataLoader`、链式法则与反向传播。
>
> **所属主题**：RNN 与 LSTM 文本建模 · 核心概念

## 本次只学这一点

| 结构 | 输入 | 输出 | 典型应用 |
|------|------|------|----------|
| N vs N | 长度 $N$ 的序列 | 等长序列 | 对联生成、词性标注、NER |
| N vs 1 | 长度 $N$ 的序列 | 单个值 | 文本分类、情感分析、人名国别分类 |
| 1 vs N | 单个输入 | 长度 $N$ 的序列 | 图片描述生成（image captioning） |
| N vs M | 长度 $N$ 的序列 | 长度 $M$ 的序列 | 机器翻译、文本摘要（seq2seq） |

记忆方法：看「输入和输出哪个是单值」。**N vs 1 只需要最后一个时间步的输出**；**N vs M 需要编码器-解码器（seq2seq）结构**。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/07-RNN与LSTM文本建模.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「按输入输出结构分类」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/07-RNN与LSTM文本建模.md)
