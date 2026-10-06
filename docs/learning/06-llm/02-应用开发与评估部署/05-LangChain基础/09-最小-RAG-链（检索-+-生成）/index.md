---
article_id: kp-9bdd5c5e2acf43df
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-1043063b962d
learning_sourceId: 1043063b962d
learning_order: 8
learning_objective: 理解并验证：最小 RAG 链（检索 + 生成）
---

# 最小 RAG 链（检索 + 生成）

> **学习目标**：能够解释「最小 RAG 链（检索 + 生成）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：大模型 API 与消息角色（见《05-大模型API与调用实践》）、embedding 与向量检索（见《07-向量数据库与Milvus》）。
>
> **所属主题**：-LangChain基础 · 可运行示例

## 本次只学这一点

```python
# 依赖：pip install langchain langchain-community langchain-text-splitters langchain-ollama chromadb
# 前置：ollama pull qwen2.5:7b && ollama pull nomic-embed-text
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

raw_text = """北京大学创办于1898年，初名京师大学堂，是中国近代第一所国立综合性大学。
1912年更名为北京大学。学校位于北京市海淀区。"""

splitter = RecursiveCharacterTextSplitter(chunk_size=60, chunk_overlap=10,
separators=["\n\n", "\n", "。", ""])
chunks = splitter.split_text(raw_text)

embeddings = OllamaEmbeddings(model="nomic-embed-text")
store = Chroma.from_texts(chunks, embeddings, persist_directory="./chroma_demo")
retriever = store.as_retriever(search_kwargs={"k": 2})

prompt = ChatPromptTemplate.from_messages([
("system", "只依据下面提供的回答问题；本主题提及的内容回答「未提及」。\n\n：\n{context}"),
("human", "{question}"),
])
llm = ChatOllama(model="qwen2.5:7b", temperature=0)

rag_chain = (
{"context": retriever | (lambda docs: "\n\n".join(d.page_content for d in docs)),
"question": RunnablePassthrough}
| prompt | llm | StrOutputParser
)

print(rag_chain.invoke("北京大学什么时候创办的？"))
print(rag_chain.invoke("北京大学的食堂几点开门？")) # 应回答「未提及」
```

| 环节 | 组件 | 关键点 |
|---|---|---|
| 分割 | `RecursiveCharacterTextSplitter` | `chunk_size` 与 `chunk_overlap` 决定检索与生成质量 |
| 向量化 | `OllamaEmbeddings` | 建库与查询必须用同一个模型 |
| 存储检索 | `Chroma` + `as_retriever` | `k` 控制召回条数 |
| 生成 | `ChatPromptTemplate` + `ChatOllama` | 明确约束「只依据作答」 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「最小 RAG 链（检索 + 生成）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)
