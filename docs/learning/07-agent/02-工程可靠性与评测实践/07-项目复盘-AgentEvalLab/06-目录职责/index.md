---
article_id: kp-6e06d15f7a1e7a59
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-215b0af0476d
learning_sourceId: 215b0af0476d
learning_order: 5
learning_objective: 理解并验证：目录职责
---

# 目录职责

> **学习目标**：能够解释「目录职责」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-为什么Agent评测比LLM评测难](../../../../../07-agent/05-评测/01-为什么Agent评测比LLM评测难.md) 的结果层/过程层/系统层框架与四象限判定、[07-Agent工程化与可靠性设计](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md) 的轨迹落盘与结构化日志、基础统计学中的二项分布与 Bootstrap 重采样。
>
> **所属主题**：-项目复盘-AgentEvalLab · 架构总览

## 本次只学这一点

| 路径 | 职责 | 关键点 |
| --- | --- | --- |
| `src/types.ts` | 全部数据契约 | `FailureType` 九值枚举、`EvaluationResult` 同时带 `failureType` 与 `primaryFailure` |
| `src/schema.ts` | 手写校验器 + JSONL 归一化 | 错误携带 `$.manifest.promptHash` 形式的路径；`SchemaValidationError.issues` 是结构化数组 |
| `src/evaluator.ts` | 单次轨迹判定与归因 | 违规的**追加顺序**即归因优先级 |
| `src/statistics.ts` | 配对汇总、McNemar、Bootstrap | McNemar 有数值稳定的对数空间分支；Bootstrap 用自带 LCG 保证可复算 |
| `src/pipeline.ts` | 编排 + Manifest 一致性 | 四道闸门，全部抛 `SchemaValidationError` |
| `src/cli.ts` | 命令行入口 | 退出码 2 = 输入不合法，1 = 其它错误 |
| `src/fixtures.ts` | 明确标注的合成任务与轨迹 | 3 条合成任务，只用于验证工具行为 |
| `schemas/*.json` | 公开 JSON Schema | Draft 2020-12，`oneOf` 区分两种输入文档 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「目录职责」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md)
