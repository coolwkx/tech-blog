---
article_id: kp-1ac1d8c01848f3c6
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-8fca08e90f95
learning_sourceId: 8fca08e90f95
learning_order: 2
learning_objective: 理解并验证：三组容易混淆的标签
---

# 三组容易混淆的标签

> **学习目标**：能够解释「三组容易混淆的标签」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的评测器判定顺序与证据信任链、[02 篇](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md) 的 `taskId + repeatId + seed` 配对主键、二项分布与 Bootstrap 重采样的基础。
>
> **所属主题**：-失败归因与显著性检验实战 · 失败分类学：九种标签与判定优先级

## 本次只学这一点

**`missing_evidence` vs `invalid_evidence_source`。** 前者是"缺"，后者是"假"。`missing_evidence` 表示任务要求的 claim 压根没出现在有效证据里；`invalid_evidence_source` 表示 **Agent 声明了自己有证据，但那条声明站不住**（来源事件不存在、来源是失败的 `tool_result`、`value` 或 `contentHash` 与来源不一致）。两者的工程含义完全不同：前者多半是 Agent 能力/流程问题，后者涉及**数据可信度**，优先级更高——因为它意味着"这个系统会自报成功"。

**`tool_error` vs `blocked`。** `tool_error` 的触发条件是"有失败的工具结果 **且** 整体状态是 failed"。注意这个 `且`：如果工具失败了三次但第四次成功了、整体 completed，那么 `tool_error` **不会**触发——因为"错误后未恢复"这个描述不成立。`blocked` 只看 `status`，不看工具事件，它表达的是"Agent 明确判断自己被挡住了"。两者可以同时出现，但如果 Agent 在被挡住时把状态写成 `completed`，那它会落进 `zero_step_termination` 或 `missing_evidence`，而不是 `blocked`——**隐瞒阻断会以别的标签暴露出来**。

**`zero_step_termination` vs `empty_final_answer`。** 前者是"没做事"，后者是"没说话"。一条轨迹可以同时命中两者，此时主归因是 `zero_step_termination`（顺序更靠前）。这个区分很实用：只有 `empty_final_answer` 说明工具链路是通的、只是输出环节丢了；两个都有说明整条链路都没启动。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「三组容易混淆的标签」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md)
