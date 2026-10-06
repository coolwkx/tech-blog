---
article_id: kp-f5cb375367d3a6f1
learning_kind: article
learning_category: 08-project
learning_direction: practice
learning_topic: topic-314d719df758
learning_sourceId: 314d719df758
learning_order: 7
learning_objective: 理解并验证：为什么 PET 能小样本奏效：三个理由
---

# 为什么 PET 能小样本奏效：三个理由

> **学习目标**：能够解释「为什么 PET 能小样本奏效：三个理由」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT 与 MLM（掩码语言模型）预训练目标、`[MASK]` token 的语义、`AutoModelForMaskedLM` 与 `AutoTokenizer`、HuggingFace `datasets.map(batched=True)`、PyTorch 训练循环与 `CrossEntropyLoss`。
>
> **所属主题**：项目实战笔记 06：电商评论分类（BERT+PET 与 BERT+P-Tuning） · 关键技术选型与理由

## 本次只学这一点

1. **不引入随机初始化参数。** `BertForSequenceClassification` 会新增 `Linear(768, 10)` 分类头，63 条样本根本训不好它；PET 直接用已在海量文本上训好的 MLM 头。
2. **把分类任务对齐到预训练目标（task alignment）。** BERT 预训练就是在"预测 `[MASK]`"，PET 让它继续做同一件事，只换了输入的位置。
3. **标签词映射提供了先验。** 告诉模型"要预测的是一个表示类别的词"，比让它从零学"第 3 号类是什么"信息量大得多。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/03-文本分类系统/06-项目-电商评论分类（BERT+PET与P-Tuning）.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「为什么 PET 能小样本奏效：三个理由」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/03-文本分类系统/06-项目-电商评论分类（BERT+PET与P-Tuning）.md)
