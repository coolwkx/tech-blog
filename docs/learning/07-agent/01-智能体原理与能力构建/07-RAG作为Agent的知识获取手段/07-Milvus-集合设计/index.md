---
article_id: kp-67771ddd0a8f0966
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-d130ec37c55d
learning_sourceId: d130ec37c55d
learning_order: 6
learning_objective: 理解并验证：Milvus 集合设计
---

# Milvus 集合设计

> **学习目标**：能够解释「Milvus 集合设计」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的外部知识记忆、[04-Agent的规划与任务分解](../../../../../07-agent/02-工具与规划/04-Agent的规划与任务分解.md) 的查询改写策略、[../llm/07-向量数据库与Milvus.md](../../../../../06-llm/07-检索增强RAG/07-向量数据库与Milvus.md)。
>
> **所属主题**：-RAG作为Agent的知识获取手段 · 关键机制

## 本次只学这一点

`_create_or_load_collection()` 的 schema：

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| `id` | `VARCHAR` | `is_primary=True, max_length=100` | 主键，写入时为文档内容的 **MD5 哈希** |
| `text` | `VARCHAR` | `max_length=65535` | 子块原文 |
| `dense_vector` | `FLOAT_VECTOR` | `dim=self.dense_dim` | BGE-M3 稠密向量 |
| `sparse_vector` | `SPARSE_FLOAT_VECTOR` | — | BGE-M3 稀疏向量（词权重） |
| `parent_id` | `VARCHAR` | `max_length=100` | 父块标识 |
| `parent_content` | `VARCHAR` | `max_length=65535` | 父块内容 |
| `source` | `VARCHAR` | `max_length=50` | 学科类别 |
| `timestamp` | `VARCHAR` | `max_length=50` | 入库时间 |

索引设计：

| 字段 | 索引类型 | 度量 | 参数 | 取舍 |
| --- | --- | --- | --- | --- |
| `dense_vector` | `IVF_FLAT` | `IP`（内积） | `nlist=128` | 倒排文件 + 暴力精算，**精度高、速度中等**；`nlist` 越大聚类越细 |
| `sparse_vector` | `SPARSE_INVERTED_INDEX` | `IP` | `drop_ratio_build=0.2` | 稀疏倒排索引，构建时丢弃权重最小的 20% 词项以省空间 |

其它要点：

- `create_schema(auto_id=False, enable_dynamic_field=True)`：主键自己给（因为要用 MD5），并允许写入 schema 之外的动态字段；
- 创建后必须 `load_collection()` 才能查询；
- 写入用 `upsert` 而非 `insert`，**相同 ID（相同内容）覆盖**，天然具备幂等性——重复索引同一批文档不会产生重复条目。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Milvus 集合设计」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md)
