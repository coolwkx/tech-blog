---
article_id: kp-92f1b93db9c5f287
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-3dbf2b7f4206
learning_sourceId: 3dbf2b7f4206
learning_order: 5
learning_objective: 理解并验证：长期记忆：消息序列化
---

# 长期记忆：消息序列化

> **学习目标**：能够解释「长期记忆：消息序列化」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[03-LangChain与工具编排](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md) 的 Memory 组件、[06-RAG作为Agent的知识获取手段](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md) 的向量检索、[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的 messages 角色约定。
>
> **所属主题**：-Agent的记忆与知识管理 · 关键机制

## 本次只学这一点

要把会话历史真正存下来（文件、Redis、数据库），不能直接存 Python 对象，需要先转成字典：

| 函数 | 方向 | 输入 | 输出 |
| --- | --- | --- | --- |
| `messages_to_dict(history.messages)` | 序列化 | 消息对象列表 | 可 JSON 化的 dict 列表 |
| `messages_from_dict(dicts)` | 反序列化 | dict 列表 | 消息对象列表 |

打印出的中间结构：

```text
[{'type': 'human', 'data': {'content': 'hi!', 'additional_kwargs': {}}},
 {'type': 'ai', 'data': {'content': 'whats up?', 'additional_kwargs': {}}}]
```

关键设计是 **`type` 与 `data` 分离**：`type` 决定反序列化时构造哪个消息类，`data` 承载内容。这保证了「存下来 → 读回来仍然是 `HumanMessage` / `AIMessage`」，而不是丢成纯文本。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「长期记忆：消息序列化」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md)
