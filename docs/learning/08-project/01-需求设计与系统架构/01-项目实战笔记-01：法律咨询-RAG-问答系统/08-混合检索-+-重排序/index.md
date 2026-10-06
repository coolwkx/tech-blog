---
article_id: kp-fe6bfada11d3fc09
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-e94c0577cb2f
learning_sourceId: e94c0577cb2f
learning_order: 8
learning_objective: 理解并验证：混合检索 + 重排序
---

# 混合检索 + 重排序

> **学习目标**：能够解释「混合检索 + 重排序」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 工程化基础、向量检索原理（Embedding / 余弦相似度 / ANN）、LangChain 的 Document 与 TextSplitter 抽象、FastAPI 基础、MySQL 与 Redis 基本操作。
>
> **所属主题**：项目实战笔记 01：法律咨询 RAG 问答系统 · 核心实现

## 本次只学这一点

```python
def hybrid_search_with_rerank(self, query, k=5, source_filter=None):
    emb = self.embedding_function([query])
    dense_q = emb["dense"][0]
    row = emb["sparse"].getrow(0)
    sparse_q = {int(i): float(v) for i, v in zip(row.indices, row.data)}

    expr = f"source == '{source_filter}'" if source_filter else ""
    reqs = [
    AnnSearchRequest([dense_q], "dense_vector",
    {"metric_type": "IP", "params": {"nprobe": 10}}, limit=k, expr=expr),
    AnnSearchRequest([sparse_q], "sparse_vector",
    {"metric_type": "IP", "params": {}}, limit=k, expr=expr),
    ]
    # 稀疏权重 0.7 / 稠密权重 1.0 —— 业务术语（法条编号、案由名）靠稀疏，语义靠稠密
    hits = self.client.hybrid_search(self.collection_name, reqs,
    ranker=WeightedRanker(0.7, 1.0),
    limit=k,
    output_fields=["text", "parent_id",
    "parent_content", "source", "timestamp"])[0]

    sub_chunks = [self._doc_from_hit(h["entity"]) for h in hits]
    parent_docs = self._get_unique_parent_docs(sub_chunks) # 按 parent_content 去重
    if len(parent_docs) < 2:
        return parent_docs[:conf.CANDIDATE_M] # 候选太少，重排无意义

    scores = self.reranker.predict([[query, d.page_content] for d in parent_docs])
    ranked = [d for _, d in sorted(zip(scores, parent_docs), reverse=True)]
    return ranked[:conf.CANDIDATE_M]
```

**两个容易忽略的工程细节**：
1. `_get_unique_parent_docs` 必须**先回溯父块再去重**：多个子块往往来自同一个父块，若先重排会浪费算力在重复内容上。
2. `len(parent_docs) < 2` 时直接返回：CrossEncoder 对 1 个候选打分纯属浪费，且排序结果无意义。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/01-问答与RAG系统/01-项目-法律咨询RAG问答系统.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「混合检索 + 重排序」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/01-问答与RAG系统/01-项目-法律咨询RAG问答系统.md)
