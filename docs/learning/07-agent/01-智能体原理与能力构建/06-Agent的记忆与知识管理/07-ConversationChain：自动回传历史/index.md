---
article_id: kp-8fb053dafce98cdc
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-3dbf2b7f4206
learning_sourceId: 3dbf2b7f4206
learning_order: 6
learning_objective: 理解并验证：ConversationChain：自动回传历史
---

# ConversationChain：自动回传历史

> **学习目标**：能够解释「ConversationChain：自动回传历史」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[03-LangChain与工具编排](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md) 的 Memory 组件、[06-RAG作为Agent的知识获取手段](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md) 的向量检索、[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的 messages 角色约定。
>
> **所属主题**：-Agent的记忆与知识管理 · 关键机制

## 本次只学这一点

用 `ConversationChain` 演示了记忆的自动化：

```text
llm = Ollama(model="qwen2.5:7b")
conversation = ConversationChain(llm=llm)
conversation.predict(input="小明有1只猫")
conversation.predict(input="小刚有2只狗")
conversation.predict(input="小明和小刚一共有几只宠物?")
# → 小明和小刚总共有3只宠物。小明有1只猫，小刚有2只狗。
```

第三轮能答对，说明 `ConversationChain` 在内部维护了一份 Memory，并在每次 `predict` 时把历史自动注入 prompt。对照 [03](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md) 的 `conversational-react-description` 代理类型——后者正是「ReAct + 记忆」的组合，用于多轮对话中调用工具。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「ConversationChain：自动回传历史」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md)
