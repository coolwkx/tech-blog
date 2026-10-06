---
article_id: "d7e52d0c88a6"
learning_kind: "guide"
learning_category: "07-agent"
---

# ① 基础范式

> 本章共 2 篇笔记。

## 本节目录

| 笔记 | 难度 | 预计用时 | 状态 |
| --- | --- | --- | --- |
| [1.1 Agent 基础范式与 ReAct 循环](01-Agent基础范式与ReAct循环.md) | ⭐⭐⭐ | 25min | ✅ 已完成 |
| [1.2 从零实现一个最小 Agent](01-从零实现一个最小Agent.md) | ⭐⭐⭐ | 25min | ✅ 已完成 |

## 本章要回答的问题

**1.1 Agent 基础范式与 ReAct 循环**
- 用一句话说清 Agent 与传统软件、与普通聊天机器人的区别，并画出「感知 → 规划 → 行动 → 观察」闭环。
- 说出 `Prompt / LLM / Memory / Planning / Action` 五要素各自在闭环里承担什么，以及 ReAct 的 Thought → Action → Observation 结构。
- 写一个带终止条件、带工具注册表、带观察回填的最小 Agent 循环，并知道它会在哪些条件下失控。

**1.2 从零实现一个最小 Agent**
- 不依赖任何框架，用纯标准库写出一个带工具注册、超时重试、步数上限的 Agent；
- 说清 ReAct、Plan-and-Execute、Reflexion 各自适用什么场景、代价是什么、怎么失败；
- 在文本协议与原生 function calling 之间做取舍，并预判各自的解析鲁棒性问题；

状态说明：✅ 已完成 ｜ 🚧 编写中 ｜ 📝 计划中

---

[⬅️ 返回本区目录](../README.md)
