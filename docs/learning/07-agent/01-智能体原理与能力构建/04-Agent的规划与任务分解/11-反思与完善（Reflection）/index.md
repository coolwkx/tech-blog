---
article_id: kp-91a056d3d3f9a9cf
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-21455d0f58d4
learning_sourceId: 21455d0f58d4
learning_order: 10
learning_objective: 理解并验证：反思与完善（Reflection）
---

# 反思与完善（Reflection）

> **学习目标**：能够解释「反思与完善（Reflection）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的五要素、[03-LangChain与工具编排](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md) 的 Task/Crew、[06-RAG作为Agent的知识获取手段](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md) 的检索流程。
>
> **所属主题**：-Agent的规划与任务分解 · 关键机制

## 本次只学这一点

在 Agent 能力图中列出了「反思与完善」与「代码解释器」。反思的本质是**把执行结果回灌给模型，要求它检查并修订**：

| 形式 | 做法 | 的对应 |
| --- | --- | --- |
| 解析失败重试 | 把「格式错误」作为 Observation 回灌 | LangChain `handle_parsing_errors=True`（见 [03](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md) 常见坑） |
| 结果校验 | 工具返回 error 字段，模型据此重规划 | Function Call 的 `{"error": ...}` 返回模式 |
| 自我批评 | 让第二个 Agent 审阅第一个的输出 | CrewAI 「内容编辑」Agent 检查语法与格式 |

CrewAI 项目里「作家写 → 编辑改 → 信使发」的流水线，本质上就是一个**角色化的反思链**：每个下游角色都是对上游输出的校验器。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/02-工具与规划/04-Agent的规划与任务分解.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「反思与完善（Reflection）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/02-工具与规划/04-Agent的规划与任务分解.md)
