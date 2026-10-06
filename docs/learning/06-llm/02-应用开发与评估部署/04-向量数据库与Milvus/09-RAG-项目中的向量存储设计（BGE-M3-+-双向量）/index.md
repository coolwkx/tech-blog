---
article_id: kp-7298336184f7b1fd
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-d0c337577532
learning_sourceId: d0c337577532
learning_order: 8
learning_objective: 理解并验证：RAG 项目中的向量存储设计（BGE-M3 + 双向量）
---

# RAG 项目中的向量存储设计（BGE-M3 + 双向量）

> **学习目标**：能够解释「RAG 项目中的向量存储设计（BGE-M3 + 双向量）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 基础、embedding 与余弦相似度的直觉、关系型数据库基本概念（库/表/行/列/主键）。
>
> **所属主题**：-向量数据库与Milvus · 关键机制

## 本次只学这一点

RAG 项目的 `vector_store.py` 是一个完整的生产级范式，值得单独记住其 Schema 设计：

| 字段 | 类型 | 作用 |
|---|---|---|
| `id` | VARCHAR(100)，主键 | 文本块唯一标识 |
| `text` | VARCHAR(65535) | 文本块原文（检索后送给 LLM 的内容） |
| `dense_vector` | FLOAT_VECTOR | BGE-M3 生成的稠密向量，索引 `IVF_FLAT`，度量 IP |
| `sparse_vector` | SPARSE_FLOAT_VECTOR | BGE-M3 生成的稀疏向量（类似学习到的 BM25 权重），索引 `SPARSE_INVERTED_INDEX`，度量 IP |
| `parent_id` | VARCHAR(100) | 所属父块 ID，支持「小块检索、大块返回」 |
| `parent_content` | VARCHAR(65535) | 父块原文，扩大上下文 |
| `source` | VARCHAR(50) | 来源文件 |
| `timestamp` | VARCHAR(50) | 时间戳 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/07-检索增强RAG/07-向量数据库与Milvus.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「RAG 项目中的向量存储设计（BGE-M3 + 双向量）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/07-检索增强RAG/07-向量数据库与Milvus.md)
