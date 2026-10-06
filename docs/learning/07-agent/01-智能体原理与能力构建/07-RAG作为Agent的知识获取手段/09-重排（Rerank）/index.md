---
article_id: kp-15dbdd1eb632bab8
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-d130ec37c55d
learning_sourceId: d130ec37c55d
learning_order: 8
learning_objective: 理解并验证：重排（Rerank）
---

# 重排（Rerank）

> **学习目标**：能够解释「重排（Rerank）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的外部知识记忆、[04-Agent的规划与任务分解](../../../../../07-agent/02-工具与规划/04-Agent的规划与任务分解.md) 的查询改写策略、[../llm/07-向量数据库与Milvus.md](../../../../../06-llm/07-检索增强RAG/07-向量数据库与Milvus.md)。
>
> **所属主题**：-RAG作为Agent的知识获取手段 · 关键机制

## 本次只学这一点

检索得到 Top-K 之后，还有一个精排阶段：

| 步骤 | 做法 | 目的 |
| --- | --- | --- |
| 1 | 把命中的子块转成 `Document`，再用 `_get_unique_parent_docs()` 取**去重的父文档** | 用大块提供完整语义，避免同一父块的多个子块挤占名额 |
| 2 | 若父文档少于 2 个，直接返回（**跳过重排**） | 重排意义不大，省一次模型推理 |
| 3 | `pairs = [[query, doc.page_content] for doc in parent_docs]` | 构造 (问题, 文档) 对 |
| 4 | `scores = self.reranker.predict(pairs)` | `CrossEncoder("./bge/bge-reranker-large")` 逐个打分 |
| 5 | `sorted(zip(scores, parent_docs), reverse=True)` | 按分数降序 |
| 6 | `return ranked_parent_docs[:conf.CANDIDATE_M]` | 裁剪到候选上限，控制 prompt 长度 |

**为什么需要重排**：向量检索是「双塔」结构，查询与文档分别编码后算相似度，速度快但精度有限；CrossEncoder 把查询与文档**拼在一起**过一遍模型，能建模细粒度交互，精度更高但无法预先建索引，因此只能对少量候选做精排。这就是「粗召回 + 精排」的两阶段范式。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「重排（Rerank）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md)
