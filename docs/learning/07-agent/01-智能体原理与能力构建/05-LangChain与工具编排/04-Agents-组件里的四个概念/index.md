---
article_id: kp-40a5380efa3ff799
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-3d8f081f5ed3
learning_sourceId: 3d8f081f5ed3
learning_order: 3
learning_objective: 理解并验证：Agents 组件里的四个概念
---

# Agents 组件里的四个概念

> **学习目标**：能够解释「Agents 组件里的四个概念」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的工具协议、[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的 ReAct 结构、[../llm/08-LangChain基础.md](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)。
>
> **所属主题**：-LangChain与工具编排 · 核心概念

## 本次只学这一点

| 概念 | 英文 | 职责 |
| --- | --- | --- |
| 代理 | Agent | 制定计划和思考下一步需要采取的行动；暴露接口接收用户输入 |
| 工具 | Tool | 解决问题的具体能力，第三方服务集成（计算、搜索、代码执行等） |
| 工具包 | Toolkit | 一些集成好了的代理包，例如 `create_csv_agent` 可以直接解读 csv 文件 |
| 代理执行器 | AgentExecutor | 将代理和工具列表包装在一起，负责**迭代运行代理的循环**，直到满足停止的标准；返回 `AgentAction` 或 `AgentFinish` |

`initialize_agent(tools, llm, agent=..., verbose=True)` 返回的就是 `AgentExecutor` 实例，`agent.run(prompt)` 触发这个循环。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Agents 组件里的四个概念」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md)
