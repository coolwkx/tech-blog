---
article_id: kp-833fcf885ffd3045
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-314d719df758
learning_sourceId: 314d719df758
learning_order: 2
learning_objective: 理解并验证：两条路线
---

# 两条路线

> **学习目标**：能够解释「两条路线」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT 与 MLM（掩码语言模型）预训练目标、`[MASK]` token 的语义、`AutoModelForMaskedLM` 与 `AutoTokenizer`、HuggingFace `datasets.map(batched=True)`、PyTorch 训练循环与 `CrossEntropyLoss`。
>
> **所属主题**：项目实战笔记 06：电商评论分类（BERT+PET 与 BERT+P-Tuning） · 项目目标与业务背景

## 本次只学这一点

| | BERT + PET（硬模板） | BERT + P-Tuning（软模板） |
| --- | --- | --- |
| 模板来源 | **人工设计**自然语言模板 | **模型学习**连续向量（伪模板） |
| 模板形态 | `这是一条[MASK]评论：{textA}。` | `[unused1]..[unused6][CLS][MASK][MASK]文本[SEP]` |
| 需改模型结构吗 | 不需要，纯数据处理 | 不需要（用 `[unused]` 占位） |
| 优点 | 不引入随机初始化参数，过拟合风险低 | 模板可全局优化，能学到更优表示 |
| 缺点 | 稳定性差，不同模板准确率可差近 20 个百分点；无法全局优化 | 引入可学习参数；超多分类/蕴含类任务效果受限 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/03-文本分类系统/06-项目-电商评论分类（BERT+PET与P-Tuning）.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「两条路线」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/03-文本分类系统/06-项目-电商评论分类（BERT+PET与P-Tuning）.md)
