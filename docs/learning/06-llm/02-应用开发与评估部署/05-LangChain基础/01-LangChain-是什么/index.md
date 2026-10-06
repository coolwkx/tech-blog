---
article_id: kp-cd8de2cdb0afe597
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-1043063b962d
learning_sourceId: 1043063b962d
learning_order: 0
learning_objective: 理解并验证：LangChain 是什么
---

# LangChain 是什么

> **学习目标**：能够解释「LangChain 是什么」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：大模型 API 与消息角色（见《05-大模型API与调用实践》）、embedding 与向量检索（见《07-向量数据库与Milvus》）。
>
> **所属主题**：-LangChain基础 · 核心概念

## 本次只学这一点

| 项 | 说明 |
|---|---|
| 创建者与时间 | Harrison Chase 创建于 2022 年 10 月 |
| 定位 | 围绕 LLM 建立的**应用开发框架** |
| 语言实现 | 目前有 **Python** 和 **Node.js** 两个版本 |
| 核心理念 | 自身**不开发 LLM**，而是为各种 LLM 实现**通用接口**，把相关组件「链接」起来，降低开发难度 |

一句话类比：**LangChain 之于 LLM，类似 JDBC 之于数据库**——屏蔽不同厂商差异，让上层应用用统一方式调用、编排与扩展。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「LangChain 是什么」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)
