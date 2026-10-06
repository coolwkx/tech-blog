---
article_id: kp-308ea483b436de01
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-215b0af0476d
learning_sourceId: 215b0af0476d
learning_order: 12
learning_objective: 理解并验证：编排层：四道一致性闸门
---

# 编排层：四道一致性闸门

> **学习目标**：能够解释「编排层：四道一致性闸门」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-为什么Agent评测比LLM评测难](../../../../../07-agent/05-评测/01-为什么Agent评测比LLM评测难.md) 的结果层/过程层/系统层框架与四象限判定、[07-Agent工程化与可靠性设计](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md) 的轨迹落盘与结构化日志、基础统计学中的二项分布与 Bootstrap 重采样。
>
> **所属主题**：-项目复盘-AgentEvalLab · 核心实现剖析

## 本次只学这一点

`validateAgainstManifest` 是整条链路里最"较真"的一段。它依次检查：

| # | 闸门 | 失败信息（含路径） |
| --- | --- | --- |
| 1 | 轨迹输入下 `tasks` 的 taskId 集合与 `manifest.taskIds` **完全相等** | `$.tasks: TaskSpec 与 manifest.taskIds 不一致；缺少 [...]；多出 [...]` |
| 2 | 实际运行涉及的任务集合与 `manifest.taskIds` **完全相等** | `$.runs: 实际运行任务与 manifest.taskIds 不一致；缺少 [...]` |
| 3 | 每条结果都必须带 seed，且 seed 属于 `manifest.seeds` | `$.manifest.seeds: 运行 X 未声明 seed` / `运行 X 使用了未声明 seed：7` |
| 4 | 每个任务的 `(repeatId, seed)` 去重后数量等于 `repeatCount`，且覆盖全部 `seeds`；**所有任务的调度序列完全一致** | `任务 X 声明 2 次配对重复，实际为 1 次` / `任务 X 未覆盖声明 seed：2` / `任务 X 的 repeatId/seed 调度与 Y 不一致` |

第 2 道闸门常被忽略但极其重要：**Manifest 里声明但没跑的任务不能从分母里消失。** 如果允许"没跑的任务不出现在报告里"，那么删掉最难的任务就能静默提高成功率——这是最廉价也最隐蔽的作弊方式。项目专门有一条测试叫「Manifest taskIds 中未执行的任务不能从报告分母消失」。

第 4 道闸门保证**每个任务在同一组随机源上被比较**。如果任务 A 只在 seed=1 上跑、任务 B 只在 seed=2 上跑，那么 A/B 对比里混入了"任务差异 + 随机源差异"两个变量，无法归因。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「编排层：四道一致性闸门」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md)
