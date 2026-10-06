---
article_id: kp-4e23627904ef1e32
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-d7bbe1de9b00
learning_sourceId: d7bbe1de9b00
learning_order: 3
learning_objective: 理解并验证：传统 RNN 的优缺点
---

# 传统 RNN 的优缺点

> **学习目标**：能够解释「传统 RNN 的优缺点」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 04 篇词向量与 `nn.Embedding`、第 05 篇文本分类流水线、PyTorch `nn.Module` 与 `Dataset/DataLoader`、链式法则与反向传播。
>
> **所属主题**：RNN 与 LSTM 文本建模 · 核心概念

## 本次只学这一点

| 优点 | 缺点 |
|------|------|
| 内部结构简单，资源消耗小 | 处理长序列时反向传播要连乘梯度，权重过大或过小都会导致**梯度爆炸或梯度消失** |
| 参数量与序列长度无关（权重共享） | 无法并行（时间步必须串行） |
| 天然能处理变长输入 | 长距离依赖实际学不好（信息被反复覆盖） |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/07-RNN与LSTM文本建模.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「传统 RNN 的优缺点」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/07-RNN与LSTM文本建模.md)
