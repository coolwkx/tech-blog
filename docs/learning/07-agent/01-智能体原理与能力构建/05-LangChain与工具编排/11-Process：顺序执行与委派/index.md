---
article_id: kp-b75b229fc43b51dd
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-3d8f081f5ed3
learning_sourceId: 3d8f081f5ed3
learning_order: 10
learning_objective: 理解并验证：Process：顺序执行与委派
---

# Process：顺序执行与委派

> **学习目标**：能够解释「Process：顺序执行与委派」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的工具协议、[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的 ReAct 结构、[../llm/08-LangChain基础.md](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)。
>
> **所属主题**：-LangChain与工具编排 · 关键机制

## 本次只学这一点

| 概念 | 取值 | 含义 |
| --- | --- | --- |
| `Process.sequential` | 顺序 | 按 tasks 列表顺序执行，**上一个任务的结果会作为附加内容传递给下一个任务** |
| `allow_delegation` | True/False | 该 Agent 是否可以把子任务委派给其他 Agent |
| `verbose` | True / 1 / 2 | 是否打印执行过程（排查多 Agent 协作问题时必开） |

`crew.kickoff()` 启动整条流水线，返回值是最终结果。顺序流程的信息传递依赖 Task 的 `description` + 上一步输出，因此在 Task 描述里明确写「你最后的答案必须是……」这类输出契约非常重要——三个 Task 的 description 都写了输出要求。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Process：顺序执行与委派」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md)
