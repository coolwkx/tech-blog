---
article_id: kp-4cee7db265f31cda
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-3d8f081f5ed3
learning_sourceId: 3d8f081f5ed3
learning_order: 7
learning_objective: 理解并验证：Chain 的两种基本形态
---

# Chain 的两种基本形态

> **学习目标**：能够解释「Chain 的两种基本形态」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的工具协议、[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的 ReAct 结构、[../llm/08-LangChain基础.md](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)。
>
> **所属主题**：-LangChain与工具编排 · 关键机制

## 本次只学这一点

| 形态 | 作用 | 示例 |
| --- | --- | --- |
| `LLMChain(llm=..., prompt=...)` | 把提示模板与模型绑定，`chain.run("王")` 直接执行 | 起名示例 |
| `SimpleSequentialChain(chains=[chain1, chain2], verbose=True)` | 把上一条链的输出直接作为下一条链的输入，只需传入第一个参数 | 起名 → 起小名 |

`SimpleSequentialChain` 的价值在于省掉了手工接线：`catchphrase = overall_chain.run("王")` 一句就能跑完整条流水线。

> **说明**：本小节超出本节范围，为通用知识补充。新版 LangChain 已用 LCEL（`prompt | model | parser`）取代 `LLMChain`，`SimpleSequentialChain` 也对应 `RunnableSequence`。概念上不变：链是「把组件按数据流串起来」，`|` 是更简洁的写法。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Chain 的两种基本形态」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md)
