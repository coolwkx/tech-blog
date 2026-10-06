---
article_id: kp-d2b374b21484dd20
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-1043063b962d
learning_sourceId: 1043063b962d
learning_order: 7
learning_objective: 理解并验证：Agents：让模型调用外部工具
---

# Agents：让模型调用外部工具

> **学习目标**：能够解释「Agents：让模型调用外部工具」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：大模型 API 与消息角色（见《05-大模型API与调用实践》）、embedding 与向量检索（见《07-向量数据库与Milvus》）。
>
> **所属主题**：-LangChain基础 · 关键机制

## 本次只学这一点

**为什么需要**：大模型虽然强大但有局限——**不能回答实时信息、处理数学逻辑问题仍非常初级**，
因此需要借助第三方工具（搜索引擎、数据库、计算器）辅助。

| 角色 | 职责 |
|---|---|
| `Agent` | 制定计划和思考下一步需要采取的行动 |
| `Tool` | 解决问题的工具 |
| `Toolkit` | 一些集成好的工具包 |
| `AgentExecutor` | 把代理和工具列表包装在一起，**迭代运行代理的循环，直到满足停止目标** |

```python
from langchain.agents import AgentType, initialize_agent, load_tools
tools = load_tools(["llm-math"], llm=llm) # "serpapi" 为实时联网搜索工具
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
print(agent.run("解以下方程：3x+4(x+2)=84，其中 x 为 3，请问 y 是多少？"))
```

常见内置工具：`python_repl`（执行 Python）、`GoogleSearch`/`BingSearch`、
`GoogleSerperAPI`（从 Google 搜索提取数据）、`llm-math`、`wikipedia`、`arxiv`、`requests_get/post`。
可用 `get_all_tool_names` 列出全部工具名。

**Agent 的本质**：把模型输出从**文本**变成**动作**（调用哪个工具、传什么参数），
再把工具的**观察结果**塞回上下文循环——这正是《11-AI-Agent开发》与 Function Calling 的雏形。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Agents：让模型调用外部工具」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)
