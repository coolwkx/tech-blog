---
article_id: kp-16e8707c8620b3fb
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-94a81d666c0a
learning_sourceId: 94a81d666c0a
learning_order: 5
learning_objective: 理解并验证：预训练任务一：Masked LM（MLM）
---

# 预训练任务一：Masked LM（MLM）

> **学习目标**：能够解释「预训练任务一：Masked LM（MLM）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 08 篇的 Transformer Encoder 与 self-attention、第 04 篇的静态词向量局限、Python 类与 PyTorch 训练循环。
>
> **所属主题**：BERT 与预训练模型 · 方法细节

## 本次只学这一点

传统语言模型是 left-to-right（或左右拼接），提取特征能力有限。BERT 提出深度双向表示，用 MASK 任务训练：

1. 在原始文本中**随机抽取 15% 的 token** 作为预测对象；
2. 在这些被选中的 token 中，按三种方式生成输入：
 - **80%** 概率替换为 `[MASK]`：`my dog is hairy` → `my dog is [MASK]`
 - **10%** 概率替换为一个随机词：`my dog is hairy` → `my dog is apple`
 - **10%** 概率保持不变：`my dog is hairy` → `my dog is hairy`
3. 模型在**不知道哪些位置被改过、哪些是原词**的情况下预测原词，被迫学习分布式上下文语义。

**为什么是 80/10/10**（三条理由要能背）：

| 比例 | 作用 |
|------|------|
| 若 100% 用 `[MASK]` | 微调时不存在 `[MASK]`，模型从未接触过这些 token 本身的信息，整个语义空间损失部分信息 |
| 10% 随机词 | 防止模型「偷懒」直接照抄当前 token；逼它学习周边语义与远距离依赖 |
| 10% 保留原词 | 保留语言本来的面貌，让信息不至于被完全遮掩，模型能「看清」真实语言 |

同时因为原文本中只有 15% 的 token 参与 MASK，并不会破坏原语言的表达能力和语言规则。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「预训练任务一：Masked LM（MLM）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)
