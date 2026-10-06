---
article_id: kp-c57ec7ddb2efc58c
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-727eecd00fa8
learning_sourceId: 727eecd00fa8
learning_order: 4
learning_objective: 理解并验证：完整用例设计表
---

# 完整用例设计表

> **学习目标**：能够解释「完整用例设计表」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的证据式判定与多标签归因、[02 篇](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md) 的 Manifest 与配对主键、[03 篇](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md) 的 McNemar 与聚类 Bootstrap、[大宗商品价格监控 Agent 复盘](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md) 的规则驱动监控循环。
>
> **所属主题**：-给一个真实Agent补评测 · 任务集设计：15 条评测用例

## 本次只学这一点

| # | 任务 ID | 难度 | 输入场景 | 期望产物 | 断言 | 证据要求 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `snap-single-source` | easy | 源 A 返回 `WTI=78.42 USD/bbl` | state 更新 + history 追加 1 行 | `state.status="normal"`；`history.appended=1` | `wti_price`、`persisted_at` |
| 2 | `unit-normalize` | easy | 铜价 `4.35 USD/lb` | 归一价写入 history | `history.unit="USD/tonne"`；`history.value≈9589` | `raw_price`、`normalized_price`、`unit_factor` |
| 3 | `tz-bucket` | easy | 抓取时刻 `2026-03-02T01:30:00Z` | history 归属交易日 | `history.tradeDate="2026-03-02"` | `trade_date`、`history_offset` |
| 4 | `board-read-latest` | easy | state 与 history 均存在 | 看板 payload | `board.stateTs==state.updatedAt`；`board.historyLen=3` | `board_payload_ts`、`board_history_len` |
| 5 | `multi-source-conflict` | medium | 三源 `78.42/79.90/78.31`，价差 1.99% > 1.5% | 共识价 + 分歧标记 | `state.consensusSource="median"`；`state.staleFlag="fresh"` | `source_spread`、`consensus_price`、`stale_flag` |
| 6 | `primary-source-degrade` | medium | 源 A 超时，源 B/C 正常 | 用 B/C 出共识 | `state.consensusSource="degraded"`；`state.sourceCount=2` | `source_attempts`、`active_sources` |
| 7 | `stale-data-guard` | medium | 三源返回 `null`，缓存只有 6 小时前的值 | state 不变 + 标记 stale | `state.status` 不变；`state.staleFlag="stale"`；`state.notified=false` | `stale_flag`、`cache_age_seconds` |
| 8 | `threshold-boundary` | medium | 价格恰好等于 `buy_threshold=800` | 不推送（严格不等号） | `state.status="normal"`；`state.notified=false` | `threshold_compare`、`state_before` |
| 9 | `idempotent-rerun` | medium | 同一 `(runId, 抓取时刻)` 执行两次 | history 只追加 1 行 | `history.appended=1`；`history.duplicateSkipped=1` | `idempotency_key`、`history_offset` |
| 10 | `notify-retry` | hard | 首次推送 502，第二次成功 | 送达 + 尝试次数 | `state.notifyDelivered=true`；`notify.attempts=2` | `notify_attempt`、`notify_delivery_id` |
| 11 | `hysteresis-no-flap` | hard | 价格在阈值附近 5 次小幅穿越 | 至多推送 1 次 | `notify.count<=1`；`state.statusChanges<=1` | `status_change_log`、`notify_count` |
| 12 | `null-not-zero` | hard | 源 A 返回 `null`，源 B/C 正常 | 忽略 A，不使用 0 | `state.price` 不为 0；`state.usedFallback=true` | `null_source_ids`、`consensus_price` |
| 13 | `cross-day-report` | hard | 连续两交易日各 3 次抓取，跨 UTC 午夜 | 日报分属两日，无重复无缺失 | `report.days=2`；`report.duplicatedDates=[]` | `report_dates`、`history_offsets` |
| 14 | `history-append-order` | hard | history 已 100 行，追加第 101 行 | 单调递增的 `appendedAt` | `history.appended=1`；`history.monotonic=true` | `last_offset_before`、`last_offset_after` |
| 15 | `partial-outage` | hard | 源 A 超时 + 源 B stale + 源 C 正常 | 标记部分失效并降级决策 | `state.staleFlag="partial"`；`state.status` 不变 | `source_attempts`、`stale_flag`、`active_sources` |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/04-给一个真实Agent补评测.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「完整用例设计表」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/04-给一个真实Agent补评测.md)
