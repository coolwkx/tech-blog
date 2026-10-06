---
article_id: kp-c884e44948ca1046
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-b7b8e8f583cb
learning_sourceId: b7b8e8f583cb
learning_order: 9
learning_objective: 理解并验证：序列打包（packing）
---

# 序列打包（packing）

> **学习目标**：能够解释「序列打包（packing）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：因果语言模型的训练目标；tokenizer 与特殊 token（BOS/EOS/PAD）；交叉熵损失；LoRA 的注入方式（见 [03 篇](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)）与显存账本（见 [02 篇](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)）。
>
> **所属主题**：SFT 训练循环与框架 · 关键机制

## 本次只学这一点

**做法**：把多条短样本拼接成一条长度为 `max_seq_len` 的序列，用 EOS 分隔，以避免大量 padding 浪费算力。

| 维度 | 不打包 | 打包 |
| --- | --- | --- |
| 有效 token 比例 | 低（大量 pad） | 接近 100% |
| 吞吐 | 基线 | 明显更高 |
| 风险 | 无 | 跨样本注意力泄漏；loss 归一化口径变化 |
| 正确实现 | —— | 必须使用 block-diagonal attention mask（或 FlashAttention 的 varlen 接口） |

如果框架只是简单拼接而没有做 block-diagonal mask，模型会"看到"上一条样本的内容——这是数据泄漏，会让验证 loss 看起来异常低。使用前务必确认实现的注意力掩码语义。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/05-SFT训练循环与框架.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「序列打包（packing）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/05-SFT训练循环与框架.md)
