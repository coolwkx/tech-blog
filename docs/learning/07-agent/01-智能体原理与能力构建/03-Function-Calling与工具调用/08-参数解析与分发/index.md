---
article_id: kp-d2552eb6484f4bb3
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-9a522c2cae70
learning_sourceId: 9a522c2cae70
learning_order: 7
learning_objective: 理解并验证：参数解析与分发
---

# 参数解析与分发

> **学习目标**：能够解释「参数解析与分发」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的 Action 环节、[../llm/05-大模型API与调用实践.md](../../../../../06-llm/06-提示工程/05-大模型API与调用实践.md) 的 `messages` 角色约定。
>
> **所属主题**：-Function-Calling与工具调用 · 关键机制

## 本次只学这一点

`parse_response(response)` 的两段式写法（已修正原文拼写）：

```text
"""Function Calling 单一函数示例：查询实时天气。

依赖：pip install zhipuai requests python-dotenv
环境变量：ZHIPU_API_KEY
"""

import json
import os

import requests
from zhipuai import ZhipuAI

CHATGLM = "glm-4"

def get_current_weather(location):
 """得到给定地址的当前天气信息"""
 with open("./cityCode_use.json", "r", encoding="utf-8") as file:
 data = json.load(file) # 城市与编码对照表，形如 [{"市名": "北京", "编码": "101010100"}, ...]

 city_code = None
 for loc in data:
 if location == loc["市名"]:
 city_code = loc["编码"]
 break
 if not city_code:
 return json.dumps({"error": "未找到城市: %s" % location}, ensure_ascii=False)

 weather_url = "http://t.weather.itboy.net/api/weather/city/" + city_code
 response = requests.get(weather_url, timeout=10)
 result1 = json.loads(response.text) # 修正：原文使用 eval(response.text)
 forecast = result1["data"]["forecast"][0]

 weather_info = {
 "location": location,
 "type": forecast["type"],
 "week": forecast["week"],
 "high_temperature": forecast["high"],
 "low_temperature": forecast["low"],
 }
 return json.dumps(weather_info, ensure_ascii=False)

tools = [
 {
 "type": "function",
 "function": {
 "name": "get_current_weather",
 "description": "获取给定位置的当前天气",
 "parameters": {
 "type": "object",
 "properties": {
 "location": {"type": "string", "description": "城市或区，例如北京、海淀"}
 },
 "required": ["location"],
 },
 },
 }
]

available_functions = {"get_current_weather": get_current_weather}

def parse_response(response):
 """根据模型回复判断是否调用工具，返回工具执行结果"""
 result = []
 message = response.choices[0].message
 if message.tool_calls:
 for tool_call in message.tool_calls: # 修正：原文只取 [0]
 name = tool_call.function.name
 args = json.loads(tool_call.function.arguments)
 func = available_functions.get(name)
 if func is None:
 result.append(json.dumps({"error": "未知函数: %s" % name}, ensure_ascii=False))
 continue
 result.append(func(**args))
 return result

def chat_completion_request(messages, tools=None, tool_choice=None, model=CHATGLM):
 client = ZhipuAI(api_key=os.environ["ZHIPU_API_KEY"])
 try:
 return client.chat.completions.create(
 model=model, messages=messages, tools=tools, tool_choice=tool_choice
 )
 except Exception as exc:
 print("Unable to generate ChatCompletion response")
 print("Exception: %s" % exc)
 return None

def main():
 messages = [
 {
 "role": "system",
 "content": (
 "你是一个天气播报小助手，你需要根据用户提供的地址来回答当地的天气情况，"
 "如果用户提供的问题具有不确定性，不要自己编造内容，提示用户明确输入"
 ),
 },
 {"role": "user", "content": "今天北京的天气如何"},
 ]

 response = chat_completion_request(messages, tools=tools, tool_choice="auto")
 if response is None:
 return

 assistant_message = response.choices[0].message
 messages.append(assistant_message.model_dump()) # 关键：保留 tool_calls 上下文

 for tool_call, function_response in zip(assistant_message.tool_calls, parse_response(response)):
 messages.append({
 "role": "tool",
 "name": tool_call.function.name,
 "tool_call_id": tool_call.id,
 "content": function_response,
 })

 last_response = chat_completion_request(messages, tools=tools, tool_choice="auto")
 if last_response is not None:
 print(last_response.choices[0].message.content)

if __name__ == "__main__":
 main()
```

要点：

- `arguments` 是**字符串**（模型逐 token 生成的自然结果），必须 `json.loads`；
- 用一张 `available_functions = {"name": callable}` 注册表分发，比 `if/elif` 链更好扩展；
- 一个 `assistant` 消息可能带**多个** `tool_calls`（并行调用），只取 `[0]` 会静默丢调用——这是三段示例的共同缺陷，见 4. 常见坑。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「参数解析与分发」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)
