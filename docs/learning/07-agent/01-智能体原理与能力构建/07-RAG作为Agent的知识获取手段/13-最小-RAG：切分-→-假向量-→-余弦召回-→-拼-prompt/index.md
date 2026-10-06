---
article_id: kp-07de4e8d33ef7ef6
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-d130ec37c55d
learning_sourceId: d130ec37c55d
learning_order: 12
learning_objective: 理解并验证：最小 RAG：切分 → 假向量 → 余弦召回 → 拼 prompt
---

# 最小 RAG：切分 → 假向量 → 余弦召回 → 拼 prompt

> **学习目标**：能够解释「最小 RAG：切分 → 假向量 → 余弦召回 → 拼 prompt」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的外部知识记忆、[04-Agent的规划与任务分解](../../../../../07-agent/02-工具与规划/04-Agent的规划与任务分解.md) 的查询改写策略、[../llm/07-向量数据库与Milvus.md](../../../../../06-llm/07-检索增强RAG/07-向量数据库与Milvus.md)。
>
> **所属主题**：-RAG作为Agent的知识获取手段 · 可运行示例

## 本次只学这一点

**依赖**：仅标准库（用哈希构造伪向量替代 embedding，便于本地验证流程）。

```python
"""Milvus 混合检索 + 重排的骨架实现（对应源文件 vector_store.py）。

依赖：pip install pymilvus milvus-model sentence-transformers
"""

import hashlib

from langchain.docstore.document import Document
from milvus_model.hybrid import BGEM3EmbeddingFunction
from pymilvus import AnnSearchRequest, DataType, MilvusClient, WeightedRanker
from sentence_transformers import CrossEncoder

COLLECTION_NAME = "edu_rag"
HOST, PORT, DATABASE = "localhost", 19530, "default"
RETRIEVAL_K = 10
CANDIDATE_M = 5

class VectorStore:
    def __init__(self, reranker_path="./bge/bge-reranker-large"):
        self.reranker = CrossEncoder(reranker_path)
        self.embedding_function = BGEM3EmbeddingFunction(use_fp16=False, device="cpu")
        self.dense_dim = self.embedding_function.dim["dense"]
        self.client = MilvusClient(uri="http://%s:%s" % (HOST, PORT), db_name=DATABASE)
        self._create_or_load_collection()

        def _create_or_load_collection(self):
            if not self.client.has_collection(COLLECTION_NAME):
                schema = self.client.create_schema(auto_id=False, enable_dynamic_field=True)
                schema.add_field(field_name="id", datatype=DataType.VARCHAR, is_primary=True, max_length=100)
                schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)
                schema.add_field(field_name="dense_vector", datatype=DataType.FLOAT_VECTOR, dim=self.dense_dim)
                schema.add_field(field_name="sparse_vector", datatype=DataType.SPARSE_FLOAT_VECTOR)
                schema.add_field(field_name="parent_id", datatype=DataType.VARCHAR, max_length=100)
                schema.add_field(field_name="parent_content", datatype=DataType.VARCHAR, max_length=65535)
                schema.add_field(field_name="source", datatype=DataType.VARCHAR, max_length=50)

                index_params = self.client.prepare_index_params()
                index_params.add_index(
                field_name="dense_vector", index_name="dense_index",
                index_type="IVF_FLAT", metric_type="IP", params={"nlist": 128},
                )
                index_params.add_index(
                field_name="sparse_vector", index_name="sparse_index",
                index_type="SPARSE_INVERTED_INDEX", metric_type="IP",
                params={"drop_ratio_build": 0.2},
                )
                self.client.create_collection(
                collection_name=COLLECTION_NAME, schema=schema, index_params=index_params
                )
                print("已创建集合 %s" % COLLECTION_NAME)
            else:
                print("已加载集合 %s" % COLLECTION_NAME)
                self.client.load_collection(COLLECTION_NAME)

                @staticmethod
                def _sparse_to_dict(row):
                    return {int(idx): float(value) for idx, value in zip(row.indices, row.data)}

                def add_documents(self, documents):
                    texts = [doc.page_content for doc in documents]
                    embeddings = self.embedding_function(texts)
                    data = []
                    for i, doc in enumerate(documents):
                        data.append({
                        "id": hashlib.md5(doc.page_content.encode("utf-8")).hexdigest(),
                        "text": doc.page_content,
                        "dense_vector": embeddings["dense"][i],
                        "sparse_vector": self._sparse_to_dict(embeddings["sparse"].getrow(i)),
                        "parent_id": doc.metadata["parent_id"],
                        "parent_content": doc.metadata["parent_content"],
                        "source": doc.metadata.get("source", "unknown"),
                        })
                        if data:
                            self.client.upsert(collection_name=COLLECTION_NAME, data=data)
                            print("已插入或更新 %d 个文档" % len(data))

                            def hybrid_search_with_rerank(self, query, k=RETRIEVAL_K, source_filter=None):
                                query_embeddings = self.embedding_function([query])
                                dense_query_vector = query_embeddings["dense"][0]
                                sparse_query_vector = self._sparse_to_dict(query_embeddings["sparse"].getrow(0))

                                filter_expr = "source == '%s'" % source_filter if source_filter else ""

                                dense_request = AnnSearchRequest(
                                data=[dense_query_vector], anns_field="dense_vector",
                                param={"metric_type": "IP", "params": {"nprobe": 10}}, limit=k, expr=filter_expr,
                                )
                                sparse_request = AnnSearchRequest(
                                data=[sparse_query_vector], anns_field="sparse_vector",
                                param={"metric_type": "IP", "params": {}}, limit=k, expr=filter_expr,
                                )

                                ranker = WeightedRanker(0.7, 1.0) # 稀疏 0.7，稠密 1.0
                                results = self.client.hybrid_search(
                                collection_name=COLLECTION_NAME,
                                reqs=[dense_request, sparse_request],
                                ranker=ranker,
                                limit=k,
                                output_fields=["text", "parent_id", "parent_content", "source"],
                                )[0]

                                parent_docs = self._get_unique_parent_docs(results)
                                if len(parent_docs) < 2: # 只有 1 个文档时跳过重排
                                    return parent_docs[:CANDIDATE_M]
                                pairs = [[query, doc.page_content] for doc in parent_docs]
                                scores = self.reranker.predict(pairs)
                                ranked = [doc for _, doc in sorted(zip(scores, parent_docs), reverse=True)]
                                return ranked[:CANDIDATE_M]

                            @staticmethod
                            def _get_unique_parent_docs(hits):
                                seen, unique_docs = set(), []
                                for hit in hits:
                                    entity = hit["entity"] if isinstance(hit, dict) and "entity" in hit else hit
                                    parent_content = entity.get("parent_content") or entity.get("text")
                                    if parent_content and parent_content not in seen:
                                        unique_docs.append(Document(
                                        page_content=parent_content,
                                        metadata={"parent_id": entity.get("parent_id"), "source": entity.get("source")},
                                        ))
                                        seen.add(parent_content)
                                        return unique_docs

                                    if __name__ == "__main__":
                                        store = VectorStore()
                                        print(store.hybrid_search_with_rerank("人工智能方向学费是多少？", source_filter="ai"))
```

预期输出（要点）：

```text
索引块数: 12
=== 查询: IVF_FLAT 索引有什么特点？
 召回: IVF_FLAT 索引属于倒排文件加暴力精算，精度高、构建速度快。
--- 最终 prompt ---
... 上下文: IVF_FLAT 索引属于倒排文件加暴力精算 ... 问题: IVF_FLAT 索引有什么特点？ ...
```

真实项目只需把 `fake_embed` 换成 `BGEM3EmbeddingFunction()` 或 `OllamaEmbeddings(model="mxbai-embed-large")`，把内存列表换成 Milvus/FAISS/Chroma。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「最小 RAG：切分 → 假向量 → 余弦召回 → 拼 prompt」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md)
