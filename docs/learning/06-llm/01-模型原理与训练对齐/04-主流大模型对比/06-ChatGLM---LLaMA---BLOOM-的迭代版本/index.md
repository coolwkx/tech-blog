---
article_id: kp-eebfa0ce04b24092
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-eeaa40388b15
learning_sourceId: eeaa40388b15
learning_order: 5
learning_objective: 理解并验证：ChatGLM / LLaMA / BLOOM 的迭代版本
---

# ChatGLM / LLaMA / BLOOM 的迭代版本

> **学习目标**：能够解释「ChatGLM / LLaMA / BLOOM 的迭代版本」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer 与注意力机制（见《02-Transformer与注意力机制》）、模型参数量与显存的基本换算、量化概念。
>
> **所属主题**：-主流大模型对比 · 核心概念

## 本次只学这一点

| 模型 | 版本 | 关键变化 |
|---|---|---|
| ChatGLM | ChatGLM2-6B | 上下文 2K → 32K；引入 Multi-Query Attention 提升推理速度；数学任务性能提升 571%（相对第一代）；多轮对话能力增强 |
| ChatGLM | ChatGLM3-6B | 多模态理解（10 余个国际标准图文评测 SOTA）、代码增强模块、网络搜索增强 |
| LLaMA | LLaMA2 | 架构同 LLaMA；上下文 2048 → 4096；训练数据多 40%；新增对话版本（SFT + RLHF 的安全对齐） |
| LLaMA | LLaMA3 | 词表 32K → **128K**；8B/70B 均采用 **GQA** 提升推理效率；预训练数据超 **15T** token（比 Llama 2 大 7 倍）；覆盖 30 多种非英语语言 |
| BLOOM | BLOOMZ | 在 BLOOM-176B 基础上用 ChatGPT 生产的数据做指令微调；衍生金融领域模型（轩辕） |

**LLaMA 的中文短板**：训练语料以英文为主，使用 BPE 分词器、词表仅 32000，中文 token 极少（只有几百个），
一个汉字常被切成多个 token，编码效率低、模型学习困难。常见补救做法：在中文语料上用 SentencePiece
训练一个中文 tokenizer（约 20000 个中文词），再与原始 LLaMA tokenizer 合并词表，得到
**Chinese-LLaMA**（词表 49953）。Baichuan 直接把词表扩到 64000 以规避这个问题。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/03-主流大模型对比.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「ChatGLM / LLaMA / BLOOM 的迭代版本」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/03-主流大模型对比.md)
