---
article_id: kp-bf0585e288dc12a2
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-e94c0577cb2f
learning_sourceId: e94c0577cb2f
learning_order: 6
learning_objective: 理解并验证：分层切分：给子块装上"回溯指针"
---

# 分层切分：给子块装上"回溯指针"

> **学习目标**：能够解释「分层切分：给子块装上"回溯指针"」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 工程化基础、向量检索原理（Embedding / 余弦相似度 / ANN）、LangChain 的 Document 与 TextSplitter 抽象、FastAPI 基础、MySQL 与 Redis 基本操作。
>
> **所属主题**：项目实战笔记 01：法律咨询 RAG 问答系统 · 核心实现

## 本次只学这一点

这是整个系统的地基。子块只用于**检索**，父块才用于**生成**。

```python
# core/document_processor.py（精简）
def process_documents(directory_path, parent_chunk_size=1200,
child_chunk_size=300, chunk_overlap=50):
    documents = load_documents_from_directory(directory_path) # 已带 source/file_path 元数据
    parent_splitter = ChineseRecursiveTextSplitter(parent_chunk_size, chunk_overlap)
    child_splitter = ChineseRecursiveTextSplitter(child_chunk_size, chunk_overlap)
    child_chunks = []
    for i, doc in enumerate(documents):
        for j, parent_doc in enumerate(parent_splitter.split_documents([doc])):
            parent_id = f"doc_{i}_parent_{j}"
            # 关键：把父块全文塞进每个子块的元数据里，检索后无需二次查库
            parent_doc.metadata["parent_id"] = parent_id
            parent_doc.metadata["parent_content"] = parent_doc.page_content

            for k, sub in enumerate(child_splitter.split_documents([parent_doc])):
                sub.metadata.update(parent_id=parent_id,
                parent_content=parent_doc.page_content,
                id=f"{parent_id}_child_{k}")
                child_chunks.append(sub)
                return child_chunks
```

**为什么这么写**：如果把 `parent_content` 只存下来做 join，检索后就要再查一次 Milvus；直接冗余进子块，一次检索就能拿到完整上下文。代价是存储放大，但文档总量只有 MB 级，完全可接受。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/01-问答与RAG系统/01-项目-法律咨询RAG问答系统.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「分层切分：给子块装上"回溯指针"」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/01-问答与RAG系统/01-项目-法律咨询RAG问答系统.md)
