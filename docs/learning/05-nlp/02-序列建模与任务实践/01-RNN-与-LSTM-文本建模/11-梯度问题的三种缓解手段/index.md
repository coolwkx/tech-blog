---
article_id: kp-db413f8e6612ec2c
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-d7bbe1de9b00
learning_sourceId: d7bbe1de9b00
learning_order: 10
learning_objective: 理解并验证：梯度问题的三种缓解手段
---

# 梯度问题的三种缓解手段

> **学习目标**：能够解释「梯度问题的三种缓解手段」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 04 篇词向量与 `nn.Embedding`、第 05 篇文本分类流水线、PyTorch `nn.Module` 与 `Dataset/DataLoader`、链式法则与反向传播。
>
> **所属主题**：RNN 与 LSTM 文本建模 · 方法细节

## 本次只学这一点

| 手段 | 做法 | 解决的 | 局限 |
|------|------|--------|------|
| 梯度裁剪 | `torch.nn.utils.clip_grad_norm_(params, max_norm=5)` | 梯度爆炸 | 对梯度消失无效 |
| 门控结构 | 换 LSTM / GRU | 梯度消失（长依赖） | 仍无法并行 |
| 残差 / 跳跃连接 | 把浅层表示加到深层 | 深度方向的退化 | 时间方向的依赖仍需门控 |
| 正交初始化 | 用正交矩阵初始化 $W_{hh}$ | 减缓谱半径偏离 1 | 只是初始化层面的缓解 |

工程实践：**梯度裁剪几乎是 RNN 训练的标配**，一行代码，代价可忽略。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/07-RNN与LSTM文本建模.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「梯度问题的三种缓解手段」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/07-RNN与LSTM文本建模.md)
