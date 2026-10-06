---
article_id: kp-db318cf10755f6a0
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-cf848e0fe35f
learning_sourceId: cf848e0fe35f
learning_order: 3
learning_objective: 理解并验证：Manifest 不覆盖的那一格：采样参数
---

# Manifest 不覆盖的那一格：采样参数

> **学习目标**：能够解释「Manifest 不覆盖的那一格：采样参数」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的六段流水线与四道一致性闸门、SHA-256 与规范化（canonicalization）的基本概念、JSON/JSONL 基础。
>
> **所属主题**：-用Manifest保证评测可复现 · 为什么评测不可复现是最大陷阱

## 本次只学这一点

这里必须诚实地说清楚一个边界：`ExperimentManifest` 有 `model`、`promptHash`、`codeCommit`、`dataset`、`taskIds`、`seeds`、`repeatCount`、`evaluatorVersion`、`data`，但**没有温度、top_p、max_tokens 这些采样参数**。

它用另一种方式兜住：`promptHash` 覆盖提示词、`codeCommit` 覆盖代码（采样参数通常写在代码或配置里，所以 commit 变了哈希就变）、`model.revision` 覆盖权重。如果你把采样参数放在**独立的运行配置**里而不进版本库，这个字段就漏了。

工程上的补救是很小的改动：额外定义一个 `runConfig`（温度、top_p、超时、最大步数、并发度）纳入 Manifest，并把它一起写进报告。项目本身没有做这件事，接入时值得补上——这条属于"复述该项目时要指出它的边界"，而不是"它做错了"。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Manifest 不覆盖的那一格：采样参数」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md)
