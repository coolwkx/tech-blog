---
article_id: kp-306e72106167ede0
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-e94c0577cb2f
learning_sourceId: e94c0577cb2f
learning_order: 7
learning_objective: 理解并验证：Milvus Schema 与双索引
---

# Milvus Schema 与双索引

> **学习目标**：能够解释「Milvus Schema 与双索引」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 工程化基础、向量检索原理（Embedding / 余弦相似度 / ANN）、LangChain 的 Document 与 TextSplitter 抽象、FastAPI 基础、MySQL 与 Redis 基本操作。
>
> **所属主题**：项目实战笔记 01：法律咨询 RAG 问答系统 · 核心实现

## 本次只学这一点

```python
# core/vector_store.py（精简）
schema = client.create_schema(auto_id=False, enable_dynamic_field=True)
schema.add_field("id", DataType.VARCHAR, is_primary=True, max_length=100)
schema.add_field("text", DataType.VARCHAR, max_length=65535)
schema.add_field("dense_vector", DataType.FLOAT_VECTOR, dim=self.dense_dim)
schema.add_field("sparse_vector", DataType.SPARSE_FLOAT_VECTOR)
schema.add_field("parent_id", ...); schema.add_field("parent_content", ...)
schema.add_field("source", ...); schema.add_field("timestamp", ...)

index_params.add_index("dense_vector", index_type="IVF_FLAT",
metric_type="IP", params={"nlist": 128})
index_params.add_index("sparse_vector", index_type="SPARSE_INVERTED_INDEX",
metric_type="IP", params={"drop_ratio_build": 0.2})
```

- `auto_id=False` + 主键取 `md5(子块文本)`：**天然幂等**。重跑灌库脚本时 `upsert` 会覆盖而不是追加，这点在调试期反复重灌时救命。
- `metric_type="IP"`：BGE 系列输出已归一化，内积等价于余弦且更快。
- `source` 字段支撑"只查 劳动法"的标量过滤，是业务方最常提的需求。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/01-问答与RAG系统/01-项目-法律咨询RAG问答系统.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Milvus Schema 与双索引」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/01-问答与RAG系统/01-项目-法律咨询RAG问答系统.md)
