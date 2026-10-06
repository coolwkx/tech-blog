---
article_id: kp-31084041980721ef
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-b7b8e8f583cb
learning_sourceId: b7b8e8f583cb
learning_order: 3
learning_objective: 理解并验证：训练框架的取舍
---

# 训练框架的取舍

> **学习目标**：能够解释「训练框架的取舍」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：因果语言模型的训练目标；tokenizer 与特殊 token（BOS/EOS/PAD）；交叉熵损失；LoRA 的注入方式（见 [03 篇](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)）与显存账本（见 [02 篇](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)）。
>
> **所属主题**：SFT 训练循环与框架 · 核心概念

## 本次只学这一点

| 方案 | 定位 | 优点 | 代价 |
| --- | --- | --- | --- |
| 手写 PyTorch 循环 | 完全可控 | 每行都可解释，便于 debug 与自定义 loss | 要自己处理 AMP、梯度累积、分布式、checkpoint |
| `transformers.Trainer` | 通用训练器 | 开箱即用，支持 AMP、累积、断点续训 | 数据侧仍要自己写 collator 与 masking |
| `trl.SFTTrainer` | 为 SFT 定制 | 内置 packing、chat template、assistant-only loss 掩码 | 抽象层多，出问题时要读源码 |
| `axolotl` / `LLaMA-Factory` | 配置驱动的一站式方案 | YAML 配置即训，支持大量模型与技巧 | 自由度受限，隐藏细节多 |
| `deepspeed` + 上述任一 | 大模型分布式 | ZeRO-3/offload，支撑 70B 级 | 配置复杂，调试成本高 |

建议路径：**先用 `Trainer` + 手写 masking 跑通一次（理解机制），再切到 `SFTTrainer` 或配置驱动框架提高效率。**

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/05-SFT训练循环与框架.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「训练框架的取舍」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/05-SFT训练循环与框架.md)
