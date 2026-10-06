---
article_id: kp-e6dd412c9f974e4b
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-9a522c2cae70
learning_sourceId: 9a522c2cae70
learning_order: 8
learning_objective: 理解并验证：多函数与「链式调用」
---

# 多函数与「链式调用」

> **学习目标**：能够解释「多函数与「链式调用」」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的 Action 环节、[../llm/05-大模型API与调用实践.md](../../../../../06-llm/06-提示工程/05-大模型API与调用实践.md) 的 `messages` 角色约定。
>
> **所属主题**：-Function-Calling与工具调用 · 关键机制

## 本次只学这一点

的多函数示例（航班查询）展示了 Function Calling 的一个重要特性：**一次任务可以触发多轮调用**。

| 轮次 | 模型决定的动作 | 依赖关系 |
| --- | --- | --- |
| 第 1 轮 | 调 `get_plane_number(date, start, end)` | 用户直接给出了日期与起止地 |
| 第 2 轮 | 调 `get_ticket_price(date, number)` | `number` 来自第 1 轮的返回值 `1123` |
| 第 3 轮 | 生成最终答复 | 「2024年4月2日，郑州到北京的航班号为1123，票价为668元」 |

这就是 [01](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 里 ReAct 的 Observation 回填机制在 API 层的体现：**第 1 轮的结构化结果成为第 2 轮的输入条件**，模型自己完成了参数传递。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「多函数与「链式调用」」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)
