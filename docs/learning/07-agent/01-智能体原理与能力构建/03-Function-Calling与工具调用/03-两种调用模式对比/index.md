---
article_id: kp-6e83994377c61ca0
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-9a522c2cae70
learning_sourceId: 9a522c2cae70
learning_order: 2
learning_objective: 理解并验证：两种调用模式对比
---

# 两种调用模式对比

> **学习目标**：能够解释「两种调用模式对比」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的 Action 环节、[../llm/05-大模型API与调用实践.md](../../../../../06-llm/06-提示工程/05-大模型API与调用实践.md) 的 `messages` 角色约定。
>
> **所属主题**：-Function-Calling与工具调用 · 核心概念

## 本次只学这一点

**没有 Function Call 时**，构建 AI 应用的模式非常简单：用户（Client）发请求给服务（ChatServer）；ChatServer 给模型提示词；重复执行。

**有 Function Call 时**，模式变复杂，给出四个主要步骤：

| 步骤 | 谁参与 | 发生了什么 |
| --- | --- | --- |
| 1 | Client → ChatServer | 用户发请求，同时带上 `prompt` 和 `functions`（函数定义） |
| 2 | ChatServer → GPT | 模型根据用户的 prompt，判断用**普通文本**还是**函数调用格式**响应 |
| 3 | ChatServer | 如果是函数调用格式，ChatServer 执行这个函数，并把结果返回给 GPT |
| 4 | GPT → Client | 模型使用提供的数据，用连贯的文本响应 |

差异可以用一张表概括：

| 维度 | 无 Function Call | 有 Function Call |
| --- | --- | --- |
| 请求内容 | `prompt` | `prompt` + `tools`（函数定义） |
| 模型输出 | 纯文本 | 纯文本 **或** 结构化调用请求 |
| 交互轮次 | 1 轮 | 至少 2 轮（调用 + 汇总） |
| 事实来源 | 模型参数记忆 | 外部系统实时返回 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「两种调用模式对比」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)
