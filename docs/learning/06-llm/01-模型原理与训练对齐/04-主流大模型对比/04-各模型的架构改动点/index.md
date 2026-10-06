---
article_id: kp-3791f55989d6aa07
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-eeaa40388b15
learning_sourceId: eeaa40388b15
learning_order: 3
learning_objective: 理解并验证：各模型的架构改动点
---

# 各模型的架构改动点

> **学习目标**：能够解释「各模型的架构改动点」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer 与注意力机制（见《02-Transformer与注意力机制》）、模型参数量与显存的基本换算、量化概念。
>
> **所属主题**：-主流大模型对比 · 核心概念

## 本次只学这一点

| 模型 | 归一化 | 激活函数 | 位置编码 | 注意力 | 其它 |
|---|---|---|---|---|---|
| ChatGLM-6B | 基于 DeepNorm 的 Post-LayerNorm | GeGLU | RoPE | MHA | embedding 层梯度缩小 10 倍以稳定训练 |
| LLaMA | Pre-LayerNorm + RMSNorm | SwiGLU | RoPE | MHA | — |
| BLOOM | Pre-LayerNorm + embedding 层后加 LayerNorm | GeLU | 相对位置编码（Alibi 类，外推性更好） | MHA | 多语言训练 |
| Baichuan-7B | Pre-LayerNorm + RMSNorm | SwiGLU | RoPE | MHA | 与 LLaMA 设计一致 |
| Qwen2.5 | RMSNorm | SwiGLU | RoPE | GQA | 提升长序列处理能力、降 KV cache |
| DeepSeek-V2/V3 | RMSNorm | SwiGLU | RoPE（解耦） | **MLA** | MoE + MLA |

> ChatGLM 是唯一「血统不同」的选手：GLM 是**自回归空白填充**目标，不是标准因果语言模型，
> 因此它的 decoder 被称为 **Prefix-Decoder**（某些位置可以看到双向信息）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/03-主流大模型对比.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「各模型的架构改动点」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/03-主流大模型对比.md)
