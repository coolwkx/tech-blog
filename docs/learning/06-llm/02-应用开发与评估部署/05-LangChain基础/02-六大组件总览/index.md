---
article_id: kp-4fda241daf3aed93
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-1043063b962d
learning_sourceId: 1043063b962d
learning_order: 1
learning_objective: 理解并验证：六大组件总览
---

# 六大组件总览

> **学习目标**：能够解释「六大组件总览」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：大模型 API 与消息角色（见《05-大模型API与调用实践》）、embedding 与向量检索（见《07-向量数据库与Milvus》）。
>
> **所属主题**：-LangChain基础 · 核心概念

## 本次只学这一点

| 组件 | 职责 | 典型类 | 解决什么问题 |
|---|---|---|---|
| Models | 各类模型与集成的统一封装 | `Ollama`、`ChatOllama`、`OllamaEmbeddings` | 不同厂商 API 不一致 |
| Prompts | 提示管理、优化、序列化 | `PromptTemplate`、`FewShotPromptTemplate` | 提示是散落字符串、难复用 |
| Chains | 一系列组件调用的编排 | `LLMChain`、LCEL | 单次调用不够，需多步串联 |
| Memory | 保存与模型交互的上下文状态 | `ChatMessageHistory` | 大模型**本身不保存上次交互内容** |
| Indexes | 结构化文档以便与模型交互 | `TextLoader`、`TextSplitter`、`VectorStore`、`Retriever` | 模型不知道你的私有文档 |
| Agents | 决定采取哪些行动、执行并观察直到完成 | `AgentType`、`Tool`、`AgentExecutor` | 模型不会查实时信息、算数不可靠 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「六大组件总览」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)
