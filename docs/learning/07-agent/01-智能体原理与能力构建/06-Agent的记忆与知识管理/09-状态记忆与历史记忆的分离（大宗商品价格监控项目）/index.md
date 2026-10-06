---
article_id: kp-87ec47fa54411de3
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-3dbf2b7f4206
learning_sourceId: 3dbf2b7f4206
learning_order: 8
learning_objective: 理解并验证：状态记忆与历史记忆的分离（大宗商品价格监控项目）
---

# 状态记忆与历史记忆的分离（大宗商品价格监控项目）

> **学习目标**：能够解释「状态记忆与历史记忆的分离（大宗商品价格监控项目）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[03-LangChain与工具编排](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md) 的 Memory 组件、[06-RAG作为Agent的知识获取手段](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md) 的向量检索、[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的 messages 角色约定。
>
> **所属主题**：-Agent的记忆与知识管理 · 关键机制

## 本次只学这一点

这个项目把「记忆」落成了两个 JSON 文件，是工程上非常典型的划分：

**`gold_state.json`（状态记忆：只关心最新值）**

```json
{
 "last_price": 888.71,
 "last_status": "normal",
 "last_notify_time": 0
}
```

| 字段 | 用途 | 为什么必须持久化 |
| --- | --- | --- |
| `last_price` | 计算相比上次的涨跌幅 `(current - last) / last * 100` | 进程重启后仍能算出变化率 |
| `last_status` | `normal` / `buy` / `sell`，用于判断状态是否变化 | 实现「状态变化才提醒」 |
| `last_notify_time` | 上次提醒的时间戳 | 实现提醒间隔限流，避免每分钟骚扰 |

`monitor_gold()` 里的判定逻辑正好对应这三个字段：

```python
if status != state.get("last_status"): # 状态变化 → 立即提醒
 send_wechat_message(...)
elif title and now - state.get("last_notify_time", 0) > notify_interval: # 状态未变但超时 → 周期提醒
 send_wechat_message(...)
else:
 print("状态未变化，无需重复提醒")
```

这就是「防重复提醒」的实现方式：**把决策所需的全部上下文写进状态文件**，而不是靠进程内变量。

**`gold_history.json`（历史记忆：关心趋势）**

```json
[
 {"time": "2026-07-08 23:40:48", "price": 888.71},
 {"time": "2026-07-08 23:44:11", "price": 888.71}
]
```

它是趋势分析（`ai_analysis.py` 取最近 12 条）、日报（按日期前缀过滤当天记录）与 Web 走势图的数据源。写入时做截断：

| 位置 | 截断策略 | 含义 |
| --- | --- | --- |
| `check_price_once()` | `history = history[-500:]` | 只保留最近 500 条 |
| `save_gold_history()` | `history = history[-20000:]` | 只保留最近 20000 条（注释说「只保存最近 90 天以内的数据量」） |

**这是一个真实存在的坑**：同一份数据在两条代码路径上有两种截断阈值，且一条用相对路径 `"gold_history.json"`、另一条用绝对路径 `HISTORY_FILE = os.path.join(os.path.dirname(__file__), "gold_history.json")`——如果工作目录不同，会写出两个不同的文件。详见第 4 节与 [08-大宗商品价格监控Agent项目复盘](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md)。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「状态记忆与历史记忆的分离（大宗商品价格监控项目）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md)
