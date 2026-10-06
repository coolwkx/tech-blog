---
article_id: kp-95d64ed871801040
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-1043063b962d
learning_sourceId: 1043063b962d
learning_order: 6
learning_objective: 理解并验证：Memory：大模型没有记忆，需要显式回传
---

# Memory：大模型没有记忆，需要显式回传

> **学习目标**：能够解释「Memory：大模型没有记忆，需要显式回传」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：大模型 API 与消息角色（见《05-大模型API与调用实践》）、embedding 与向量检索（见《07-向量数据库与Milvus》）。
>
> **所属主题**：-LangChain基础 · 关键机制

## 本次只学这一点

**关键认知**：大模型本身**不具备上下文的概念**，不保存上次交互的内容；ChatGPT 能对话是因为它**把历史记录回传给了模型**。

| 类型 | 含义 |
|---|---|
| 短期记忆 | 单一会话内传递数据 |
| 长期记忆 | 处理多个会话时获取和更新信息 |

```python
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import messages_to_dict, messages_from_dict

history = ChatMessageHistory
history.add_user_message("在吗？")
history.add_ai_message("有什么事?")
dicts = messages_to_dict(history.messages) # 可落 Redis/MySQL/文件（长期记忆）
restored = messages_from_dict(dicts) # 读回后还原成消息对象
```

**记忆的工程代价**：全量回传会让 token 随轮次线性增长，因此必须做**窗口截断或摘要压缩**。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Memory：大模型没有记忆，需要显式回传」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)
