---
article_id: kp-f88470ad1c1ff603
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-215b0af0476d
learning_sourceId: 215b0af0476d
learning_order: 3
learning_objective: 理解并验证：它替代的是什么
---

# 它替代的是什么

> **学习目标**：能够解释「它替代的是什么」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-为什么Agent评测比LLM评测难](../../../../../07-agent/05-评测/01-为什么Agent评测比LLM评测难.md) 的结果层/过程层/系统层框架与四象限判定、[07-Agent工程化与可靠性设计](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md) 的轨迹落盘与结构化日志、基础统计学中的二项分布与 Bootstrap 重采样。
>
> **所属主题**：-项目复盘-AgentEvalLab · 项目定位

## 本次只学这一点

| 自研评测脚本的常见写法 | 本项目对应的做法 |
| --- | --- |
| `metrics.json` 里存一个成功率数字 | `agent-eval-lab-artifact-v1` 报告，含 Manifest、逐条结果、配对表、置信区间 |
| 配置写在脚本顶部的常量里 | `ExperimentManifest` 固化为输入的一部分，缺字段直接报错 |
| 失败只记 `passed: false` | 多标签 `violations` + 稳定 `primaryFailure` |
| 用 `except: pass` 容错脏数据 | Schema 错误带 JSON 路径，CLI 退出码 2 |
| 「改进了」= 数字变大 | McNemar exact p + task-cluster Bootstrap CI |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「它替代的是什么」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md)
