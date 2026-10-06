---
article_id: kp-d0ac262b859b14a6
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-0b49eeb55140
learning_sourceId: 0b49eeb55140
learning_order: 10
learning_objective: 理解并验证：ReAct：把「想」和「做」交替进行
---

# ReAct：把「想」和「做」交替进行

> **学习目标**：能够解释「ReAct：把「想」和「做」交替进行」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[../llm/05-大模型API与调用实践.md](../../../../../06-llm/06-提示工程/05-大模型API与调用实践.md) 的消息角色与 API 调用、[../llm/04-提示词工程.md](../../../../../06-llm/06-提示工程/04-提示词工程.md) 的 system prompt 用法、本目录 [02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)。
>
> **所属主题**：-Agent基础范式与ReAct循环 · 关键机制

## 本次只学这一点

> **说明**：这里只在 LangChain 的 `zero-shot-react-description` 代理类型里提到「利用 ReAct 框架根据工具的描述来决定使用哪个工具」，未展开 ReAct 细节，本小节为通用知识补充。

ReAct（Reasoning + Acting，arXiv:2210.03629）的核心思想是让模型在**同一条轨迹里交替产出推理（Reasoning trace）与动作（Action）**，再用环境的反馈（Observation）纠正下一步推理。它的轨迹格式是：

```text
Thought: 我需要先知道北京今天的天气
Action: get_current_weather
Action Input: {"location": "北京"}
Observation: {"location": "北京", "temperature": "33℃", "type": "晴"}
Thought: 我已经拿到天气数据，可以回答用户了
Final Answer: 北京今天晴，最高 33℃，最低 17℃。
```

三个关键点：

1. **Thought 是给模型自己看的**，不执行，允许模型「打草稿」，这也是为什么重复推理能提升准确率；
2. **Action 的合法值来自工具描述（tool description）**，所以工具描述写得清楚，等于给模型限定了解空间；
3. **Observation 必须原样回填**，不能被模型改写——它是唯一的事实来源。

对比其它范式：

| 范式 | 特点 | 典型缺陷 |
| --- | --- | --- |
| Chain-of-Thought（CoT） | 只推理、不行动 | 无法获取外部信息，事实错误无法纠正 |
| Act-only | 只行动、不推理 | 动作选择盲目，容易连续调用错误工具 |
| **ReAct** | 推理与行动交替 | 轨迹变长，token 成本与延迟上升 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「ReAct：把「想」和「做」交替进行」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md)
