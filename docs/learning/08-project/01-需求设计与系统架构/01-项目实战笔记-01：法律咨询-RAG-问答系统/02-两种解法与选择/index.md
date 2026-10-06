---
article_id: kp-8ef3da9d4df8b598
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-e94c0577cb2f
learning_sourceId: e94c0577cb2f
learning_order: 1
learning_objective: 理解并验证：两种解法与选择
---

# 两种解法与选择

> **学习目标**：能够解释「两种解法与选择」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 工程化基础、向量检索原理（Embedding / 余弦相似度 / ANN）、LangChain 的 Document 与 TextSplitter 抽象、FastAPI 基础、MySQL 与 Redis 基本操作。
>
> **所属主题**：项目实战笔记 01：法律咨询 RAG 问答系统 · 项目目标与业务背景

## 本次只学这一点

| 路线 | 做法 | 本项目取舍 |
| --- | --- | --- |
| 垂直领域微调 | 把企业知识灌进模型权重 | 成本高、知识更新要重训，**放弃** |
| RAG | 知识放外部库，检索后再生成 | 知识可热更新、可溯源、可解释，**采用** |

最终形态是 **RAG 融合问答系统**：MySQL 存高频 FQA（命中即返回，快且准）+ Milvus 存文档切片（兜底，覆盖长尾）+ Redis 做热点缓存 + FastAPI/WebSocket 对外提供流式问答。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/01-问答与RAG系统/01-项目-法律咨询RAG问答系统.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「两种解法与选择」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/01-问答与RAG系统/01-项目-法律咨询RAG问答系统.md)
