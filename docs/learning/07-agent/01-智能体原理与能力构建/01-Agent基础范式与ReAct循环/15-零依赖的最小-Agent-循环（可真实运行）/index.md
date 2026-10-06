---
article_id: kp-fdd2b8c80a43bd32
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-0b49eeb55140
learning_sourceId: 0b49eeb55140
learning_order: 14
learning_objective: 理解并验证：零依赖的最小 Agent 循环（可真实运行）
---

# 零依赖的最小 Agent 循环（可真实运行）

> **学习目标**：能够解释「零依赖的最小 Agent 循环（可真实运行）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[../llm/05-大模型API与调用实践.md](../../../../../06-llm/06-提示工程/05-大模型API与调用实践.md) 的消息角色与 API 调用、[../llm/04-提示词工程.md](../../../../../06-llm/06-提示工程/04-提示词工程.md) 的 system prompt 用法、本目录 [02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)。
>
> **所属主题**：-Agent基础范式与ReAct循环 · 可运行示例

## 本次只学这一点

下面这个例子不依赖任何模型，用一个「脚本化的假 LLM」替代模型输出，把 Agent 的骨架跑通。**依赖：仅 Python 标准库（Python 3.8+）。**

```python
"""最小 Agent 循环示例：用脚本化的 planner 替代 LLM，演示 ReAct 结构。

依赖：仅标准库。
"""

import json
import re

TOOL_SCHEMAS = [
{
"name": "get_current_weather",
"description": "查询给定城市当前的天气情况",
"parameters": {
"type": "object",
"properties": {
"location": {"type": "string", "description": "城市名，例如 北京"}
},
"required": ["location"],
},
},
{
"name": "calculator",
"description": "执行四则运算，输入形如 '3*4+2' 的表达式",
"parameters": {
"type": "object",
"properties": {
"expression": {"type": "string", "description": "算术表达式"}
},
"required": ["expression"],
},
},
]

def get_current_weather(location):
    fake_db = {"北京": {"type": "晴", "high": 33, "low": 17}}
    return fake_db.get(location, {"error": "未知城市: %s" % location})

def calculator(expression):
    if not re.fullmatch(r"[0-9+\-*/(). ]+", expression):
        return {"error": "表达式包含非法字符"}
    return {"result": eval(expression)} # 仅演示，生产环境请改用 ast.literal_eval

TOOLS = {"get_current_weather": get_current_weather, "calculator": calculator}

class ScriptedLLM:
    """假 LLM：按预设脚本依次吐 Thought/Action，演示 ReAct 轨迹格式。"""

    def __init__(self, script):
        self.script = list(script)
        self.calls = 0

        def __call__(self, memory):
            if self.calls >= len(self.script):
                return "Final Answer: 北京今天晴，最高 33℃，最低 17℃。", None, None
            action, action_input = self.script[self.calls]
            self.calls += 1
            if action is None:
                return action_input, None, None
            return "需要调用工具 %s" % action, action, action_input

        def execute(action, action_input):
            if action not in TOOLS:
                return {"error": "未知工具: %s" % action}
            return TOOLS[action](**action_input)

        def run_agent(goal, llm, max_steps=5):
            memory = [{"role": "user", "content": goal}]
            for step in range(1, max_steps + 1):
                thought, action, action_input = llm(memory)
                print("[step %d] Thought: %s" % (step, thought))
                if action is None:
                    print("[step %d] Finish" % step)
                    return thought
                observation = execute(action, action_input)
                print("[step %d] Action: %s(%s)" % (step, action, json.dumps(action_input, ensure_ascii=False)))
                print("[step %d] Observation: %s" % (step, json.dumps(observation, ensure_ascii=False)))
                memory.append({"role": "assistant", "content": thought, "action": action})
                memory.append({"role": "tool", "content": json.dumps(observation, ensure_ascii=False)})
                return "达到最大步数仍未完成"

            if __name__ == "__main__":
                scripted = ScriptedLLM([
                ("get_current_weather", {"location": "北京"}),
                (None, "Final Answer: 北京今天晴，最高 33℃，最低 17℃。"),
                ])
                print(run_agent("今天北京的天气如何？", scripted))
```

运行后可以看到完整的 `Thought → Action → Observation → Final Answer` 轨迹——这正是 ReAct 的外形，只是「思考」由脚本而非模型产生。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「零依赖的最小 Agent 循环（可真实运行）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md)
