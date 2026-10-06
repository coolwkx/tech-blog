---
article_id: kp-3f6a3c2377b5b93f
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-314d719df758
learning_sourceId: 314d719df758
learning_order: 1
learning_objective: 理解并验证：真正的难点：样本极少
---

# 真正的难点：样本极少

> **学习目标**：能够解释「真正的难点：样本极少」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT 与 MLM（掩码语言模型）预训练目标、`[MASK]` token 的语义、`AutoModelForMaskedLM` 与 `AutoTokenizer`、HuggingFace `datasets.map(batched=True)`、PyTorch 训练循环与 `CrossEntropyLoss`。
>
> **所属主题**：项目实战笔记 06：电商评论分类（BERT+PET 与 BERT+P-Tuning） · 项目目标与业务背景

## 本次只学这一点

```text
train.txt 63 条 ← 训练集只有 63 条！
dev.txt 590 条 ← 验证集
```

**63 条样本训 110M 参数的 BERT**，传统 Fine-tuning 必然过拟合。这就是引入 Prompt-Tuning 的根本原因：

> 在很多实际场景中，由于领域特殊性和标注成本高，导致标注训练数据缺乏，模型无法有效学习参数，从而易出现过拟合现象。因此，如何通过小样本数据训练得到一个性能较好的分类模型，是目前的研究热点。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/03-文本分类系统/06-项目-电商评论分类（BERT+PET与P-Tuning）.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「真正的难点：样本极少」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/03-文本分类系统/06-项目-电商评论分类（BERT+PET与P-Tuning）.md)
