---
article_id: kp-638760993897231f
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-d130ec37c55d
learning_sourceId: d130ec37c55d
learning_order: 3
learning_objective: 理解并验证：LangChain Indexes 四件套
---

# LangChain Indexes 四件套

> **学习目标**：能够解释「LangChain Indexes 四件套」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的外部知识记忆、[04-Agent的规划与任务分解](../../../../../07-agent/02-工具与规划/04-Agent的规划与任务分解.md) 的查询改写策略、[../llm/07-向量数据库与Milvus.md](../../../../../06-llm/07-检索增强RAG/07-向量数据库与Milvus.md)。
>
> **所属主题**：-RAG作为Agent的知识获取手段 · 核心概念

## 本次只学这一点

在 LangChain 部分给出的通用抽象：

| 组件 | 职责 | 示例 |
| --- | --- | --- |
| 文档加载器（Document Loaders） | 把各种格式文件转成文本，基于 `Unstructured` 包 | `TextLoader`、`UnstructuredFileLoader`、`PDF`、`CSV`、`Markdown`、`Images`、`FileDirectory`、`HTML`、`Microsoft PowerPoint`、`Jupyter Notebook` |
| 文本分割器（Text Splitters） | 按分隔符与长度把长文本切成片段 | `CharacterTextSplitter`（默认分隔符 `\n\n`）、`MarkdownTextSplitter`、`TokenTextSplitter`、`PythonCodeTextSplitter`、`LatexTextSplitter` |
| 向量库（VectorStores） | 存储嵌入向量并提供相似查询 | Chroma、FAISS、Milvus、Pinecone、Redis、ElasticSearch |
| 检索器（Retrievers） | 统一查询接口 | `VectorStoreRetriever`、`TF-IDFRetriever`、`SVMRetriever`、`ElasticSearchBM25`、`WeaviateHybridSearch`、`PineconeHybridSearch`、`Wikipedia`、`ChatGPTPluginRetriever` 等 |

**检索器的接口约定**：至少提供一个 `get_relevant_texts`（`get_relevant_documents`）方法，接收查询字符串，返回一组文档。

`CharacterTextSplitter` 的行为示例（原例）：

```python
"""最小 RAG 流程演示：切分 → 向量化 → 余弦召回 → 拼上下文。

依赖：仅标准库。真实项目请用 BGE / OpenAI Embeddings 替换 fake_embed。
"""

import hashlib
import math

DOCUMENT = """
Milvus 是面向向量检索的数据库，支持亿级向量的近似最近邻搜索。
它采用存算分离架构，可通过增加 query node 水平扩展检索吞吐。
IVF_FLAT 索引属于倒排文件加暴力精算，精度高、构建速度快。
SPARSE_INVERTED_INDEX 适合稀疏向量，构建时可用 drop_ratio_build 丢弃低权重词项。
Zilliz Cloud 是全托管的 Milvus 服务，免去集群运维，按量计费。
选择向量数据库时需要权衡成本、运维复杂度与数据规模。
"""

DIM = 64

def fake_embed(text):
    """用字符 bigram 的哈希构造固定维度伪向量，仅用于流程演示。"""
    vector = [0.0] * DIM
    for i in range(len(text) - 1):
        gram = text[i:i + 2]
        index = int(hashlib.md5(gram.encode("utf-8")).hexdigest(), 16) % DIM
        vector[index] += 1.0
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]

    def cosine(a, b):
        return sum(x * y for x, y in zip(a, b))

    def chunk_text(text, chunk_size=60, overlap=10):
        """按字符滑窗切分（真实项目请用按语义/标点的递归切分器）。"""
        chunks = []
        start = 0
        while start < len(text):
            chunks.append(text[start:start + chunk_size])
            start += chunk_size - overlap
            return [c.strip() for c in chunks if c.strip()]

        def build_index(text):
            chunks = chunk_text(text)
            return [{"text": chunk, "vector": fake_embed(chunk)} for chunk in chunks]

        def retrieve(index, query, k=2):
            query_vector = fake_embed(query)
            scored = [(cosine(query_vector, item["vector"]), item) for item in index]
            scored.sort(key=lambda pair: pair[0], reverse=True)
            return [item for _, item in scored[:k]]

        RAG_PROMPT = """你是一个智能助手，帮助用户回答问题。
        如果提供了上下文，请基于上下文回答；如果答案来源于检索到的文档，请在回答中说明。

        上下文: {context}
        问题: {question}

        如果无法回答，请回复："信息不足，无法回答。"
        回答:"""

        def build_prompt(query, docs):
            context = "\n\n".join(doc["text"] for doc in docs) if docs else ""
            return RAG_PROMPT.format(context=context, question=query)

        if __name__ == "__main__":
            index = build_index(DOCUMENT)
            print("索引块数:", len(index))

            for query in ["IVF_FLAT 索引有什么特点？", "完全无关的问题：今天天气如何？"]:
                docs = retrieve(index, query, k=2)
                print("\n=== 查询:", query)
                for doc in docs:
                    print(" 召回:", doc["text"][:40].replace("\n", " "))
                    print("--- 最终 prompt ---")
                    print(build_prompt(query, docs))
```

注意 `chunk_size=5` 却切出 `'a b c'`（3 个字符）——因为切分先按分隔符断开，再在长度限制内合并，所以**实际块长通常小于 `chunk_size`**。这一点在调参时容易误判。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「LangChain Indexes 四件套」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md)
