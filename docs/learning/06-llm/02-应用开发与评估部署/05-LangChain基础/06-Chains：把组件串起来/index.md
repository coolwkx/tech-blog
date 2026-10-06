---
article_id: kp-c32ea8a9a3dbc571
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-1043063b962d
learning_sourceId: 1043063b962d
learning_order: 5
learning_objective: 理解并验证：Chains：把组件串起来
---

# Chains：把组件串起来

> **学习目标**：能够解释「Chains：把组件串起来」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：大模型 API 与消息角色（见《05-大模型API与调用实践》）、embedding 与向量检索（见《07-向量数据库与Milvus》）。
>
> **所属主题**：-LangChain基础 · 关键机制

## 本次只学这一点

**旧写法（语料，基于 2023 年版本）**：

```python
from langchain.chains import LLMChain
chain = LLMChain(llm=llm, prompt=prompt)
print(chain.run("王"))
```

**`SimpleSequentialChain`**：把**前一条链的输出**直接作为**后一条链的输入**。

```python
from langchain.chains import LLMChain, SimpleSequentialChain
first = LLMChain(llm=llm, prompt=PromptTemplate(
template="我的邻居姓{lastname}，他生了个儿子，给他儿子起个名字", input_variables=["lastname"]))
second = LLMChain(llm=llm, prompt=PromptTemplate(
template="邻居的儿子名字叫{child_name}，给他起一个小名", input_variables=["child_name"]))
overall = SimpleSequentialChain(chains=[first, second], verbose=True)
print(overall.run("王")) # 只需传入第一个链的参数
```

**为什么要链**：多步任务需要传递中间结果、对齐变量名、可观测执行过程。链把「拼字符串 → 调用 → 再拼」的胶水代码收敛成声明式结构。

**新旧 API 对照（重要）**——LangChain 0.1 之后主推 **LCEL**，用管道符 `|` 组合 `Runnable`：

| 旧写法（语料） | 新写法（LCEL） |
|---|---|
| `LLMChain(llm=llm, prompt=p)` + `chain.run(x)` | `p \| llm` + `chain.invoke({"变量": x})` |
| `SimpleSequentialChain(chains=[a, b])` | `a \| b` |
| `ConversationChain(llm=llm)` | `RunnableWithMessageHistory` + `InMemoryChatMessageHistory` |
| `retriever.get_relevant_documents(q)` | `retriever.invoke(q)` |
| `from langchain.llms import Ollama` | `from langchain_ollama import OllamaLLM` |
| `from langchain.chat_models import ChatOpenAI` | `from langchain_openai import ChatOpenAI` |

LCEL 等价写法：

```python
chain = first_prompt | llm | (lambda name: {"child_name": name.strip()}) | second_prompt | llm
print(chain.invoke({"lastname": "王"}))
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Chains：把组件串起来」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)
