---
article_id: kp-316e5e3bf54dbf6d
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-0b49eeb55140
learning_sourceId: 0b49eeb55140
learning_order: 13
learning_objective: 理解并验证：终止条件设计
---

# 终止条件设计

> **学习目标**：能够解释「终止条件设计」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[../llm/05-大模型API与调用实践.md](../../../../../06-llm/06-提示工程/05-大模型API与调用实践.md) 的消息角色与 API 调用、[../llm/04-提示词工程.md](../../../../../06-llm/06-提示工程/04-提示词工程.md) 的 system prompt 用法、本目录 [02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)。
>
> **所属主题**：-Agent基础范式与ReAct循环 · 关键机制

## 本次只学这一点

Agent 循环必须显式设置退出条件，否则会陷入「反复调用同一工具」的死循环。工程上常用的四道闸门：

| 闸门 | 做法 | 作用 |
| --- | --- | --- |
| 显式终态 | 定义 `Final Answer` / `finish` 动作 | 让模型有明确的「停止」出口 |
| 步数上限 | `max_iterations`（LangChain 默认有类似参数） | 兜底，防止无限循环 |
| 超时 | 整体 wall-clock 超时 | 防止单步工具卡死拖垮整条链路 |
| 重复检测 | 比较连续两步的 Action + Action Input | 检测原地打转，触发人工介入 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「终止条件设计」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md)
