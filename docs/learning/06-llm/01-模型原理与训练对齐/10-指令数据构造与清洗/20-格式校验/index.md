---
article_id: kp-3753acacab3e8582
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-272ce9acf0c8
learning_sourceId: 272ce9acf0c8
learning_order: 19
learning_objective: 理解并验证：格式校验
---

# 格式校验

> **学习目标**：能够解释「格式校验」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT/MLM 预训练目标、Tokenizer 与词表（vocab）、`[MASK]` token 与 MLM Head、交叉熵损失、基本的分类任务指标（acc / P / R / F1）。
>
> **所属主题**：-指令数据构造与清洗 · 数据清洗清单

## 本次只学这一点

格式问题不会让训练崩，但会让模型学会「输出脏格式」。必须校验的项：字段完整性（`instruction` / `input` / `output` 是否齐全）、多轮对话的角色是否 `user → assistant` 交替、是否残留未转义的模板占位符（`{textA}`、`{MASK}`、`<|im_start|>`）、HTML 标签与未闭合的 markdown 代码块、以及输出里混入的思维链草稿（`好的，让我想想…`）——如果训练时没有对应的格式约定，这些草稿会被模型当成规范学走。校验函数见 5.7 的 `validate_dialogue`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/06-指令数据构造与清洗.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「格式校验」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/06-指令数据构造与清洗.md)
