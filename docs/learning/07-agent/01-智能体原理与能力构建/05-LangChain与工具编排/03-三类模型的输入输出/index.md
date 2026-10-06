---
article_id: kp-5295e86d59612f96
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-3d8f081f5ed3
learning_sourceId: 3d8f081f5ed3
learning_order: 2
learning_objective: 理解并验证：三类模型的输入输出
---

# 三类模型的输入输出

> **学习目标**：能够解释「三类模型的输入输出」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的工具协议、[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的 ReAct 结构、[../llm/08-LangChain基础.md](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)。
>
> **所属主题**：-LangChain与工具编排 · 核心概念

## 本次只学这一点

| 类型 | 输入 | 输出 | 典型用法 |
| --- | --- | --- | --- |
| LLMs | 文本字符串 | 文本字符串 | 纯文本补全 |
| Chat Models | 聊天消息（`SystemMessage` / `HumanMessage` / `AIMessage` / `ChatMessage`） | 聊天消息 | 对话应用、Agent |
| Embeddings Models | 文本（单个字符串或字符串列表） | 浮点数列表（向量） | 文本向量化、检索 |

| 消息类型 | 说明 |
| --- | --- |
| `SystemMessage` | 指定模型所处的环境和背景，如「作为一个代码专家」或「返回 json 格式」 |
| `HumanMessage` | 用户发送给 LLM 的提示信息，如「实现一个快速排序方法」 |
| `AIMessage` | AI 输出的消息，可以是针对问题的回答 |
| `ChatMessage` | 可接受任意角色的参数；大多数时候应使用上面三种 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「三类模型的输入输出」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md)
