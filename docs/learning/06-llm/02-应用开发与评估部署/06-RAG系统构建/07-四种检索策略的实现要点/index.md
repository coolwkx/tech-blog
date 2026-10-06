---
article_id: kp-3a698cfc7806cc98
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-6f07590fb31d
learning_sourceId: 6f07590fb31d
learning_order: 6
learning_objective: 理解并验证：四种检索策略的实现要点
---

# 四种检索策略的实现要点

> **学习目标**：能够解释「四种检索策略的实现要点」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：LangChain 六大组件（见《08-LangChain基础》）、Milvus 与向量检索（见《07-向量数据库与Milvus》）、embedding 与相似度。
>
> **所属主题**：-RAG系统构建 · 关键机制

## 本次只学这一点

`rag_system.py` 把策略落到四个方法上：

| 方法 | 实现 | 注意点 |
|---|---|---|
| `_retrieve_with_hyde` | 用 `hyde_prompt` 生成假设答案 → 用**假设答案**去检索 | 注释指出「HyDE 通常只用于生成检索向量，不一定需要 rerank 这一步」 |
| `_retrieve_with_subqueries` | 生成子查询 → 逐个检索 → 合并 → **按 `page_content` 去重** | 每个子查询都做混合检索 + 重排，**开销可能较大** |
| `_retrieve_with_backtracking` | 生成简化问题 → 用简化问题检索 | 降低检索难度 |
| 默认（直接检索） | 用原查询做混合检索，支持 `source_filter` | 按学科过滤 |

**去重的正确做法**：代码里先注释掉了「基于对象内存地址」的思路，改为
`{doc.page_content: doc for doc in all_docs}`——**基于内容去重**。
注释明确指出：如果 Document 内容相同但对象不同，按内存地址无法去重。这是很典型的一课。

**统一收敛**：无论走哪条策略，最终都在 `retrieve_and_merge` 里做 `ranked_sub_chunks[:candidate_m]`，
即**所有策略共用同一个「精选阶段」**，保证送给 LLM 的上下文长度可控。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/07-检索增强RAG/09-RAG系统构建.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「四种检索策略的实现要点」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/07-检索增强RAG/09-RAG系统构建.md)
