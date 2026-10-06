---
article_id: kp-8e8672b7c22e4a5c
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-3d8f081f5ed3
learning_sourceId: 3d8f081f5ed3
learning_order: 0
learning_objective: 理解并验证：LangChain 是什么
---

# LangChain 是什么

> **学习目标**：能够解释「LangChain 是什么」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的工具协议、[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的 ReAct 结构、[../llm/08-LangChain基础.md](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)。
>
> **所属主题**：-LangChain与工具编排 · 核心概念

## 本次只学这一点

LangChain 由 Harrison Chase 创建于 2022 年 10 月，是围绕 LLM 建立的一个框架。核心定位：

> LangChain 自身并不开发 LLM，它的核心理念是为各种 LLM 实现**通用的接口**，把 LLM 相关的组件「链接」在一起，简化 LLM 应用的开发难度。

| 项目 | 值 |
| --- | --- |
| 语言实现 | Python、Node.js |
| 官方文档 | https://python.langchain.com/ |
| 基础安装 | `pip install langchain langchain_community` |
| 本地模型配套 | `pip install ollama`（配合 Ollama 使用 `Ollama` / `ChatOllama` / `OllamaEmbeddings`） |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「LangChain 是什么」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md)
