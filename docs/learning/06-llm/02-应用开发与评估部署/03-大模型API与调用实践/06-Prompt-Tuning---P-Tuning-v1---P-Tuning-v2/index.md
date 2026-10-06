---
article_id: kp-a3eb62084075acfb
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-563344f304a7
learning_sourceId: 563344f304a7
learning_order: 5
learning_objective: 理解并验证：Prompt Tuning / P-Tuning v1 / P-Tuning v2
---

# Prompt Tuning / P-Tuning v1 / P-Tuning v2

> **学习目标**：能够解释「Prompt Tuning / P-Tuning v1 / P-Tuning v2」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT 与 MLM 预训练目标（见《02-Transformer与注意力机制》）、Python 与 HTTP 基础、PyTorch 训练循环。
>
> **所属主题**：-大模型API与调用实践 · 关键机制

## 本次只学这一点

**Prompt Tuning**（Google，2021，《The Power of Scale for Parameter-Efficient Prompt Tuning》，
基于 T5，最大 11B）：为每一个输入文本假设一个**固定前缀提示**，该提示由神经网络参数化，
并在下游任务微调时更新，**大模型参数被冻结**。

| 优点 | 缺点 |
|---|---|
| 大模型的微调新范式；小样本学习场景表现好；可固定大模型参数只调少量附加参数适配下游任务 | 模型参数规模大了之后可解释性不太行；收敛速度较慢；调参比较复杂 |

特点总结：**适配性能基本与全参数微调相当**。

**P-Tuning v1**（清华，2022，《GPT Understands, Too》，面向 NLU）：提出动机是
「大模型的 prompt 构造方式严重影响下游任务的效果」，因此**把 prompt 转换为可以学习的 Embedding 参数进行优化**。
做法：**固定 LLM 参数**，用 MLP + LSTM 对 prompt embedding 进行编码，编码后与其他向量拼接再正常输入 LLM。
训练后**只保留 prompt 编码之后的向量**即可，无需保留编码器。

直接优化 embedding 参数存在两个挑战：

| 挑战 | 含义 | 解法 |
|---|---|---|
| Discreteness（不连续性） | 输入正常语料的 embedding 已经过预训练，而直接对 prompt embedding 随机初始化训练，容易陷入局部最优 | 用 LSTM + MLP 重参数化，把可学习参数映射为连续 embedding |
| Association（关联性） | 无法捕捉 prompt embedding 之间的相关关系 | 同上，用序列模型建模 token 间依赖 |

**P-Tuning v1 与 Prompt Tuning 的区别**：

| 对比项 | Prompt Tuning | P-Tuning |
|---|---|---|
| 位置 | 额外 embedding 加在**开头**，更像模仿 Instruction | 添加位置**不固定** |
| 是否需额外网络初始化 | 不需要 MLP | 通过 LSTM + MLP 来做初始化 |

**P-Tuning v2**（《P-Tuning v2: Prompt Tuning Can Be Comparable to Fine-tuning Universally Across Scales and Tasks》）：
核心思想是**在模型的每一层都应用连续的 prompt**，并对 prompt 参数进行更新优化，
主要解决 P-Tuning v1 **在小参数量模型上表现差**的问题，同时针对 NLU 任务优化适配。
训练后同样只保留 prompt 编码后的向量，无需保留编码器。

> 一句话记忆三者差异：**Prompt Tuning 只在输入层加前缀；P-Tuning v1 用 LSTM+MLP 把可学习参数映射成连续 embedding
> 且位置灵活；P-Tuning v2 把前缀加到每一层**，因此小模型上也能逼近全量微调。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/06-提示工程/05-大模型API与调用实践.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Prompt Tuning / P-Tuning v1 / P-Tuning v2」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/06-提示工程/05-大模型API与调用实践.md)
