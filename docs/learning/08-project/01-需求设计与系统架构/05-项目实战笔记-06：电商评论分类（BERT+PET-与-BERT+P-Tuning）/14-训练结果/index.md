---
article_id: kp-1b1f70d872afc5e3
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-314d719df758
learning_sourceId: 314d719df758
learning_order: 14
learning_objective: 理解并验证：训练结果
---

# 训练结果

> **学习目标**：能够解释「训练结果」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT 与 MLM（掩码语言模型）预训练目标、`[MASK]` token 的语义、`AutoModelForMaskedLM` 与 `AutoTokenizer`、HuggingFace `datasets.map(batched=True)`、PyTorch 训练循环与 `CrossEntropyLoss`。
>
> **所属主题**：项目实战笔记 06：电商评论分类（BERT+PET 与 BERT+P-Tuning） · 核心实现

## 本次只学这一点

```text
global step 40, epoch: 4, loss: 0.62105, speed: 1.27 step/s
global step 60, epoch: 7, loss: 0.41744, speed: 1.23 step/s
global step 390, epoch: 48, loss: 0.06674, speed: 1.20 step/s
global step 400, epoch: 49, loss: 0.06507, speed: 1.21 step/s

Evaluation precision: 0.78000, recall: 0.76000, F1: 0.75000
```

**仅用 63 条训练样本，在 590 条验证集上精确率约 78%**，而传统 Fine-tuning 在 63 条样本上通常拿不到这个水平。想再提升，最直接的手段是**扩增样本**。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/03-文本分类系统/06-项目-电商评论分类（BERT+PET与P-Tuning）.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「训练结果」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/03-文本分类系统/06-项目-电商评论分类（BERT+PET与P-Tuning）.md)
