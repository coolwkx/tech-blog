---
article_id: kp-c6820b89648b4c91
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-0b49eeb55140
learning_sourceId: 0b49eeb55140
learning_order: 12
learning_objective: 理解并验证：从对话机器人到 Agent：医疗问诊机器人的位置
---

# 从对话机器人到 Agent：医疗问诊机器人的位置

> **学习目标**：能够解释「从对话机器人到 Agent：医疗问诊机器人的位置」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[../llm/05-大模型API与调用实践.md](../../../../../06-llm/06-提示工程/05-大模型API与调用实践.md) 的消息角色与 API 调用、[../llm/04-提示词工程.md](../../../../../06-llm/06-提示工程/04-提示词工程.md) 的 system prompt 用法、本目录 [02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)。
>
> **所属主题**：-Agent基础范式与ReAct循环 · 关键机制

## 本次只学这一点

的 GPT2 医疗问诊机器人是一个**对话式 Agent 的雏形**：

- 数据处理把一轮对话拼成 `[CLS] 句子1 [SEP] 句子2 [SEP] …`（见 `data_preprocess/preprocess.py`），这就是最简单的记忆载体；
- 推理时把最近 `max_history_len` 轮历史依次拼进 `input_ids` 再送模型（见 [05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md)），这就是上下文记忆；
- 但它**没有工具、没有自主规划**，回复完全由模型的下一 token 概率决定。

对照 1.6 节的形式表，它落在「ChatGPT 对话式」那一栏：有记忆、无规划、无工具。理解这一点，就能明白 Agent 的两个增量到底是什么——**行动计划（Planning）**和**工具调用（Action）**。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「从对话机器人到 Agent：医疗问诊机器人的位置」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md)
