---
article_id: kp-5b9b4965ed76b005
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-3d8f081f5ed3
learning_sourceId: 3d8f081f5ed3
learning_order: 11
learning_objective: 理解并验证：用 Agent 解方程（agents_apply.py）
---

# 用 Agent 解方程（agents_apply.py）

> **学习目标**：能够解释「用 Agent 解方程（agents_apply.py）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的工具协议、[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的 ReAct 结构、[../llm/08-LangChain基础.md](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)。
>
> **所属主题**：-LangChain与工具编排 · 可运行示例

## 本次只学这一点

**依赖**：`pip install langchain langchain-community ollama`；本地需先 `ollama pull qwen2.5:7b`。`llm-math` 工具还需要 `pip install numexpr`。

```python
"""LangChain Agent 示例：让代理自行选择数学工具解方程。

依赖：pip install langchain langchain-community ollama numexpr
前置：ollama pull qwen2.5:7b
"""

from langchain.agents import AgentType, initialize_agent
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_community.llms import Ollama

# 实例化大模型
llm = Ollama(model="qwen2.5:7b")

# 设置工具："serpapi" 实时联网搜索工具、"llm-math" 数学计算工具
tools = load_tools(["llm-math"], llm=llm)

# 实例化代理 Agent：返回 AgentExecutor 类型的实例
agent = initialize_agent(
 tools,
 llm,
 agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
 verbose=True,
 handle_parsing_errors=True, # 本地模型格式不稳定时的必备兜底
)

prompt_template = """解以下方程：3x + 4(x + 2) - 84 = y; 其中x为3，请问y是多少？"""

result = agent.run(prompt_template)
print("result-->", result)
```

`verbose=True` 会打印完整的 ReAct 轨迹（Thought / Action / Action Input / Observation），这是排查「代理为什么选了错的工具」的第一手材料。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「用 Agent 解方程（agents_apply.py）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md)
