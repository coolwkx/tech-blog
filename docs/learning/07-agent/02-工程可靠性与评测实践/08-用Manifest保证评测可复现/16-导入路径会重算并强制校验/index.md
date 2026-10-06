---
article_id: kp-08374c178780b3c2
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-cf848e0fe35f
learning_sourceId: cf848e0fe35f
learning_order: 15
learning_objective: 理解并验证：导入路径会重算并强制校验
---

# 导入路径会重算并强制校验

> **学习目标**：能够解释「导入路径会重算并强制校验」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的六段流水线与四道一致性闸门、SHA-256 与规范化（canonicalization）的基本概念、JSON/JSONL 基础。
>
> **所属主题**：-用Manifest保证评测可复现 · 用 taskId + repeatId + seed 作为幂等键

## 本次只学这一点

`results-v1` 输入下 `pairKey` 是显式字段，工具不会盲信，而是**按三段重新计算后比对**：

```ts
const expectedPairKey = `${taskId}::${repeatId}::${seed}`;
if (pairKey !== expectedPairKey) {
  fail(`${path}.pairKey`, `必须由 taskId + repeatId + seed 生成，期望 ${expectedPairKey}`);
}
```

这条校验防的是**通过改主键来改变配对关系**：如果不校验，导入文件可以给两个本该配对的样本编不同的 `pairKey`，让它们变成"孤立配对"从而被统计逻辑忽略——或者更糟，把本该独立的两条编成同一个键。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「导入路径会重算并强制校验」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md)
