---
article_id: kp-94c2d5c198075b74
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-727eecd00fa8
learning_sourceId: 727eecd00fa8
learning_order: 10
learning_objective: 理解并验证：统计方法与预算门槛
---

# 统计方法与预算门槛

> **学习目标**：能够解释「统计方法与预算门槛」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的证据式判定与多标签归因、[02 篇](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md) 的 Manifest 与配对主键、[03 篇](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md) 的 McNemar 与聚类 Bootstrap、[大宗商品价格监控 Agent 复盘](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md) 的规则驱动监控循环。
>
> **所属主题**：-给一个真实Agent补评测 · 指标口径与统计方法

## 本次只学这一点

| 场景 | 方法 | 注意 |
| --- | --- | --- |
| A/B 对比 | 按 `taskId::repeatId::seed` 严格配对 | 重复或孤立主键直接报错，不静默丢弃 |
| 方向性显著性 + 区间 | McNemar exact p-value；以 `taskId` 为聚类单位的 Bootstrap CI | 只看 `fail→pass` 与 `pass→fail`；重采样单位是任务不是运行 |
| 回归 + 成本门槛 | `pass→fail > 0` 直接失败；成功率下限 + 平均步数上限 | 两个成本门槛都要有，否则"更早失败"看起来更省 |

```json
{"budget": {"minSuccessRate": 0.90, "maxAvgSteps": 2.0, "maxRegressions": 0}}
```

`maxRegressions: 0` 是刻意的：**成功率可以因新增难任务而下降并被容忍，但"原本通过的任务现在失败"永远不可接受**，因为它意味着改动破坏了已工作的功能。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/04-给一个真实Agent补评测.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「统计方法与预算门槛」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/04-给一个真实Agent补评测.md)
