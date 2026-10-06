---
article_id: kp-322e69af5aa3704f
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-8fca08e90f95
learning_sourceId: 8fca08e90f95
learning_order: 11
learning_objective: 理解并验证：归因表怎么用
---

# 归因表怎么用

> **学习目标**：能够解释「归因表怎么用」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的评测器判定顺序与证据信任链、[02 篇](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md) 的 `taskId + repeatId + seed` 配对主键、二项分布与 Bootstrap 重采样的基础。
>
> **所属主题**：-失败归因与显著性检验实战 · 多标签 violations 与 primaryFailure 归因

## 本次只学这一点

| 目标 | 用什么字段 | 注意 |
| --- | --- | --- |
| 失败分布图（饼图/柱图） | `primaryFailure` | 各类别之和 = 失败运行数，可以归一化 |
| 定位改进优先级 | `violations` 全量标签 | 计数之和 > 失败数，不要归一化 |
| 具体证据缺失分析 | `violations[].evidenceIds` | 只有部分标签带该字段 |
| 跨版本趋势 | `primaryFailure` | 顺序稳定，可逐版本对比 |
| 单条失败复盘 | `reasons` | 与 `violations` 的 message 顺序一致 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「归因表怎么用」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md)
