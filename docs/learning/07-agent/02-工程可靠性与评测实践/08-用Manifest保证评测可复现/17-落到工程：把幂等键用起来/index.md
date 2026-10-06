---
article_id: kp-1934ca802a3c2154
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-cf848e0fe35f
learning_sourceId: cf848e0fe35f
learning_order: 16
learning_objective: 理解并验证：落到工程：把幂等键用起来
---

# 落到工程：把幂等键用起来

> **学习目标**：能够解释「落到工程：把幂等键用起来」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的六段流水线与四道一致性闸门、SHA-256 与规范化（canonicalization）的基本概念、JSON/JSONL 基础。
>
> **所属主题**：-用Manifest保证评测可复现 · 用 taskId + repeatId + seed 作为幂等键

## 本次只学这一点

| 场景 | 用法 |
| --- | --- |
| 结果落盘 | 文件名用 `pairKey` 转义后命名，如 `easy-title__r1__1.json` |
| 数据库 | 对 `(condition, pairKey)` 建唯一索引，重复写入直接冲突而不是覆盖 |
| 续跑脚本 | 启动时读已有结果集合，跳过已存在的键 |
| 报告自检 | 断言 `len(results) == len(taskIds) * repeatCount * 2`（两个条件） |
| 缓存 | 以 `(pairKey, promptHash, model.revision)` 为缓存键，任何一项变化就失效 |

`seed` 缺失时工具会把 `pairKey` 写成 `...::none`，但**Manifest 模式下每条运行都必须带 seed**，所以这个分支只对非 Manifest 的宽松场景存在。别依赖它。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「落到工程：把幂等键用起来」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md)
