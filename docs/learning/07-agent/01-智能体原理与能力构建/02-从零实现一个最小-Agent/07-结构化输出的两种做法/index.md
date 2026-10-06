---
article_id: kp-2c74beeb407b70ca
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-7f36aafe1891
learning_sourceId: 7f36aafe1891
learning_order: 6
learning_objective: 理解并验证：结构化输出的两种做法
---

# 结构化输出的两种做法

> **学习目标**：能够解释「结构化输出的两种做法」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 的 AST 与异常处理、JSON Schema 基本概念、LLM 的采样与上下文窗口、[ReAct / Plan-and-Execute / Reflexion 的术语定义](../../../../../07-agent/90-cheatsheet/glossary.md)
>
> **所属主题**：从零实现一个最小 Agent · 深入机制

## 本次只学这一点

| 维度 | 文本协议（ReAct 的 Action/Action Input） | 原生 Function Calling |
| --- | --- | --- |
| 工具如何声明 | 工具清单写进 System Prompt 的纯文本 | 独立的 `tools` 参数，标准 JSON Schema |
| 模型输出什么 | 自由文本，需要正则或 JSON 二次解析 | 结构化的 `tool_calls` 数组，参数已是合法 JSON |
| 解析鲁棒性 | 差。围栏、全角冒号、多余解释、多行参数都可能让正则失配 | 好。由服务端约束解码保证，参数类型基本不会错 |
| 可观测性 | trace 里能看到完整 Thought，调试体验好 | 默认没有推理文本，需要模型额外支持 reasoning 字段 |
| 兼容性 | 任何模型都能用，不依赖服务端能力 | 需要模型与服务端同时支持该协议 |
| 典型坑 | 模型在参数里塞额外字段、把 JSON 写成 YAML | 模型漏参数、编造不存在的工具名、并行发起多个调用 |
| 适用场景 | 教学、原型、弱模型兜底、需要看推理过程 | 生产环境，尤其是工具多、参数结构复杂时 |

结论是「以 function calling 为主，文本协议作为降级通道」。但即使走 function calling，也**必须**保留三个校验：工具名在注册表里、必填参数齐全、参数类型能通过 JSON Schema。服务端保证的是「格式合法」，不是「语义正确」。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/01-基础范式/01-从零实现一个最小Agent.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「结构化输出的两种做法」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/01-基础范式/01-从零实现一个最小Agent.md)
