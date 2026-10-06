---
article_id: kp-d709ceaec1e138a4
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-0ae5654d8e63
learning_sourceId: 0ae5654d8e63
learning_order: 13
learning_objective: 理解并验证：多源降级 + 校验 + 退避重试的价格抓取器
---

# 多源降级 + 校验 + 退避重试的价格抓取器

> **学习目标**：能够解释「多源降级 + 校验 + 退避重试的价格抓取器」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的工具协议与错误处理、[05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的状态持久化、[08-大宗商品价格监控Agent项目复盘](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md)。
>
> **所属主题**：-Agent工程化与可靠性设计 · 可运行示例

## 本次只学这一点

**依赖**：仅标准库（用 `urllib` 替代 `requests`，演示同样的降级结构）。

```text
"""Agent 运行骨架：配置外置 + 状态落盘 + 步数上限 + 轨迹记录。

依赖：仅标准库。
"""

import json
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "agent_config.json")
STATE_FILE = os.path.join(BASE_DIR, "agent_run_state.json")

DEFAULT_CONFIG = {
 "max_steps": 5,
 "tool_timeout_seconds": 10,
 "notify_interval_seconds": 3600,
 "enable_retrieval": True,
}

def load_config(path=CONFIG_FILE):
 try:
 with open(path, "r", encoding="utf-8") as file:
 config = json.load(file)
 except (OSError, ValueError) as exc:
 print("配置加载失败，使用默认配置: %s" % exc)
 config = {}
 merged = dict(DEFAULT_CONFIG)
 merged.update(config) # 缺哪项补哪项，多余项忽略
 return merged

def load_state(path=STATE_FILE):
 try:
 with open(path, "r", encoding="utf-8") as file:
 return json.load(file)
 except (OSError, ValueError):
 return {"runs": 0, "last_success_time": 0}

def save_state(state, path=STATE_FILE):
 with open(path, "w", encoding="utf-8") as file:
 json.dump(state, file, ensure_ascii=False, indent=2)

def run_agent(goal, planner, tools, config=None):
 """planner(goal, facts, step) -> {"tool": name, "args": {...}} 或 None"""
 config = config or load_config()
 state = load_state()
 facts, trace = {}, []
 started = time.time()

 for step in range(1, int(config["max_steps"]) + 1):
 action = planner(goal, facts, step)
 if action is None:
 break
 name = action["tool"]
 if name not in tools:
 trace.append({"step": step, "error": "未知工具: %s" % name})
 break
 try:
 result = tools[name](**action["args"])
 except Exception as exc: # 工具错误 → Observation
 result = {"error": str(exc)}
 trace.append({"step": step, "tool": name, "args": action["args"], "result": result})
 if isinstance(result, dict) and not result.get("error"):
 facts.update(result)
 else:
 break # 关键步骤失败则停止，交人工处理
 else:
 trace.append({"step": None, "error": "达到最大步数仍未完成"})

 state["runs"] = state.get("runs", 0) + 1
 state["last_success_time"] = int(time.time())
 state["last_trace"] = trace
 save_state(state)

 return {
 "facts": facts,
 "trace": trace,
 "elapsed": round(time.time() - started, 3),
 "runs_total": state["runs"],
 }

if __name__ == "__main__":
 def planner(goal, facts, step):
 if "number" not in facts:
 return {"tool": "get_plane_number",
 "args": {"date": "2024-04-02", "start": "郑州", "end": "北京"}}
 return None

 TOOLS = {"get_plane_number": lambda **kw: {"date": kw["date"], "number": "1123"}}
 print(json.dumps(run_agent("查询航班号", planner, TOOLS), ensure_ascii=False, indent=2))
```

这段代码与项目的差别只有三处：把 `print` 换成 `logging`、把「一层 for」改成「每个源内退避重试」、把「静默 continue」改成显式 `logger.warning`——但这三处正是「能跑」与「可运维」的分界线。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「多源降级 + 校验 + 退避重试的价格抓取器」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md)
