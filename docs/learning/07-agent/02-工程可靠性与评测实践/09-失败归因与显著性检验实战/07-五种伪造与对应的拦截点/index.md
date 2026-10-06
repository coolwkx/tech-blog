---
article_id: kp-95edac5dc7b14707
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-8fca08e90f95
learning_sourceId: 8fca08e90f95
learning_order: 6
learning_objective: 理解并验证：五种伪造与对应的拦截点
---

# 五种伪造与对应的拦截点

> **学习目标**：能够解释「五种伪造与对应的拦截点」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的评测器判定顺序与证据信任链、[02 篇](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md) 的 `taskId + repeatId + seed` 配对主键、二项分布与 Bootstrap 重采样的基础。
>
> **所属主题**：-失败归因与显著性检验实战 · 证据式判定：为什么"状态字符串对了"不算通过

## 本次只学这一点

| 伪造手法 | 拦截点 | 结果标签 |
| --- | --- | --- |
| 编一个不存在的 `sourceEventId` | 来源表查不到 `(sourceEventId, claimId)` | `invalid_evidence_source` |
| 指向一个 `success: false` 的 `tool_result` | 来源表只收 `success === true` 的事件 | `invalid_evidence_source` |
| 来源事件存在，但改写 `value` | `value` 不一致 | `invalid_evidence_source` |
| 来源事件存在，值对但改 `contentHash` | `contentHash` 不一致 | `invalid_evidence_source` |
| 证据全对，但最终回答不提它 | `final.citations` 缺少该 claim | `missing_evidence` |

注意第五种故意归到 `missing_evidence` 而不是 `invalid_evidence_source`：证据本身是干净的，问题是**结论与证据脱节**。这个区分让"模型偷懒不写引用"和"模型伪造证据"能被分开统计——前者靠 prompt 工程解决，后者要靠架构上的观测通道隔离。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「五种伪造与对应的拦截点」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md)
