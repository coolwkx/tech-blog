---
article_id: kp-9dff9a29d26a83df
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-d130ec37c55d
learning_sourceId: d130ec37c55d
learning_order: 7
learning_objective: 理解并验证：混合检索：稠密 + 稀疏
---

# 混合检索：稠密 + 稀疏

> **学习目标**：能够解释「混合检索：稠密 + 稀疏」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的外部知识记忆、[04-Agent的规划与任务分解](../../../../../07-agent/02-工具与规划/04-Agent的规划与任务分解.md) 的查询改写策略、[../llm/07-向量数据库与Milvus.md](../../../../../06-llm/07-检索增强RAG/07-向量数据库与Milvus.md)。
>
> **所属主题**：-RAG作为Agent的知识获取手段 · 关键机制

## 本次只学这一点

**为什么要混合**：稠密向量擅长语义相似（「学费多少」↔「收费标准」），稀疏向量擅长精确词匹配（专有名词、型号、人名）。两者互补，混合检索能同时提高召回率与准确率。

流程（`hybrid_search_with_rerank`）：

| 步骤 | 代码 | 说明 |
| --- | --- | --- |
| 1 | `query_embeddings = self.embedding_function([query])` | 一次调用同时得到稠密与稀疏查询向量 |
| 2 | 稀疏矩阵转 dict：`{idx: value}` | 稀疏向量在 Milvus 中以 `{维度: 权重}` 形式传入 |
| 3 | 构造两个 `AnnSearchRequest` | 一个查 `dense_vector`，一个查 `sparse_vector` |
| 4 | `WeightedRanker(0.7, 1.0)` | **稀疏权重 0.7，稠密权重 1.0** |
| 5 | `client.hybrid_search(reqs=[dense, sparse], ranker=ranker, limit=k, output_fields=[...])` | 返回融合后的 Top-K |

检索参数：

| 参数 | 值 | 含义 |
| --- | --- | --- |
| `param={"metric_type": "IP", "params": {"nprobe": 10}}` | 稠密 | 探测 10 个倒排单元；`nprobe` 越大越准越慢 |
| `limit = k`（`conf.RETRIEVAL_K`） | 两路 | 每路各取 Top-K 参与融合 |
| `expr = filter_expr` | 可选 | 如 `source == 'ai'`，按学科过滤 |
| `output_fields` | `text / parent_id / parent_content / source / timestamp` | 只取需要回传的字段，减少网络开销 |

`WeightedRanker` 的权重是需要根据数据调的超参：如果业务里专有名词多、查询短，可以适当提高稀疏权重；如果查询是自然语言长句，稠密权重应更高。给出的 `0.7 / 1.0` 是经验起点而非定论。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「混合检索：稠密 + 稀疏」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md)
