---
article_id: kp-50c10d96e543e8a1
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-eeaa40388b15
learning_sourceId: eeaa40388b15
learning_order: 6
learning_objective: 理解并验证：DeepSeek 系列与关键技术
---

# DeepSeek 系列与关键技术

> **学习目标**：能够解释「DeepSeek 系列与关键技术」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer 与注意力机制（见《02-Transformer与注意力机制》）、模型参数量与显存的基本换算、量化概念。
>
> **所属主题**：-主流大模型对比 · 核心概念

## 本次只学这一点

DeepSeek（深度求索）是专注大语言模型的中国 AI 实验室，总部位于杭州，以技术理想主义与开源路线著称。
梳理了从 V1 到 R1 的演进，其技术创新集中在三处：**MLA（推理省显存）、MoE 改进（训练省算力）、RL 算法（GRPO/纯 RL 提推理）**。

| 版本 | 关键点 | 效果定位 |
|---|---|---|
| DeepSeek LLM（V1） | 通用基础模型，多阶段学习率调度器（预热—稳态—分步退火），AdamW 优化器 | 中英文任务明显优于同规模 LLaMA2 |
| DeepSeek Coder | 两阶段训练：先在代码数据上预训练，再对数学相关任务做专门预训练与微调 | 代码生成与理解专精 |
| DeepSeek Math | 与 Coder 同架构，数学推理专精；RL 阶段引入 GRPO | 竞赛级基准接近 GPT-4 / Gemini 水平 |
| DeepSeek-V2 | 引入 **MLA** 与 **DeepSeekMoE**；注意力模块用 MLA 减少推理 KV cache | 显存明显降低的同时效果比 MHA/GQA 更好 |
| DeepSeek-V3 | MoE 上继续创新：**无辅助损失的负载均衡**、**多 token 预测（MTP）** | 671B 参数（37B 激活）、训练成本约 557.8 万美元（对比 LLaMA 3.1 405B 需 3080 万 GPU 小时，成本高数十倍） |
| DeepSeek-R1 | 纯强化学习 + 冷启动 + 多阶段训练 + 蒸馏 | 推理能力与 OpenAI o1 基本相当 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/03-主流大模型对比.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「DeepSeek 系列与关键技术」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/03-主流大模型对比.md)
