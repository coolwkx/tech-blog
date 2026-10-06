---
article_id: kp-b10573e877822dae
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-6f07590fb31d
learning_sourceId: 6f07590fb31d
learning_order: 8
learning_objective: 理解并验证：混合检索与重排序
---

# 混合检索与重排序

> **学习目标**：能够解释「混合检索与重排序」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：LangChain 六大组件（见《08-LangChain基础》）、Milvus 与向量检索（见《07-向量数据库与Milvus》）、embedding 与相似度。
>
> **所属主题**：-RAG系统构建 · 关键机制

## 本次只学这一点

`VectorStore.hybrid_search_with_rerank(query, k, source_filter)` 是检索侧的统一入口：

| 环节 | 做法 |
|---|---|
| 双路检索 | BGE-M3 同时产出**稠密向量**（语义）与**稀疏向量**（关键词权重），分别走 `IVF_FLAT` 与 `SPARSE_INVERTED_INDEX` |
| 过滤 | 支持 `source_filter` 按学科过滤（对应 `valid_sources`） |
| 融合重排 | `WeightedRanker`（明确侧重时）或 `RRFRanker`（默认） |
| 返回 | **重排后的父文档**（`_doc_from_hit` 把 Milvus 命中结果转成 `Document` 对象） |

**为什么必须重排序**：两路检索的分数不可直接比较，必须先融合排序，再截取 Top-M 作为上下文。
详见《07-向量数据库与Milvus》2.5。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/07-检索增强RAG/09-RAG系统构建.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「混合检索与重排序」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/07-检索增强RAG/09-RAG系统构建.md)
