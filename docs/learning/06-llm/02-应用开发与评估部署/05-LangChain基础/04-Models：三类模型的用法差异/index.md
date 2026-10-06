---
article_id: kp-8cb3c7167a18cdb6
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-1043063b962d
learning_sourceId: 1043063b962d
learning_order: 3
learning_objective: 理解并验证：Models：三类模型的用法差异
---

# Models：三类模型的用法差异

> **学习目标**：能够解释「Models：三类模型的用法差异」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：大模型 API 与消息角色（见《05-大模型API与调用实践》）、embedding 与向量检索（见《07-向量数据库与Milvus》）。
>
> **所属主题**：-LangChain基础 · 关键机制

## 本次只学这一点

**LLMs**：`invoke` 传字符串、返回字符串。

```python
from langchain_community.llms import Ollama
model = Ollama(model="qwen2.5:7b")
print(model.invoke("请给我讲个鬼故事"))
```

**Chat Models**：按约定传入**消息对象**，返回的也是消息对象（取 `.content`）。

| 消息类 | 作用 |
|---|---|
| `SystemMessage` | 设置模型的行为方式和目标，可接收任意形式的值 |
| `HumanMessage` | 发送给 LLM 的提示信息 |
| `AIMessage` | 保存 LLM 的响应，以便下次请求把这些信息传回给 LLM |

```python
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

model = ChatOllama(model="qwen2.5:7b")
res = model.invoke([SystemMessage(content="现在你是一个著名的诗人"),
HumanMessage(content="给我写一首唐诗")])
print(res.content)
```

**Embeddings**：注意 **建库与查询用不同方法，且必须用同一个模型**。

```python
from langchain_community.embeddings import OllamaEmbeddings
emb = OllamaEmbeddings(model="nomic-embed-text", temperature=0)
q = emb.embed_query("这是第一个测试文档") # 查询向量
docs = emb.embed_documents(["这是第一个测试文档", "这是第二个测试文档"]) # 批量建库
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Models：三类模型的用法差异」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)
