---
article_id: kp-aef06809800f7b97
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-727eecd00fa8
learning_sourceId: 727eecd00fa8
learning_order: 8
learning_objective: 理解并验证：一条任务的判据与轨迹
---

# 一条任务的判据与轨迹

> **学习目标**：能够解释「一条任务的判据与轨迹」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的证据式判定与多标签归因、[02 篇](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md) 的 Manifest 与配对主键、[03 篇](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md) 的 McNemar 与聚类 Bootstrap、[大宗商品价格监控 Agent 复盘](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md) 的规则驱动监控循环。
>
> **所属主题**：-给一个真实Agent补评测 · 成功判据与证据要求

## 本次只学这一点

```json
{"taskId": "notify-retry", "difficulty": "hard",
 "objective": "推送 502 后按退避策略重试直至送达，且只在送达后更新状态",
 "requiredEvidence": ["notify_attempt", "notify_delivery_id"],
 "assertions": {"state.notifyDelivered": true}}
```

对应轨迹（节选，省略了 `tool_call` 事件与 `tool` 字段）：

```json
{"runId": "optimized-notify-retry-r1", "taskId": "notify-retry", "condition": "optimized",
 "repeatId": "r1", "seed": 1, "status": "completed",
 "finalState": {"state.notifyDelivered": true},
 "events": [
   {"eventId": "o3-res-1", "type": "tool_result", "step": 1, "success": false},
   {"eventId": "o3-res-2", "type": "tool_result", "step": 2, "success": true, "evidence": [
     {"claimId": "notify_attempt", "value": "2", "sourceEventId": "o3-res-2"},
     {"claimId": "notify_delivery_id", "value": "wx-7712", "sourceEventId": "o3-res-2"}]},
   {"eventId": "o3-ver", "type": "verification", "step": 2, "success": true, "evidence": [
     {"claimId": "notify_attempt", "value": "2", "sourceEventId": "o3-res-2"},
     {"claimId": "notify_delivery_id", "value": "wx-7712", "sourceEventId": "o3-res-2"}]},
   {"eventId": "o3-fin", "type": "final", "step": 2, "text": "第 2 次推送送达 wx-7712",
    "citations": ["notify_attempt", "notify_delivery_id"]}]}
```

三个关键点：失败的 `tool_result` 不产出可信证据；`verification` 的 `sourceEventId` 必须指向 `o3-res-2`（**不是** `o3-call-2`）；`final.citations` 必须列出两条 claim。把 `notify_delivery_id` 改成 `wx-forged`，判定立刻变成 `invalid_evidence_source`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/04-给一个真实Agent补评测.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「一条任务的判据与轨迹」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/04-给一个真实Agent补评测.md)
