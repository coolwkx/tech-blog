---
article_id: kp-702ea0fe63fc100f
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-3d8f081f5ed3
learning_sourceId: 3d8f081f5ed3
learning_order: 8
learning_objective: 理解并验证：自定义工具：从 llm-math 到 @tool
---

# 自定义工具：从 llm-math 到 @tool

> **学习目标**：能够解释「自定义工具：从 llm-math 到 @tool」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的工具协议、[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的 ReAct 结构、[../llm/08-LangChain基础.md](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)。
>
> **所属主题**：-LangChain与工具编排 · 关键机制

## 本次只学这一点

内置工具覆盖不到业务逻辑时，需要注册自己的工具。在 CrewAI 项目中用 LangChain 的 `@tool` 装饰器实现（`custom_tools.py`）：

| 装饰器写法 | 注册出来的工具名 |
| --- | --- |
| `@tool("将文本写入文档中")` | `将文本写入文档中` |
| `@tool("发送文本到邮件")` | `发送文本到邮件` |

注意示例的一个细节：装饰器写在方法上时，`tools=[CustomTools.store_poesy_to_txt]` 这样按类属性引用，而不是 `CustomTools().store_poesy_to_txt`——因为 `@tool` 已经把函数对象转成了 BaseTool 实例。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「自定义工具：从 llm-math 到 @tool」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md)
