---
article_id: kp-ab93edf5ba4e46c4
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-215b0af0476d
learning_sourceId: 215b0af0476d
learning_order: 10
learning_objective: 理解并验证：评测层：违规的追加顺序就是归因优先级
---

# 评测层：违规的追加顺序就是归因优先级

> **学习目标**：能够解释「评测层：违规的追加顺序就是归因优先级」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-为什么Agent评测比LLM评测难](../../../../../07-agent/05-评测/01-为什么Agent评测比LLM评测难.md) 的结果层/过程层/系统层框架与四象限判定、[07-Agent工程化与可靠性设计](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md) 的轨迹落盘与结构化日志、基础统计学中的二项分布与 Bootstrap 重采样。
>
> **所属主题**：-项目复盘-AgentEvalLab · 核心实现剖析

## 本次只学这一点

`evaluateRun` 的核心结构是"顺序追加 → 首个即主因"：

```ts
// 精简重写：只保留顺序与判定条件
const violations: FailureViolation[] = [];

if (run.events.length === 0)                    add("missing_trajectory", "轨迹为空");
if (toolCalls.length === 0)                     add("zero_step_termination", "没有执行任何工具步骤");
if (!finalEvent?.text?.trim())                  add("empty_final_answer", "最终回答为空");
if (invalidEvidence.length > 0)                 add("invalid_evidence_source", ...);
if (missingRequiredEvidence.length > 0)         add("missing_evidence", ...);
if (missingCitations.length > 0)                add("missing_evidence", ...);   // 同 code 会被合并
if (hasToolError && run.status === "failed")    add("tool_error", "工具错误后未恢复");
if (run.status === "blocked")                   add("blocked", "任务被明确阻断");
if (run.status === "failed")                    add("goal_not_completed", "运行状态未完成");

const primaryFailure = violations[0]?.code ?? "none";
const passed = violations.length === 0;
```

四个必须看懂的机制：

**① 同一 code 的违规会被合并而不是追加。** `addViolation` 先 `findIndex` 找同 code 项，找到就把 message 拼上去、把 `evidenceIds` 求并集。所以"缺少证据"和"最终回答未引用证据"最终合成一条 `missing_evidence`，其 `message` 是两句话、`evidenceIds` 是两个 claim 的并集。

**② `primaryFailure` 是稳定可预测的，不是"最严重的"。** 它严格等于列表首项，而列表顺序由代码书写顺序决定。这意味着主归因可以跨版本对比——用户能预期"零步终止 + 缺证据"一定归为 `zero_step_termination`。把"最严重"这种主观排序写进代码，会立刻产生跨版本不可比的问题。

**③ 证据来源只认成功的 `tool_result`，且要求 `sourceEventId` 自指。** 构建可信来源表时做了两道过滤：

```ts
for (const event of run.events) {
  if (event.type !== "tool_result" || event.success !== true) continue;   // 失败工具不产出可信证据
  for (const record of event.evidence ?? []) {
    if (record.sourceEventId !== event.eventId) continue;                 // 证据必须由本事件产出
    sourceEvidence.set(`${event.eventId}::${record.claimId}`, {
      value: record.value,
      contentHash: record.contentHash,
    });
  }
}
```

`verification` 事件里声明的证据只有在 `(sourceEventId, claimId)` 能在来源表里找到、**且 `value` 与 `contentHash` 都一致**时才算有效。所以三种伪造同时被挡住：来源事件不存在、来源是失败的 `tool_result`、值被改过。全部归入 `invalid_evidence_source`。

**④ `steps` 是 `step` 的去重计数，不是 tool_call 的条数。**

```ts
const steps = new Set(toolCalls.map((event) => event.step)).size;
```

同一步内并行调用三个工具算 1 步而不是 3 步。这个口径必须和统计层的"平均步数"保持一致，否则跨版本比较步数会失真。

**⑤ 平均步数要报两个口径。** `summarize` 同时给出 `avgStepsAll` 与 `avgStepsSuccessful`（无成功时为 `null`）。原因很直白：失败任务常常零步结束，会**拉低**全量平均步数，于是"提前失败"看起来像"更高效"。项目在报告的 `notes` 里显式写了这条理由。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「评测层：违规的追加顺序就是归因优先级」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md)
