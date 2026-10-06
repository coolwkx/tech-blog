---
article_id: kp-fb46c5c453919efe
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-eeaa40388b15
learning_sourceId: eeaa40388b15
learning_order: 0
learning_objective: 理解并验证：为什么开源模型「看起来都一样」
---

# 为什么开源模型「看起来都一样」

> **学习目标**：能够解释「为什么开源模型「看起来都一样」」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer 与注意力机制（见《02-Transformer与注意力机制》）、模型参数量与显存的基本换算、量化概念。
>
> **所属主题**：-主流大模型对比 · 核心概念

## 本次只学这一点

ChatGPT 爆火后，国内外近百款大模型发布。开源阵营可以按「血统」分为两条线：

| 家族 | 机构 | 基座架构 | 衍生模型 |
|---|---|---|---|
| LLaMA | Meta AI | decoder-only | Alpaca、Vicuna、BELLE、Phoenix、Chinese-LLaMA、Baichuan（部分借鉴） |
| ChatGLM | 清华大学 | GLM（Prefix-Decoder） | ChatGLM2-6B、ChatGLM3-6B |
| BLOOM | Hugging Face | decoder-only | BLOOMZ、BELLE、Phoenix |
| Baichuan | 百川智能 | decoder-only | Baichuan2-13B、（金融）轩辕 |
| Qwen | 阿里巴巴 | decoder-only | Qwen1.5、Qwen2、Qwen2.5 |

**架构趋同的原因**：LLaMA 证明了「decoder-only + Pre-LayerNorm/RMSNorm + SwiGLU + RoPE」这套组合在训练稳定性、
推理效率与效果上最均衡，后续模型基本沿用并只做局部替换（例如把 MHA 换成 GQA 来省 KV cache）。
**差异因此转移到了数据侧**：训练语料配比、词表大小与分词效率、指令微调/对齐数据质量。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/03-主流大模型对比.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「为什么开源模型「看起来都一样」」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/03-主流大模型对比.md)
