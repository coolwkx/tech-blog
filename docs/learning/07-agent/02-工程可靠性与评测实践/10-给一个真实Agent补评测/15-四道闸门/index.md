---
article_id: kp-1e89f1f7f894b32d
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-727eecd00fa8
learning_sourceId: 727eecd00fa8
learning_order: 14
learning_objective: 理解并验证：四道闸门
---

# 四道闸门

> **学习目标**：能够解释「四道闸门」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的证据式判定与多标签归因、[02 篇](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md) 的 Manifest 与配对主键、[03 篇](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md) 的 McNemar 与聚类 Bootstrap、[大宗商品价格监控 Agent 复盘](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md) 的规则驱动监控循环。
>
> **所属主题**：-给一个真实Agent补评测 · 评测脚本骨架与基线运行

## 本次只学这一点

| 输入 | 退出码 | 输出 |
| --- | ---: | --- |
| 合法轨迹 | 0 | 报告 + 摘要 |
| 删掉 `notify-retry` 的全部 run | 2 | `输入不合法：任务未执行：['notify-retry']` |
| 同一 `pairKey` 出现两次 | 2 | `输入不合法：baseline 配对主键重复` |
| 某条原本通过的任务变失败 | 1 | `[回归门槛] 回归：snap-single-source::r1::1 由通过变为失败` |
| 篡改 `notify_delivery_id` 的值 | 1 | 该运行 `primaryFailure=invalid_evidence_source` |

退出码 2 与 1 的分工很重要：2 是"数据问题，去看那行 JSON"，1 是"功能回归，去看那次改动"。`_run`/`_task` 里那些抛 `InputError` 的检查作用相同——**任何"数据不完整也能出报告"的口子都会被滥用**。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/04-给一个真实Agent补评测.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「四道闸门」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/04-给一个真实Agent补评测.md)
