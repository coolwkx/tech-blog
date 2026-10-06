---
article_id: kp-7fad6e450231791b
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-6f07590fb31d
learning_sourceId: 6f07590fb31d
learning_order: 10
learning_objective: 理解并验证：-RAG系统构建：可运行示例
---

# -RAG系统构建：可运行示例

> **学习目标**：能够解释「-RAG系统构建：可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：LangChain 六大组件（见《08-LangChain基础》）、Milvus 与向量检索（见《07-向量数据库与Milvus》）、embedding 与相似度。
>
> **所属主题**：-RAG系统构建 · 可运行示例

## 本次只学这一点

```text
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

docs = TextLoader("data/物流信息.txt", encoding="utf-8").load()

# 1) 分层切块：父块给 LLM，子块建索引（子块携带父块 id 与原文）
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=60, chunk_overlap=10)
children = []
for i, doc in enumerate(docs):
 for j, parent in enumerate(parent_splitter.split_documents([doc])):
 pid = f"doc_{i}_parent_{j}"
 for k, child in enumerate(child_splitter.split_documents([parent])):
 child.metadata.update({"id": f"{pid}_child_{k}", "parent_id": pid,
 "parent_content": parent.page_content})
 children.append(child)

# 2) 向量化入库并持久化
embeddings = OllamaEmbeddings(model="mxbai-embed-large", temperature=0)
db = FAISS.from_documents(children, embeddings)
db.save_local("faiss/wuliu")


# 3) 检索 + 父块返回（命中子块，用父块原文替换以补全上下文）
def retrieve_context(question, k=3):
 parents, seen = [], set()
 for h in db.similarity_search(question, k=k):
 pid = h.metadata.get("parent_id")
 if pid and pid not in seen:
 seen.add(pid)
 parents.append(h.metadata.get("parent_content", h.page_content))
 return parents


# 4) 生成：Prompt 必须约束「不许编造」，并给出兜底话术
TEMPLATE = """基于以下已知信息，简洁和专业的来回答用户的问题。不允许在答案中添加编造成分。
如果已知信息不足以回答，请回答「已知信息不足，无法回答」。

已知内容:
{context}

问题:
{question}
回答:"""
prompt = PromptTemplate(input_variables=["context", "question"], template=TEMPLATE)
llm = Ollama(model="qwen2.5:7b", temperature=0)

for q in ["从上海发往北京用顺丰要多久？", "海运到南美洲需要几天？"]:
 ctx = "\n".join(retrieve_context(q, k=3))
 print("Q:", q)
 print("A:", llm.invoke(prompt.format(context=ctx, question=q)))
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/07-检索增强RAG/09-RAG系统构建.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「-RAG系统构建：可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/07-检索增强RAG/09-RAG系统构建.md)
