---
article_id: kp-730c62ea48af0ac3
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-7f36aafe1891
learning_sourceId: 7f36aafe1891
learning_order: 8
learning_objective: 理解并验证：接到真实的 OpenAI 兼容 API
---

# 接到真实的 OpenAI 兼容 API

> **学习目标**：能够解释「接到真实的 OpenAI 兼容 API」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 的 AST 与异常处理、JSON Schema 基本概念、LLM 的采样与上下文窗口、[ReAct / Plan-and-Execute / Reflexion 的术语定义](../../../../../07-agent/90-cheatsheet/glossary.md)
>
> **所属主题**：从零实现一个最小 Agent · 深入机制

## 本次只学这一点

`llm` 是唯一的注入点，换成任何服务都只改这一个函数。**运行下面这段需要 API key**；前面那份实现本身不需要任何 key 就能读懂（见 4.7 的离线跑法）。

```python
import os
from openai import OpenAI # pip install openai

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"],
 base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))

def llm(prompt: str) -> str:
 """把 MiniAgent 的 llm 接口接到任意 OpenAI 兼容服务上。"""
 response = client.chat.completions.create(
 model=os.getenv("MODEL", "gpt-4o-mini"),
 messages=[{"role": "user", "content": prompt}],
 temperature=0, # Agent 场景几乎总是 0：动作要可复现、可回放
 max_tokens=512,
 )
 return response.choices[0].message.content or ""

agent = MiniAgent(llm=llm, registry=build_registry("."), max_steps=8)
print(agent.run("帮我算一下 (1250 + 430) * 3 / 4 是多少"))
```

两个容易忽略的点：生产上应该发 `messages` 列表而不是把整段历史拼成一个字符串，这样能利用 prompt caching 省钱；`max_tokens` 要留够 `Action Input` 的空间，截断在半句 JSON 上会让解析器白忙一轮。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/01-基础范式/01-从零实现一个最小Agent.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「接到真实的 OpenAI 兼容 API」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/01-基础范式/01-从零实现一个最小Agent.md)
