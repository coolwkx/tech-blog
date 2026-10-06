---
article_id: kp-06e3c4d4ff39db3f
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-21455d0f58d4
learning_sourceId: 21455d0f58d4
learning_order: 14
learning_objective: 理解并验证：策略选择器（对应 strategy_selector.py）
---

# 策略选择器（对应 strategy_selector.py）

> **学习目标**：能够解释「策略选择器（对应 strategy_selector.py）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的五要素、[03-LangChain与工具编排](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md) 的 Task/Crew、[06-RAG作为Agent的知识获取手段](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md) 的检索流程。
>
> **所属主题**：-Agent的规划与任务分解 · 可运行示例

## 本次只学这一点

**依赖**：`pip install openai langchain python-dotenv`；环境变量 `DASHSCOPE_API_KEY`。

```python
"""检索策略选择器：让 LLM 在四种增强策略中选择一个（只返回策略名）。

依赖：pip install openai langchain python-dotenv
环境变量：DASHSCOPE_API_KEY
"""

import os

from langchain.prompts import PromptTemplate
from openai import OpenAI

STRATEGIES = ["直接检索", "假设问题检索", "子查询检索", "回溯问题检索"]

STRATEGY_PROMPT = PromptTemplate(
template="""
你是一个智能助手，负责分析用户查询 {query}，并从以下四种检索增强策略中选择一个最适合的策略，
直接返回策略名称，不需要解释过程。

1. **直接检索**：对用户查询直接进行检索，不进行任何增强处理。
适用场景：查询意图明确，需要从知识库中检索特定信息的问题。
2. **假设问题检索（HyDE）**：使用 LLM 生成一个假设的答案，然后基于假设答案进行检索。
适用场景：查询较为抽象，直接检索效果不佳的问题。
3. **子查询检索**：将复杂的用户查询拆分为多个简单的子查询，分别检索并合并结果。
适用场景：查询涉及多个实体或方面，需要分别检索不同信息的问题。
4. **回溯问题检索**：将复杂的用户查询转化为更基础、更易于检索的问题，然后进行检索。
适用场景：查询较为复杂，需要简化后才能有效检索的问题。

根据用户查询 {query}，直接返回最适合的策略名称，例如 "直接检索"。不要输出任何分析过程或其他内容。
""",
input_variables=["query"],
)

def select_strategy(query, model="qwen-plus"):
    client = OpenAI(
    api_key=os.environ["DASHSCOPE_API_KEY"],
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    try:
        completion = client.chat.completions.create(
        model=model,
        messages=[
        {"role": "system", "content": "你是一个有用的助手。"},
        {"role": "user", "content": STRATEGY_PROMPT.format(query=query)},
        ],
        temperature=0.1, # 压低随机性，把生成压成一次受限分类
        )
        raw = completion.choices[0].message.content if completion.choices else ""
    except Exception as exc: # 规划器失败必须有安全默认值
        print("策略选择失败，回退到直接检索: %s" % exc)
        return "直接检索"

    strategy = raw.strip()
    if strategy not in STRATEGIES: # 白名单校验，防止模型自由发挥
        print("模型返回了非法策略 %r，回退到直接检索" % strategy)
        return "直接检索"
    return strategy

if __name__ == "__main__":
    for q in [
    "人工智能方向学费是多少？",
    "人工智能在教育领域的应用有哪些？",
    "比较 Milvus 和 Zilliz Cloud 的优缺点。",
    ]:
        print("%s -> %s" % (q, select_strategy(q)))
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/02-工具与规划/04-Agent的规划与任务分解.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「策略选择器（对应 strategy_selector.py）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/02-工具与规划/04-Agent的规划与任务分解.md)
