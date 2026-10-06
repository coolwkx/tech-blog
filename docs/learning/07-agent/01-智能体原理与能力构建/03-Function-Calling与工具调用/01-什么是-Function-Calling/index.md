---
article_id: kp-0a1c6a885497218f
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-9a522c2cae70
learning_sourceId: 9a522c2cae70
learning_order: 0
learning_objective: 理解并验证：什么是 Function Calling
---

# 什么是 Function Calling

> **学习目标**：能够解释「什么是 Function Calling」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的 Action 环节、[../llm/05-大模型API与调用实践.md](../../../../../06-llm/06-提示工程/05-大模型API与调用实践.md) 的 `messages` 角色约定。
>
> **所属主题**：-Function-Calling与工具调用 · 核心概念

## 本次只学这一点

2023 年 6 月 13 日 OpenAI 公布了 Function Calling（函数调用）功能，其定义是：

> 在语言模型中集成外部功能或 API 的调用能力，这意味着模型可以在生成文本的过程中调用外部函数或服务，获取额外的数据或执行特定的任务。

实际语义要比字面更谨慎：**模型不会执行函数，只是返回函数的参数**；开发者利用模型输出的参数在自己应用里调用函数（标准写法即如此表述）。所以 Function Calling 的准确理解是「**结构化输出 + 工具路由**」，不是「让模型去跑代码」。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「什么是 Function Calling」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)
