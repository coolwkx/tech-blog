---
article_id: kp-82a68250010bc958
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-d130ec37c55d
learning_sourceId: d130ec37c55d
learning_order: 13
learning_objective: 理解并验证：Milvus 混合检索与重排（vector_store.py）
---

# Milvus 混合检索与重排（vector_store.py）

> **学习目标**：能够解释「Milvus 混合检索与重排（vector_store.py）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的外部知识记忆、[04-Agent的规划与任务分解](../../../../../07-agent/02-工具与规划/04-Agent的规划与任务分解.md) 的查询改写策略、[../llm/07-向量数据库与Milvus.md](../../../../../06-llm/07-检索增强RAG/07-向量数据库与Milvus.md)。
>
> **所属主题**：-RAG作为Agent的知识获取手段 · 可运行示例

## 本次只学这一点

**依赖**：`pip install pymilvus milvus-model sentence-transformers`；本地需准备 `./bge/bge-reranker-large` 模型目录。

```python
"""LangChain 侧的 RAG 最小验证：加载 → 切分 → 向量化 → 检索。

依赖：pip install langchain langchain-community chromadb faiss-cpu ollama
"""

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="mxbai-embed-large")

documents = TextLoader("./pku.txt", encoding="utf-8").load()
text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
texts = text_splitter.split_documents(documents)
print("切分后块数:", len(texts))

try:
 from langchain_community.vectorstores import Chroma
 db = Chroma.from_documents(texts, embeddings)
except ImportError:
 from langchain_community.vectorstores import FAISS
 db = FAISS.from_documents(texts, embeddings)

retriever = db.as_retriever(search_kwargs={"k": 1})
docs = retriever.get_relevant_documents("北京大学什么时候成立的")
for doc in docs:
 print(doc.page_content)
```

要点回顾：`upsert` 用内容 MD5 作主键保证幂等；稠密与稀疏各发一个 `AnnSearchRequest` 后用 `WeightedRanker` 融合；命中子块后**替换为去重的父块**再重排；`nprobe` 控制精度/速度权衡。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Milvus 混合检索与重排（vector_store.py）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md)
