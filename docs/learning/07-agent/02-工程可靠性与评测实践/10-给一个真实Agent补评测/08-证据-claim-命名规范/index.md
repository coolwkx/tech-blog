---
article_id: kp-46a987df292d90b5
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-727eecd00fa8
learning_sourceId: 727eecd00fa8
learning_order: 7
learning_objective: 理解并验证：证据 claim 命名规范
---

# 证据 claim 命名规范

> **学习目标**：能够解释「证据 claim 命名规范」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的证据式判定与多标签归因、[02 篇](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md) 的 Manifest 与配对主键、[03 篇](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md) 的 McNemar 与聚类 Bootstrap、[大宗商品价格监控 Agent 复盘](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md) 的规则驱动监控循环。
>
> **所属主题**：-给一个真实Agent补评测 · 成功判据与证据要求

## 本次只学这一点

| 后缀 | 含义 | 例 |
| --- | --- | --- |
| `_price` / `_spread` | 具体价格值 / 派生差异量 | `wti_price`、`source_spread` |
| `_flag` / `_attempts` | 状态标记 / 尝试次数 | `stale_flag`、`notify_attempt` |
| `_id` | 外部系统返回的标识 | `notify_delivery_id` |
| `_offset` / `_len` | 文件位置 / 长度 | `history_offset`、`board_history_len` |
| `_ts` / `_date` | 时间戳 / 日期 | `persisted_at`、`trade_date` |

两个约定：①每条 claim 必须由 `tool_result` 事件产出，不允许由 `plan` 或 `final` 产出；②**派生量与原始量都要留证据**（既要有 `raw_price` 也要有 `normalized_price` 和 `unit_factor`），否则无法区分"抓错了"和"换算错了"。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/04-给一个真实Agent补评测.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「证据 claim 命名规范」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/04-给一个真实Agent补评测.md)
