---
article_id: kp-d69e6438e6b6f90a
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-4cd0a37cb105
learning_sourceId: 4cd0a37cb105
learning_order: 8
learning_objective: 理解并验证：记忆层：状态与历史分离
---

# 记忆层：状态与历史分离

> **学习目标**：能够解释「记忆层：状态与历史分离」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的五要素、[05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的状态与历史分离、[07-Agent工程化与可靠性设计](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md) 的降级与限流。
>
> **所属主题**：-大宗商品价格监控Agent项目复盘 · 关键机制

## 本次只学这一点

```json
// commodity_state.json —— 只关心最新值
{"last_price": 888.71, "last_status": "normal", "last_notify_time": 0}

// commodity_history.json —— 时间序列
[{"time": "2026-07-08 23:40:48", "price": 888.71},
 {"time": "2026-07-08 23:44:11", "price": 888.71}]
```

两者的读取方式完全不同：

| 文件 | 读取者 | 读取方式 |
| --- | --- | --- |
| `commodity_state.json` | `monitor_commodity` | `state.get("last_price")` 等，单值查询 |
| `commodity_history.json` | `ai_analysis`、`daily_report`、`dashboard` | 全量载入后切片（`prices[-12:]`、`history[-50:]`、按日期前缀过滤） |

这种划分是通用的：**「决策所需的最新事实」与「分析所需的历史序列」应当分文件存放**，因为前者的读写频率高、体积恒定，后者体积持续增长且需要截断策略。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「记忆层：状态与历史分离」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md)
