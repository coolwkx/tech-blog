---
article_id: kp-6d2309d68700c082
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-8fca08e90f95
learning_sourceId: 8fca08e90f95
learning_order: 3
learning_objective: 理解并验证：一条轨迹能同时命中几个标签
---

# 一条轨迹能同时命中几个标签

> **学习目标**：能够解释「一条轨迹能同时命中几个标签」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的评测器判定顺序与证据信任链、[02 篇](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md) 的 `taskId + repeatId + seed` 配对主键、二项分布与 Bootstrap 重采样的基础。
>
> **所属主题**：-失败归因与显著性检验实战 · 失败分类学：九种标签与判定优先级

## 本次只学这一点

这是 Agent 评测与 LLM 评测在数据结构上的关键差异。一个典型的"看起来完成了"的失败轨迹：

```text
tool_call   step=1  search
tool_result step=1  success=false          ← 工具失败
tool_call   step=2  search
tool_result step=2  success=true  evidence=[query]
verification step=1 success=true  evidence=[query]
final       step=2  text="搜索完成"  citations=["query"]
status: failed
任务要求证据: ["query", "count"]
```

判定结果：

| 标签 | 是否命中 | 原因 |
| --- | :-: | --- |
| `missing_evidence` | ✓ | `count` 从未被验证，且未被引用 |
| `tool_error` | ✓ | 有失败工具结果，且 `status === "failed"` |
| `goal_not_completed` | ✓ | `status === "failed"` |
| `zero_step_termination` | ✗ | 有 `tool_call` |
| `empty_final_answer` | ✗ | `final.text` 非空 |
| `invalid_evidence_source` | ✗ | `query` 能绑定到成功工具产出的同值证据 |
| `missing_trajectory` / `blocked` | ✗ | 有事件；`status` 不是 blocked |

三条标签，`primaryFailure = missing_evidence`。**如果数据结构只允许一个失败原因，我们就丢掉了"工具失败过"这条最有价值的改进线索。**

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「一条轨迹能同时命中几个标签」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md)
