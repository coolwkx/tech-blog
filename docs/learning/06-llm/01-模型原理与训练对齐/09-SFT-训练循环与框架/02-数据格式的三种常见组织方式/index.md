---
article_id: kp-5d29f4d15a3cbb7c
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-b7b8e8f583cb
learning_sourceId: b7b8e8f583cb
learning_order: 1
learning_objective: 理解并验证：数据格式的三种常见组织方式
---

# 数据格式的三种常见组织方式

> **学习目标**：能够解释「数据格式的三种常见组织方式」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：因果语言模型的训练目标；tokenizer 与特殊 token（BOS/EOS/PAD）；交叉熵损失；LoRA 的注入方式（见 [03 篇](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)）与显存账本（见 [02 篇](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)）。
>
> **所属主题**：SFT 训练循环与框架 · 核心概念

## 本次只学这一点

| 格式 | 结构 | 优点 | 缺点 |
| --- | --- | --- | --- |
| Alpaca 式 | `{"instruction": ..., "input": ..., "output": ...}` | 简单直观，单轮任务友好 | 多轮对话表达力弱 |
| ShareGPT / messages 式 | `{"messages": [{"role": "system"/"user"/"assistant", "content": ...}, ...]}` | 原生支持多轮、角色、工具调用 | 需要正确的 chat template |
| 纯文本续写式 | `{"text": "..."}` | 不需要模板 | **无法做 assistant-only 掩码**，会把 prompt 也学进去 |

**推荐**：只要基座有官方 chat template，就用 messages 式，并让 tokenizer 负责拼接。手写字符串拼接是最常见的 bug 来源（漏掉 `<|im_start|>`、多一个空格、少一个 `<|eot_id|>`）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/05-SFT训练循环与框架.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「数据格式的三种常见组织方式」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/05-SFT训练循环与框架.md)
