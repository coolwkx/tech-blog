---
article_id: kp-f55d748f8028f6a9
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-8fca08e90f95
learning_sourceId: 8fca08e90f95
learning_order: 9
learning_objective: 理解并验证：汇总计数为什么不能相加
---

# 汇总计数为什么不能相加

> **学习目标**：能够解释「汇总计数为什么不能相加」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的评测器判定顺序与证据信任链、[02 篇](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md) 的 `taskId + repeatId + seed` 配对主键、二项分布与 Bootstrap 重采样的基础。
>
> **所属主题**：-失败归因与显著性检验实战 · 多标签 violations 与 primaryFailure 归因

## 本次只学这一点

条件汇总里 `failures` 的生成方式是**遍历每条结果的每个 violation**：

```ts
for (const result of results) {
  for (const violation of result.violations) {
    failures[violation.code] = (failures[violation.code] ?? 0) + 1;
  }
}
```

于是各标签计数之和 **≥** 失败运行数。举例：6 条运行、2 条通过，剩下 4 条失败：

| 标签 | 计数 |
| --- | ---: |
| `missing_evidence` | 3 |
| `tool_error` | 2 |
| `goal_not_completed` | 4 |
| **合计** | **9** |

9 显然大于 4。报表里写"共有 9 次失败"是错的；正确的是"4 条失败运行，共产生 9 条违规标签"。要拿失败总数，只能用 `runs - passed`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「汇总计数为什么不能相加」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md)
