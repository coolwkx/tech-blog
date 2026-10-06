---
article_id: kp-322ab0602a018d26
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-727eecd00fa8
learning_sourceId: 727eecd00fa8
learning_order: 13
learning_objective: 理解并验证：跑一次基线
---

# 跑一次基线

> **学习目标**：能够解释「跑一次基线」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的证据式判定与多标签归因、[02 篇](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md) 的 Manifest 与配对主键、[03 篇](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md) 的 McNemar 与聚类 Bootstrap、[大宗商品价格监控 Agent 复盘](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md) 的规则驱动监控循环。
>
> **所属主题**：-给一个真实Agent补评测 · 评测脚本骨架与基线运行

## 本次只学这一点

四任务（`snap-single-source` / `multi-source-conflict` / `notify-retry` / `timezone-bucket`）各跑 baseline 与 optimized：

```bash
python monitor_eval.py --input monitor-runs.json --output reports/baseline.json
```

```text
baseline  25.0% (1/4)  平均步数 1.00
optimized 100.0% (4/4)  平均步数 1.25
配对 4：fail->pass=3 pass->fail=0  p=0.2500
task-cluster 95% CI = [+0.2500, +1.0000]（4 个任务簇）
baseline 失败标签：assertion_failed=2、goal_not_completed=2、missing_evidence=2、tool_error=1
```

**这份基线最重要的信息不是 100%，而是 `p=0.2500` 和宽度 0.75 的置信区间。** 4 个任务簇给出的区间几乎覆盖整个 `[0, 1]`，说明"提升到 100%"**完全没有统计支撑**——它只是 4 条合成任务的演示。生产接入必须先跑 30–50 条任务再谈显著性（见 [03 篇](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md) 5.5 节）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/04-给一个真实Agent补评测.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「跑一次基线」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/04-给一个真实Agent补评测.md)
