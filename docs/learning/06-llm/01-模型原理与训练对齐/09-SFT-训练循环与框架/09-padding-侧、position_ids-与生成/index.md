---
article_id: kp-88a6f2aad26d09d4
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-b7b8e8f583cb
learning_sourceId: b7b8e8f583cb
learning_order: 8
learning_objective: 理解并验证：padding 侧、position_ids 与生成
---

# padding 侧、position_ids 与生成

> **学习目标**：能够解释「padding 侧、position_ids 与生成」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：因果语言模型的训练目标；tokenizer 与特殊 token（BOS/EOS/PAD）；交叉熵损失；LoRA 的注入方式（见 [03 篇](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)）与显存账本（见 [02 篇](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)）。
>
> **所属主题**：SFT 训练循环与框架 · 关键机制

## 本次只学这一点

| 问题 | 训练时 | 推理时 |
| --- | --- | --- |
| padding 放在哪一侧 | 训练必须**右侧** padding（配合 causal mask 才正确）；左 padding 在训练中会让位置对齐出错 | 生成时必须**左侧** padding（否则不同长度样本的生成起点不一致） |
| attention mask | 必须以 `attention_mask` 明确告知 padding 位置，不能只靠 `input_ids` | 同左 |
| labels 的 pad 位 | 必须是 `-100` | 不适用 |

在 `transformers` 中，`DataCollatorForSeq2Seq` / `DataCollatorForLanguageModeling` 默认做右侧 padding；而 `tokenizer.padding_side = "left"` 是很多生成式推理示例的默认设置。**同一个 tokenizer 在训练与推理之间切换 padding 侧时，最容易出问题。**

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/05-SFT训练循环与框架.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「padding 侧、position_ids 与生成」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/05-SFT训练循环与框架.md)
