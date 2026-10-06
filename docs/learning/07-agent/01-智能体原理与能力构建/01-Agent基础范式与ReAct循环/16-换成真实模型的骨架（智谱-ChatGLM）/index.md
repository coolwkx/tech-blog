---
article_id: kp-49f1ff0bb6fe8bb8
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-0b49eeb55140
learning_sourceId: 0b49eeb55140
learning_order: 15
learning_objective: 理解并验证：换成真实模型的骨架（智谱 ChatGLM）
---

# 换成真实模型的骨架（智谱 ChatGLM）

> **学习目标**：能够解释「换成真实模型的骨架（智谱 ChatGLM）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[../llm/05-大模型API与调用实践.md](../../../../../06-llm/06-提示工程/05-大模型API与调用实践.md) 的消息角色与 API 调用、[../llm/04-提示词工程.md](../../../../../06-llm/06-提示工程/04-提示词工程.md) 的 system prompt 用法、本目录 [02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)。
>
> **所属主题**：-Agent基础范式与ReAct循环 · 可运行示例

## 本次只学这一点

Function Call 章节用的是智谱 `glm-4`。把上面的 `ScriptedLLM` 换成真实调用即可：

```text
"""真实模型版 Agent 骨架（需联网与 API Key）。

依赖：pip install zhipuai python-dotenv
环境变量：ZHIPU_API_KEY
"""

import json
import os

from zhipuai import ZhipuAI

from tools import TOOL_SCHEMAS, TOOLS # 复用 3.1 中定义的注册表

def chat_completion_request(client, messages, tools=None, tool_choice=None, model="glm-4"):
 try:
 return client.chat.completions.create(
 model=model, messages=messages, tools=tools, tool_choice=tool_choice
 )
 except Exception as exc: # 网络/额度/参数错误都收敛成日志，不中断循环
 print("Unable to generate ChatCompletion response")
 print("Exception: %s" % exc)
 return None

def run(goal, max_steps=5):
 client = ZhipuAI(api_key=os.environ["ZHIPU_API_KEY"])
 messages = [
 {"role": "system", "content": "你是一个助手，不确定的信息不要编造，必要时调用工具。"},
 {"role": "user", "content": goal},
 ]
 for _ in range(max_steps):
 response = chat_completion_request(client, messages, tools=TOOL_SCHEMAS, tool_choice="auto")
 if response is None:
 return "模型调用失败"
 message = response.choices[0].message
 messages.append(message.model_dump())
 if not message.tool_calls:
 return message.content
 for tool_call in message.tool_calls:
 name = tool_call.function.name
 args = json.loads(tool_call.function.arguments)
 result = TOOLS[name](**args) if name in TOOLS else {"error": "未知工具"}
 messages.append({
 "role": "tool",
 "tool_call_id": tool_call.id,
 "content": json.dumps(result, ensure_ascii=False),
 })
 return "达到最大步数仍未完成"

if __name__ == "__main__":
 print(run("今天北京的天气如何？"))
```

工具调用的协议细节（`tool_calls`、`tool_call_id`、`model_dump`）在 [02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 里逐字段拆解。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「换成真实模型的骨架（智谱 ChatGLM）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md)
