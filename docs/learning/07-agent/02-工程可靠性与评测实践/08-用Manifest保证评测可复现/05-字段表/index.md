---
article_id: kp-139422060a8033d3
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-cf848e0fe35f
learning_sourceId: cf848e0fe35f
learning_order: 4
learning_objective: 理解并验证：字段表
---

# 字段表

> **学习目标**：能够解释「字段表」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的六段流水线与四道一致性闸门、SHA-256 与规范化（canonicalization）的基本概念、JSON/JSONL 基础。
>
> **所属主题**：-用Manifest保证评测可复现 · Manifest 字段逐个讲解

## 本次只学这一点

| 字段 | 类型与约束 | 不合法时的行为 |
| --- | --- | --- |
| `schema` | 字面量 `agent-eval-lab-manifest-v1` | 报 `$.manifest.schema: 必须是 agent-eval-lab-manifest-v1` |
| `experimentId` | 非空字符串 | 报 `$.manifest.experimentId: 必须是非空字符串` |
| `createdAt` | 可被 `Date.parse` 解析的 ISO 时间 | `$.manifest.createdAt: 必须是有效的 ISO 日期时间` |
| `model.provider` | 非空字符串 | 报错 |
| `model.name` | 非空字符串 | 报错 |
| `model.revision` | 可选字符串 | 缺省合法 |
| `promptHash` | `sha256:<64 位十六进制>` | `$.manifest.promptHash: 必须使用 sha256:<64位十六进制> 格式` |
| `codeCommit` | 7–40 位十六进制 | `$.manifest.codeCommit: 必须是 7–40 位十六进制 Git commit` |
| `dataset.name` | 非空字符串 | 报错 |
| `dataset.hash` | `sha256:<64 位十六进制>` | 报错（与 `promptHash` 同规则） |
| `taskIds` | 非空且去重的字符串数组 | `至少包含一个预期任务 ID` / `taskId 重复：t3` |
| `seeds` | 非空且去重的整数数组 | `至少包含一个确定性 seed` / `seed 重复：1` |
| `repeatCount` | 正整数，且 **≥ `seeds.length`** | `每任务配对重复总数不能少于 seeds 数量` |
| `evaluatorVersion` | 语义化版本号 | `必须是语义化版本号` |
| `data.classification` | `synthetic` / `controlled` / `public` | 枚举报错 |
| `data.containsPrivateData` | 布尔 | 报错 |
| `data.redacted` | 布尔 | 报错 |
| `data` 交叉约束 | `public` 时 `containsPrivateData` 必须为 `false` | `$.manifest.data: public 数据不能标记为包含私有数据` |
| `notes` | 可选字符串数组 | 缺省合法 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「字段表」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md)
