---
article_id: kp-5332f418bad5f49d
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-f10d60d670aa
learning_sourceId: f10d60d670aa
learning_order: 5
learning_objective: 理解并验证：Function Call 完整两轮调用（可运行骨架）
---

# Function Call 完整两轮调用（可运行骨架）

> **学习目标**：能够解释「Function Call 完整两轮调用（可运行骨架）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：本目录 01~11 篇。
>
> **所属主题**：-大模型面试题库 · 可运行示例

## 本次只学这一点

```python
# 依赖：pip install openai>=1.0
# 关键：模型只返回「函数名 + 参数」，真正的函数执行发生在你的代码里
import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# ---------- 第一步：定义真实函数 ----------
def get_current_weather(location: str) -> str:
    """得到给定地址的当前天气信息（示例返回固定数据）"""
    weather_info = {
    "location": location, "type": "晴",
    "high_temperature": "33", "low_temperature": "17", "week": "星期一",
    }
    return json.dumps(weather_info, ensure_ascii=False)

AVAILABLE_FUNCTIONS = {"get_current_weather": get_current_weather}

# ---------- 第二步：把函数定义（JSON Schema）交给模型 ----------
tools = [
{
"type": "function",
"function": {
"name": "get_current_weather",
"description": "获取给定位置的当前天气",
"parameters": {
"type": "object",
"properties": {
"location": {"type": "string", "description": "城市或区，例如北京、海淀"},
},
"required": ["location"],
},
},
}
]

# ---------- 第三步：两轮调用 ----------
def main():
    messages = [
    {"role": "system",
    "content": "你是一个天气播报小助手，你需要根据用户提供的地址来回答当地的天气情况，"
    "如果用户提供的问题具有不确定性，不要自己编造内容，提示用户明确输入"},
    {"role": "user", "content": "今天北京的天气如何"},
    ]

    # 第 1 轮：模型决定是否调用函数
    first = client.chat.completions.create(
    model="gpt-4o-mini", messages=messages, tools=tools, tool_choice="auto"
    )
    assistant_message = first.choices[0].message
    messages.append(assistant_message.model_dump())

    if assistant_message.tool_calls:
        tool_call = assistant_message.tool_calls[0]
        function_name = tool_call.function.name # 模型选中的函数名
        function_args = json.loads(tool_call.function.arguments) # 模型填好的参数
        print(f"[模型请求调用] {function_name}({function_args})")

        # 第 2 步：由「我们的代码」真正执行函数
        function_response = AVAILABLE_FUNCTIONS[function_name](**function_args)

        # 第 3 步：把函数结果作为 tool 消息送回模型
        messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id, # 必须与本次调用 id 对应
        "name": function_name,
        "content": function_response,
        })

        # 第 2 轮：模型结合函数结果生成自然语言回答
        last = client.chat.completions.create(
        model="gpt-4o-mini", messages=messages, tools=tools, tool_choice="auto"
        )
        print("[最终回答]", last.choices[0].message.content)
    else:
        print("[直接回答]", assistant_message.content)

        if __name__ == "__main__":
            main()
```

**六步流程（面试要能背下来）**：
① 定义函数（真实 API／工具，或模拟函数）→
② 把函数定义作为 `tools` 参数提供给模型 →
③ 模型生成函数调用 JSON（含函数名与参数值）→
④ 后端系统根据 JSON 调用相应函数 →
⑤ 把函数结果作为额外上下文返回给模型 →
⑥ 模型综合原始查询与函数结果，生成最终输出。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/09-面试专题/12-大模型面试题库.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Function Call 完整两轮调用（可运行骨架）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/09-面试专题/12-大模型面试题库.md)
