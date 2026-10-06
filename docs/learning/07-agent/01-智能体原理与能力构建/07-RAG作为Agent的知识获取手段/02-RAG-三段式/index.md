---
article_id: kp-dd063867d3fff9a8
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-d130ec37c55d
learning_sourceId: d130ec37c55d
learning_order: 1
learning_objective: 理解并验证：RAG 三段式
---

# RAG 三段式

> **学习目标**：能够解释「RAG 三段式」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的外部知识记忆、[04-Agent的规划与任务分解](../../../../../07-agent/02-工具与规划/04-Agent的规划与任务分解.md) 的查询改写策略、[../llm/07-向量数据库与Milvus.md](../../../../../06-llm/07-检索增强RAG/07-向量数据库与Milvus.md)。
>
> **所属主题**：-RAG作为Agent的知识获取手段 · 核心概念

## 本次只学这一点

| 阶段 | 何时执行 | 主要动作 | 的模块 |
| --- | --- | --- | --- |
| 索引（Indexing） | 离线，一次性或定期 | 加载 → 切分 → 向量化 → 写入向量库 | `document_processor.py`、`vector_store.py`（写入部分） |
| 检索（Retrieval） | 在线，每次查询 | 查询向量化 → 混合检索 → 重排 → 取父文档 | `vector_store.py`（检索部分）、`strategy_selector.py` |
| 生成（Generation） | 在线，检索之后 | 拼上下文 → 调 LLM → 输出答案 | `prompts.py`、`rag_system.py` |

一个常见的理解误区是把 RAG 等同于「向量检索」。实际上**检索只是中间一环**，前后两环（切分策略、prompt 设计）对最终质量的影响往往更大。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「RAG 三段式」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md)
