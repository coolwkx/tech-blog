---
article_id: kp-fcf0c7ebe3350c8f
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-8fca08e90f95
learning_sourceId: 8fca08e90f95
learning_order: 0
learning_objective: 理解并验证：标签表
---

# 标签表

> **学习目标**：能够解释「标签表」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的评测器判定顺序与证据信任链、[02 篇](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md) 的 `taskId + repeatId + seed` 配对主键、二项分布与 Bootstrap 重采样的基础。
>
> **所属主题**：-失败归因与显著性检验实战 · 失败分类学：九种标签与判定优先级

## 本次只学这一点

评测器的 `FailureType` 是一个九值枚举，其中 `none` 表示通过，其余八个是违规标签：

| 标签 | 判定条件 | 典型现场 |
| --- | --- | --- |
| `missing_trajectory` | `events.length === 0` | 运行器返回了空轨迹；采集管道断了 |
| `zero_step_termination` | 没有任何 `tool_call` 事件 | 模型直接回答；或工具白名单为空导致全部被拦 |
| `empty_final_answer` | 没有 `final` 事件，或 `final.text.trim()` 为空 | Agent 做完动作忘了输出结论；流式输出被截断 |
| `invalid_evidence_source` | 声明的证据无法绑定到成功 `tool_result` 的产出，或值/哈希不一致 | 模型自报"已确认"；证据来源事件不存在；值被改写 |
| `missing_evidence` | 任务要求的 claim 不在已验证证据集里，**或**未被最终回答引用 | 只抓到一部分数据；证据验证了但没写进结论 |
| `tool_error` | 存在失败的 `tool_result` **且** `status === "failed"` | 工具连续失败，运行器仍返回 failed |
| `blocked` | `status === "blocked"` | 登录墙、验证码、权限不足、依赖不可用 |
| `goal_not_completed` | `status === "failed"` | 兜底标签：运行状态本身就没完成 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「标签表」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md)
