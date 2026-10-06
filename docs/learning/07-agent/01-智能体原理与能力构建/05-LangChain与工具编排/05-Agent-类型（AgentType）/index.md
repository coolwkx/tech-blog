---
article_id: kp-c7afd99878574949
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-3d8f081f5ed3
learning_sourceId: 3d8f081f5ed3
learning_order: 4
learning_objective: 理解并验证：Agent 类型（AgentType）
---

# Agent 类型（AgentType）

> **学习目标**：能够解释「Agent 类型（AgentType）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的工具协议、[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的 ReAct 结构、[../llm/08-LangChain基础.md](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)。
>
> **所属主题**：-LangChain与工具编排 · 核心概念

## 本次只学这一点

点名了三种（LangChain 实际提供的类型更多）：

| 类型 | 工具选择依据 | 输入形态 | 适用场景 |
| --- | --- | --- | --- |
| `zero-shot-react-description` | 利用 ReAct 框架，**单纯依靠工具的描述信息**选择工具，可使用多个工具 | 单一字符串 | 通用、无历史的多工具任务 |
| `structured-chat-zero-shot-react-description` | 同上，但可通过工具的**参数 schema** 构造结构化的动作输入 | 结构化 | 参数复杂的工具调用 |
| `conversational-react-description` | ReAct + **记忆功能保存对话历史** | 对话 | 多轮对话中调用工具 |

三者的递进关系是：`zero-shot-react-description` 是基线；`structured-chat-*` 解决「参数怎么传」；`conversational-*` 解决「对话上下文怎么带」。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Agent 类型（AgentType）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md)
