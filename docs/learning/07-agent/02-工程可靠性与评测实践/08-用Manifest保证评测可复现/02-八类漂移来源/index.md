---
article_id: kp-4796b4cb3fd55bb5
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-cf848e0fe35f
learning_sourceId: cf848e0fe35f
learning_order: 1
learning_objective: 理解并验证：八类漂移来源
---

# 八类漂移来源

> **学习目标**：能够解释「八类漂移来源」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的六段流水线与四道一致性闸门、SHA-256 与规范化（canonicalization）的基本概念、JSON/JSONL 基础。
>
> **所属主题**：-用Manifest保证评测可复现 · 为什么评测不可复现是最大陷阱

## 本次只学这一点

| # | 漂移来源 | 典型表现 | Manifest 对应字段 |
| --- | --- | --- | --- |
| 1 | 模型版本 | 上游静默升级；同一 `name` 指向不同权重 | `model.provider` / `model.name` / `model.revision` |
| 2 | 提示词内容 | 提示词散落在代码常量、数据库、环境变量里，改了不留痕 | `promptHash` |
| 3 | 采样参数 | 温度、top_p、max_tokens、并行度 | **需要扩展**（见 1.4） |
| 4 | 工具与依赖版本 | 抓取超时、重试次数、解析规则变更 | 工程约定 + 轨迹里的 `tool` 字段 |
| 5 | 数据 | 任务被改写、增删、难度重分布 | `dataset.name` / `dataset.hash` / `taskIds` |
| 6 | 随机源 | seed 未固定，重跑结果不同 | `seeds` / `repeatCount` |
| 7 | 评测器自身 | 判定规则改了，成功率跟着变 | `evaluatorVersion` |
| 8 | 时序与环境 | 时区、并发、限流、外部服务抖动 | 未覆盖，须另存环境信息 |

前七类可以被"输入的一部分"解决，第八类不行——所以项目在 `docs/ARCHITECTURE.md` 里明确写了：Manifest 能说明"什么配置产生了这份报告"，**但它不会自动证明外部模型服务或私有数据从未变化**；正式实验仍需保存原始轨迹、环境信息和人工复核记录。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「八类漂移来源」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md)
