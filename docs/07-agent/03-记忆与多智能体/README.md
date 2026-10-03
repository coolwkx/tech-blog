# ③ 记忆与多智能体

> 本章共 3 篇笔记。

## 本节目录

| 笔记 | 难度 | 预计用时 | 状态 |
| --- | --- | --- | --- |
| [3.1 LangChain 与工具编排](03-LangChain与工具编排.md) | ⭐⭐⭐ | 25min | ✅ 已完成 |
| [3.2 Agent 的记忆与知识管理](05-Agent的记忆与知识管理.md) | ⭐⭐⭐ | 25min | ✅ 已完成 |
| [3.3 RAG 作为 Agent 的知识获取手段](06-RAG作为Agent的知识获取手段.md) | ⭐⭐⭐ | 25min | ✅ 已完成 |

## 本章要回答的问题

**3.1 LangChain 与工具编排**
- 说清 Agent、AgentExecutor、Tool、Toolkit 四者的分工，并选用 `zero-shot-react-description` / `conversational-react-description` 等代理类型。
- 用 `load_tools` + `initialize_agent` 跑通一个带数学计算工具的代理，并用 `@tool` 注册自己的工具。
- 用 CrewAI 的 Agent / Task / Crew 定义一条顺序执行的多角色流水线（写稿 → 编辑 → 寄信）。

**3.2 Agent 的记忆与知识管理**
- 区分短期记忆、长期状态记忆、外部知识记忆三类载体，并说出各自生命周期。
- 用 `ChatMessageHistory` 与 `messages_to_dict` / `messages_from_dict` 做会话记忆的持久化与恢复。
- 设计一个带滑动窗口截断的状态文件（如 `last_price` / `last_status` / `last_notify_time`），并解释为什么状态需要落盘才能实现「不重复提醒」。

**3.3 RAG 作为 Agent 的知识获取手段**
- 说出 RAG 三段式（索引 / 检索 / 生成）中各模块的职责，并画出 RAG 的模块协作图。
- 解释父子块分层切分的动机，写出 Milvus 集合的字段与索引设计（`IVF_FLAT` + `SPARSE_INVERTED_INDEX`）。
- 说明混合检索的融合方式（`WeightedRanker`）与重排（`CrossEncoder`）的分工，并写出一个最小可运行 RAG。

状态说明：✅ 已完成 ｜ 🚧 编写中 ｜ 📝 计划中

---

[⬅️ 返回本区目录](../README.md)
