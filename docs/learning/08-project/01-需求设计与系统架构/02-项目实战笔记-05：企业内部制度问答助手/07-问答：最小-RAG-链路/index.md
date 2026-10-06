---
article_id: kp-907336cf479a2ae8
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-bbd88f00e6f8
learning_sourceId: bbd88f00e6f8
learning_order: 7
learning_objective: 理解并验证：问答：最小 RAG 链路
---

# 问答：最小 RAG 链路

> **学习目标**：能够解释「问答：最小 RAG 链路」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 基础、向量检索的基本概念（Embedding / 相似度 / Top-K）、`pip` 环境管理、Streamlit 的最简用法。
>
> **所属主题**：项目实战笔记 05：企业内部制度问答助手 · 核心实现

## 本次只学这一点

```text
# local_qa.py
import time
from local_db import *
from langchain import PromptTemplate
from langchain_community.llms import Ollama

# 加载 FAISS 向量库（注意：必须用建库时同一个 embedding 模型）
embeddings = OllamaEmbeddings(model="mxbai-embed-large", temperature=0)
db = FAISS.load_local("faiss/policy", embeddings, allow_dangerous_deserialization=True)

start_time = time.time

def get_related_content(related_docs):
 """把检索到的多个 Document 拼成一段连续上下文"""
 related_content = []
 for doc in related_docs:
 related_content.append(doc.page_content.replace("\n\n", "\n"))
 return "\n".join(related_content)

def define_prompt:
 question = '我的年假有多少天？报销多久能到账？'

 # ① 检索：取最相似的 2 个块
 docs = db.similarity_search(question, k=2)
 related_content = get_related_content(docs)

 # ② 组装 Prompt
 PROMPT_TEMPLATE = """
 基于以下已知信息，简洁和专业的来回答用户的问题。不允许在答案中添加编造成分。
 已知内容:
 {context}
 问题:
 {question}"""

 prompt = PromptTemplate(input_variables=["context", "question"],
 template=PROMPT_TEMPLATE)
 my_pmt = prompt.format(context=related_content, question=question)
 return my_pmt

def qa:
 model = Ollama(model="qwen2.5:7b")
 my_pmt = define_prompt
 result = model.invoke(my_pmt)
 return result

if __name__ == '__main__':
 result = qa
 print(result)
 end_time = time.time
 print(end_time - start_time)
```

**Prompt 里那句"不允许在答案中添加编造成分"是整个项目最重要的一行。** RAG 的全部价值建立在一个承诺上：**答案来自检索到的材料**。如果 Prompt 不显式约束，模型会热情地"补全"知识库里没有的信息（比如编出一个"年假只有 3 天"）。这句约束把模型的自由度从"自由作答"压到"仅根据材料作答"。

对照 RAG 的 Prompt，可以看到同一个思路的两个成熟度：

```text
RAG: 如果无法回答，请回复："信息不足，无法回答，请联系人工客服，电话：{phone}。"
本项目: 不允许在答案中添加编造成分。
```

RAG 更成熟，因为它规定了**兜底动作**（转人工），而不仅仅是禁止。禁止只会让模型沉默或含糊，给出明确的兜底话术才能形成闭环。**改进本项目的 Prompt 时，第一个该加的就是这个兜底分支。**

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/01-问答与RAG系统/05-项目-企业内部制度问答助手.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「问答：最小 RAG 链路」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/01-问答与RAG系统/05-项目-企业内部制度问答助手.md)
