---
article_id: kp-7c693bc3e162149d
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-cf848e0fe35f
learning_sourceId: cf848e0fe35f
learning_order: 14
learning_objective: 理解并验证：幂等键的三重作用
---

# 幂等键的三重作用

> **学习目标**：能够解释「幂等键的三重作用」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的六段流水线与四道一致性闸门、SHA-256 与规范化（canonicalization）的基本概念、JSON/JSONL 基础。
>
> **所属主题**：-用Manifest保证评测可复现 · 用 taskId + repeatId + seed 作为幂等键

## 本次只学这一点

**① 防覆盖。** 统计层构建配对字典时，同一 `pairKey` 出现两次直接抛错：

```ts
for (const result of results) {
  if (byPair.has(result.pairKey)) throw new Error(`Duplicate ${condition} pair key: ${result.pairKey}`);
  byPair.set(result.pairKey, result);
}
```

"重跑覆盖"是最隐蔽的数据污染：文件系统上看起来只多了一个新文件，实际报告里的分母换了。抛错比"以最后一次为准"安全得多——因为它逼你去查**为什么同一个键会出现两次**（通常是调度脚本重复触发或断点续跑没做去重）。

**② 保证配对。** 两侧的 key 集合必须完全相同：

```ts
if (baselineKeys.join("\n") !== optimizedKeys.join("\n")) {
  throw new Error(`Unpaired results: missing optimized [...] ; missing baseline [...]`);
}
```

这一条保证成功率、`fail→pass`/`pass→fail`、McNemar 三者用的是**同一批有效配对**。如果允许"有的 key 只有 baseline、有的只有 optimized"，那么成功率的分母和 McNemar 的样本量就会不同，两个数字之间的任何推断都是错的。

**③ 断点续跑与缓存。** 幂等键是天然的续跑单位：跑完一个 `(taskId, repeatId, seed)` 就落一条结果，中断后重跑时按它去重。这也是它被叫做"幂等键"的原因——同一键重复执行，状态不叠加。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「幂等键的三重作用」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md)
