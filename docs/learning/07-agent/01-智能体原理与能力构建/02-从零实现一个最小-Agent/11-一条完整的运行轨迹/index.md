---
article_id: kp-e856e425126fad7f
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-7f36aafe1891
learning_sourceId: 7f36aafe1891
learning_order: 10
learning_objective: 理解并验证：一条完整的运行轨迹
---

# 一条完整的运行轨迹

> **学习目标**：能够解释「一条完整的运行轨迹」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 的 AST 与异常处理、JSON Schema 基本概念、LLM 的采样与上下文窗口、[ReAct / Plan-and-Execute / Reflexion 的术语定义](../../../../../07-agent/90-cheatsheet/glossary.md)
>
> **所属主题**：从零实现一个最小 Agent · 深入机制

## 本次只学这一点

把 `mock_llm` 塞进 `MiniAgent` 并开启 `verbose=True`，实际输出如下（逐字来自运行结果）：

```text
--- step 1 ---
Thought: 这是算术题，交给 calculator。
Action: calculator
Action Input: {"expression": "(1250 + 430) * 3 / 4"}
Observation: (1250 + 430) * 3 / 4 = 1260

--- step 2 ---
Thought: 数字算完了，还差 ReAct 与 Reflexion 的区别，去本地知识库检索。
Action: search
Action Input: {"query": "ReAct Reflexion", "top_k": 2}
Observation: [1] react: ReAct (Yao et al., 2022)：交错输出 Thought/Action/Observation，把推理与工具调用串成循环。
[2] reflexion: Reflexion (Shinn et al., 2023)：失败后生成语言化反思，写入下一轮记忆再重试。

--- step 3 ---
Thought: 计算和检索都拿到了，可以收尾。
Final Answer: (1250+430)*3/4 = 1260。ReAct 是交错推理与行动，Reflexion 是在失败后生成语言化反思再重试。
```

三个特征值得盯着看：**第一，step 1 的 Thought 与 Action 并不一一对应**，Thought 只是「要说点什么」的槽位，真正的控制信号在 `Action` 那一行，所以 trace 必须把两者都记下来。**第二，`top_k` 从未出现在用户问题里**，它是模型照着 JSON Schema 自己补出来的——工具的参数定义实际上在替模型做输入设计。**第三，step 3 没有 Observation**，终止步骤不产生新信息，它的输出直接就是返回值。

再看终止条件被触发时的轨迹。把假模型换成固定脚本，让它连续三次发同一个动作：

```text
step 1: Action: read_file Action Input: {"path": "config.yaml"}
 Observation: ERROR: 文件不存在或不是普通文件：config.yaml
step 2: （同一动作）Observation: ... [系统] 这是第 2 次执行完全相同的动作，请换一个动作或直接给 Final Answer。
step 3: （同一动作）-> [提前终止] 同一动作重复 3 次，判定为死循环。
```

注意 step 2 那句 `[系统]` 提示是拼进 observation 里的，也就是**把工程约束伪装成环境反馈**。这比在代码里直接 raise 更有效，因为模型会把它当成需要处理的输入，而不是一个中断。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/01-基础范式/01-从零实现一个最小Agent.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「一条完整的运行轨迹」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/01-基础范式/01-从零实现一个最小Agent.md)
