---
article_id: kp-2eb2ad064f53c13d
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-1043063b962d
learning_sourceId: 1043063b962d
learning_order: 9
learning_objective: 理解并验证：带记忆的多轮对话（新版写法）
---

# 带记忆的多轮对话（新版写法）

> **学习目标**：能够解释「带记忆的多轮对话（新版写法）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：大模型 API 与消息角色（见《05-大模型API与调用实践》）、embedding 与向量检索（见《07-向量数据库与Milvus》）。
>
> **所属主题**：-LangChain基础 · 可运行示例

## 本次只学这一点

```python
# 依赖：pip install langchain-core langchain-ollama
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

prompt = ChatPromptTemplate.from_messages([
("system", "你是一个说话简洁的助手。"),
MessagesPlaceholder(variable_name="history"),
("human", "{input}"),
])
chain = prompt | ChatOllama(model="qwen2.5:7b", temperature=0)

_store = {}
def get_history(session_id: str):
    if session_id not in _store:
        _store[session_id] = InMemoryChatMessageHistory()
        return _store[session_id]

    chat = RunnableWithMessageHistory(chain, get_history,
    input_messages_key="input", history_messages_key="history")
    cfg = {"configurable": {"session_id": "user-1"}}
    print(chat.invoke({"input": "小明有1只猫"}, config=cfg).content)
    print(chat.invoke({"input": "小刚有2只狗"}, config=cfg).content)
    print(chat.invoke({"input": "他们一共有几只宠物？"}, config=cfg).content) # 能利用上文
```

`RunnableWithMessageHistory` 相当于把「取历史 → 拼 prompt → 调用 → 写回历史」显式化，
`session_id` 对应会话隔离，便于换成持久化后端——这就替代了旧的 `ConversationChain`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「带记忆的多轮对话（新版写法）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)
