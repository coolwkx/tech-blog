---
article_id: kp-f08a8757107bc336
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-21455d0f58d4
learning_sourceId: 21455d0f58d4
learning_order: 13
learning_objective: 理解并验证：Plan-and-Execute 骨架：先出计划，再逐步执行
---

# Plan-and-Execute 骨架：先出计划，再逐步执行

> **学习目标**：能够解释「Plan-and-Execute 骨架：先出计划，再逐步执行」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的五要素、[03-LangChain与工具编排](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md) 的 Task/Crew、[06-RAG作为Agent的知识获取手段](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md) 的检索流程。
>
> **所属主题**：-Agent的规划与任务分解 · 可运行示例

## 本次只学这一点

**依赖**：仅标准库（用脚本化 planner 替代 LLM）。

```python
"""显式规划（Plan-and-Execute）骨架：先产出计划，再逐步执行并允许修订。

依赖：仅标准库。
"""

import json

TOOL_REGISTRY = {
"get_plane_number": lambda **kw: {"date": kw["date"], "number": "1123"},
"get_ticket_price": lambda **kw: {"ticket_price": "668"},
"notify_user": lambda **kw: {"sent": True, "to": kw.get("contact", "unknown")},
}

def scripted_planner(goal, known_facts):
    """假规划器：根据已知事实逐步给出下一步动作，模拟 Plan-and-Execute。"""
    if "number" not in known_facts:
        return {"step": 1, "tool": "get_plane_number",
    "args": {"date": "2024-04-02", "start": "郑州", "end": "北京"}}
    if "ticket_price" not in known_facts:
        return {"step": 2, "tool": "get_ticket_price",
    "args": {"date": "2024-04-02", "number": known_facts["number"]}}
    return None # 计划完成

def execute_plan(goal, max_steps=5):
    known_facts = {}
    trace = []
    for _ in range(max_steps):
        action = scripted_planner(goal, known_facts)
        if action is None:
            break
        tool_name = action["tool"]
        result = TOOL_REGISTRY[tool_name](**action["args"])
        print("step %d -> %s(%s) => %s" % (
        action["step"], tool_name,
        json.dumps(action["args"], ensure_ascii=False),
        json.dumps(result, ensure_ascii=False),
        ))
        known_facts.update(result)
        trace.append({"tool": tool_name, "args": action["args"], "result": result})
        return known_facts, trace

    if __name__ == "__main__":
        facts, trace = execute_plan("查询 2024-04-02 郑州到北京的票价")
        print("最终已知事实:", json.dumps(facts, ensure_ascii=False))
```

这个骨架演示了两个关键设计：`known_facts` 充当**执行期状态**（步骤间传参的载体），`scripted_planner` 每次只返回**一步**并在信息充足时返回 `None` 终止——对应 2.1 节「先出计划、允许修订」的折中方案。真实场景中把 `scripted_planner` 换成一次 LLM 调用即可。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/02-工具与规划/04-Agent的规划与任务分解.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Plan-and-Execute 骨架：先出计划，再逐步执行」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/02-工具与规划/04-Agent的规划与任务分解.md)
