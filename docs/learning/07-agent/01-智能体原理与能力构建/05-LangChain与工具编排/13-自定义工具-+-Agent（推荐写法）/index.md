---
article_id: kp-78bc1ffe1f5e6677
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-3d8f081f5ed3
learning_sourceId: 3d8f081f5ed3
learning_order: 12
learning_objective: 理解并验证：自定义工具 + Agent（推荐写法）
---

# 自定义工具 + Agent（推荐写法）

> **学习目标**：能够解释「自定义工具 + Agent（推荐写法）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的工具协议、[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的 ReAct 结构、[../llm/08-LangChain基础.md](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)。
>
> **所属主题**：-LangChain与工具编排 · 可运行示例

## 本次只学这一点

**依赖**：`pip install langchain langchain-community`（`@tool` 来自 `langchain_core.tools`）。

```python
"""用 @tool 注册自定义工具，交给 Agent 编排。

依赖：pip install langchain langchain-community
"""

from langchain.agents import AgentType, initialize_agent
from langchain_community.llms import Ollama
from langchain_core.tools import tool

@tool("查询本地商品库存")
def query_stock(sku: str) -> str:
    """输入商品 SKU，返回当前库存数量。SKU 形如 'A1001'。"""
    fake_db = {"A1001": 12, "A1002": 0, "A1003": 47}
    if sku not in fake_db:
        return "未找到 SKU: %s" % sku
    return "SKU %s 当前库存 %d 件" % (sku, fake_db[sku])

@tool("按单价与数量计算总价")
def calc_total(price: float, quantity: int) -> str:
    """输入单价与数量，返回总价（保留两位小数）。"""
    return "总价：%.2f 元" % (price * quantity)

llm = Ollama(model="qwen2.5:7b")
tools = [query_stock, calc_total]

agent = initialize_agent(
tools,
llm,
agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
verbose=True,
handle_parsing_errors=True,
)

if __name__ == "__main__":
    print(agent.run("A1003 还有多少库存？如果单价 19.9 元，全部买下要多少钱？"))
```

`@tool` 装饰器的第一个参数是**工具名**，函数 docstring 是**工具描述**——两者都会进入提示词，所以 docstring 要写清楚「输入是什么、返回什么、格式要求」。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「自定义工具 + Agent（推荐写法）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md)
