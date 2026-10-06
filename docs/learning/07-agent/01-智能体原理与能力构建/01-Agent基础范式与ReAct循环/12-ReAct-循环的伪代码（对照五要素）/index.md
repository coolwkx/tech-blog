---
article_id: kp-ccc5b21b49d8371d
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-0b49eeb55140
learning_sourceId: 0b49eeb55140
learning_order: 11
learning_objective: 理解并验证：ReAct 循环的伪代码（对照五要素）
---

# ReAct 循环的伪代码（对照五要素）

> **学习目标**：能够解释「ReAct 循环的伪代码（对照五要素）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[../llm/05-大模型API与调用实践.md](../../../../../06-llm/06-提示工程/05-大模型API与调用实践.md) 的消息角色与 API 调用、[../llm/04-提示词工程.md](../../../../../06-llm/06-提示工程/04-提示词工程.md) 的 system prompt 用法、本目录 [02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)。
>
> **所属主题**：-Agent基础范式与ReAct循环 · 关键机制

## 本次只学这一点

```text
function run(goal):
 memory = [system_prompt, user(goal)]
 for step in 1..max_steps:
 thought, action, action_input = llm(memory, tools=TOOL_SCHEMAS)
 if action is None: # 模型认为可以直接回答
 return thought # 对应：Action 环节的「返回」
 observation = execute(action, action_input) # 观察环境
 memory.append(assistant(thought, action, action_input))
 memory.append(tool(observation)) # 对应：Memory 环节
 return "达到最大步数仍未完成"
```

这段伪代码里的每个符号都能对回：`llm(memory, tools=...)` 是 LLM + Prompt；`execute` 是 Action；`memory.append()` 是 Memory；`for step in ...` 是 Planning 的展开形式。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「ReAct 循环的伪代码（对照五要素）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md)
