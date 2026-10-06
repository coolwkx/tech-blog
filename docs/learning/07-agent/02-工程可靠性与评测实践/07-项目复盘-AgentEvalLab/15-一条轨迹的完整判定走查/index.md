---
article_id: kp-945eb32f824d2bca
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-215b0af0476d
learning_sourceId: 215b0af0476d
learning_order: 14
learning_objective: 理解并验证：一条轨迹的完整判定走查
---

# 一条轨迹的完整判定走查

> **学习目标**：能够解释「一条轨迹的完整判定走查」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-为什么Agent评测比LLM评测难](../../../../../07-agent/05-评测/01-为什么Agent评测比LLM评测难.md) 的结果层/过程层/系统层框架与四象限判定、[07-Agent工程化与可靠性设计](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md) 的轨迹落盘与结构化日志、基础统计学中的二项分布与 Bootstrap 重采样。
>
> **所属主题**：-项目复盘-AgentEvalLab · 核心实现剖析

## 本次只学这一点

把上面五段串起来跑一遍，才看得出顺序为什么重要。取仓库合成 fixtures 里的 hard-block 基线轨迹（任务 `requiredEvidence: ["blocker"]`）：

```text
events:
  [0] final, step=0, text="任务完成", outputTokens=6      ← 注意：零个 tool_call
status: completed
```

逐条判定，严格按代码书写顺序：

| 顺序 | 检查 | 结果 |
| --- | --- | --- |
| 1 | `events.length === 0`？ | 否（有 1 个事件）→ 不记 `missing_trajectory` |
| 2 | 有 `tool_call` 吗？ | **没有** → 记 `zero_step_termination`「没有执行任何工具步骤」 |
| 3 | `final.text` 非空？ | 是（"任务完成"）→ 不记 `empty_final_answer` |
| 4 | 有非法证据吗？ | 无 `verification`，也没有证据声明 → 不记 `invalid_evidence_source` |
| 5 | `blocker` 在已验证证据集里？ | **不在** → 记 `missing_evidence`，`evidenceIds: ["blocker"]` |
| 6 | `blocker` 在 `final.citations` 里？ | **不在** → 追加同 code，**合并**进第 5 步那条 |
| 7 | 有失败工具结果且 status=failed？ | 没有工具调用 → 不记 `tool_error` |
| 8 | `status === "blocked"`？ | 否 |
| 9 | `status === "failed"`？ | 否（是 completed）→ 不记 `goal_not_completed` |

最终：

```json
{
  "pairKey": "hard-block::r1::1",
  "passed": false,
  "primaryFailure": "zero_step_termination",
  "failureType": "zero_step_termination",
  "violations": [
    { "code": "zero_step_termination", "message": "没有执行任何工具步骤" },
    { "code": "missing_evidence", "message": "缺少已验证证据：blocker；最终回答未引用证据：blocker",
      "evidenceIds": ["blocker"] }
  ],
  "steps": 0
}
```

三处值得记住的细节：

1. **`status` 是 `completed`，但 `passed` 是 `false`。** 这就是整个项目的核心论点——退出状态与目标完成度是两条独立的轴。`goal_not_completed` 只在 `status === "failed"` 时触发，所以一条"运行器认为成功、评测器认为失败"的轨迹，其主归因会是 `zero_step_termination` 这类**事实性**标签，而不是含糊的"未完成"。
2. **两次 `missing_evidence` 合并成了一条。** 第 6 步的 message 被拼到第 5 步上，`evidenceIds` 仍是去重后的 `["blocker"]`。所以数 `violations.length` 得到的是"**不同类别**的数量"，不是"违规条目数"。
3. **导入路径不会重算 message。** `results-v1` 输入下 message 是外部文件给出的文本，工具只校验它满足三条一致性（`passed` 与 `primaryFailure`/`violations` 自洽、`violations` 顺序与 `primaryFailure` 一致、`reasons` 与 `violations` 的 message 逐项相等），**不重新生成**。所以"轨迹输入"与"结果输入"对同一条轨迹可能给出措辞不同但语义等价的 message——这不影响统计，但会影响 message 级 diff，需要在报告对比时留意。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「一条轨迹的完整判定走查」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md)
