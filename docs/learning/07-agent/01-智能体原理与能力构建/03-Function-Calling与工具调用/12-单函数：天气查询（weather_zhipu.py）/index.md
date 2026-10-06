---
article_id: kp-ac0e4b8d16e4df1a
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-9a522c2cae70
learning_sourceId: 9a522c2cae70
learning_order: 11
learning_objective: 理解并验证：单函数：天气查询（weather_zhipu.py）
---

# 单函数：天气查询（weather_zhipu.py）

> **学习目标**：能够解释「单函数：天气查询（weather_zhipu.py）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的 Action 环节、[../llm/05-大模型API与调用实践.md](../../../../../06-llm/06-提示工程/05-大模型API与调用实践.md) 的 `messages` 角色约定。
>
> **所属主题**：-Function-Calling与工具调用 · 可运行示例

## 本次只学这一点

**依赖**：`pip install zhipuai requests python-dotenv`；环境变量 `ZHIPU_API_KEY`。

```python
"""多函数 Function Calling：先查航班号，再根据航班号查票价。

依赖：标准库。真实调用模型时参考 3.1 的 chat_completion_request。
"""

import json

plane_number = {
"北京": {"广州": "356", "深圳": "126", "郑州": "1123"},
"郑州": {"北京": "1123", "天津": "3661"},
}

def get_plane_number(date: str, start: str, end: str):
    """根据始发地、目的地和日期，查询对应日期的航班号"""
    destinations = plane_number.get(start)
    if not destinations or end not in destinations:
        return {"error": "未查询到 %s → %s 的航班" % (start, end)}
    number = destinations[end]
    return {"date": date, "number": number}

def get_ticket_price(date: str, number: str):
    """查询某航班在某日的价格"""
    price_table = {"1123": "668", "356": "520", "126": "430"}
    if number not in price_table:
        return {"error": "未查询到航班 %s 的票价" % number}
    return {"ticket_price": price_table[number]}

FUNCTION_MAP = {
"get_plane_number": get_plane_number,
"get_ticket_price": get_ticket_price,
}

tools = [
{
"type": "function",
"function": {
"name": "get_plane_number",
"description": "根据始发地、目的地和日期，查询对应日期的航班号",
"parameters": {
"type": "object",
"properties": {
"start": {"type": "string", "description": "出发地"},
"end": {"type": "string", "description": "目的地"},
"date": {"type": "string", "description": "日期"},
},
"required": ["start", "end", "date"],
},
},
},
{
"type": "function",
"function": {
"name": "get_ticket_price",
"description": "查询某航班在某日的价格",
"parameters": {
"type": "object",
"properties": {
"number": {"type": "string", "description": "航班号"},
"date": {"type": "string", "description": "日期"},
},
"required": ["number", "date"],
},
},
},
]

def parse_function_call(model_response):
    """把模型回复里的所有 tool_call 都执行掉，返回结果列表"""
    results = []
    message = model_response.choices[0].message
    if not message.tool_calls:
        return [""]
    for tool_call in message.tool_calls:
        args = json.loads(tool_call.function.arguments)
        func = FUNCTION_MAP.get(tool_call.function.name)
        results.append(func(**args) if func else {"error": "未知函数"})
        return results

    if __name__ == "__main__":
        # 手工模拟「模型已经决定调用 get_plane_number」这一轮
        first = get_plane_number(date="2024-04-02", start="郑州", end="北京")
        print("第 1 轮结果:", json.dumps(first, ensure_ascii=False))
        # 把上一轮结果里的航班号喂给第二个工具（真实场景由模型自动完成这步）
        second = get_ticket_price(date="2024-04-02", number=first["number"])
        print("第 2 轮结果:", json.dumps(second, ensure_ascii=False))
```

预期输出（结果展示）：

```text
北京市当前的天气情况。今天是星期一，北京的天气情况是晴天，
最高气温为33℃，最低气温为17℃。请注意天气变化，做好防晒和保暖措施。
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「单函数：天气查询（weather_zhipu.py）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)
