---
article_id: kp-6f3e14a669d96920
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-215b0af0476d
learning_sourceId: 215b0af0476d
learning_order: 6
learning_objective: 理解并验证：两种输入，一套统计
---

# 两种输入，一套统计

> **学习目标**：能够解释「两种输入，一套统计」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-为什么Agent评测比LLM评测难](../../../../../07-agent/05-评测/01-为什么Agent评测比LLM评测难.md) 的结果层/过程层/系统层框架与四象限判定、[07-Agent工程化与可靠性设计](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md) 的轨迹落盘与结构化日志、基础统计学中的二项分布与 Bootstrap 重采样。
>
> **所属主题**：-项目复盘-AgentEvalLab · 架构总览

## 本次只学这一点

| 输入 Schema | 内容 | 谁来做判定 |
| --- | --- | --- |
| `agent-eval-lab-trajectories-v1` | `manifest + tasks + runs` | 本工具：执行完整性门、证据绑定、多标签归因 |
| `agent-eval-lab-results-v1` | `manifest + results` | 外部：工具只做严格配对与统计复算 |

这个双入口设计解决了一个现实问题：**很多团队已经在别处算好了逐条 passed，只是统计口径不严。** 允许他们只导入结果、把统计这一层换掉，比要求他们重做整条链路更容易落地。但导入路径的校验反而更严——`passed=true` 时 `primaryFailure` 必须是 `none` 且 `violations` 必须为空，`passed=false` 时首个 violation 必须等于 `primaryFailure`，`pairKey` 必须等于重新计算的值（拒绝伪造主键改变配对关系）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「两种输入，一套统计」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md)
