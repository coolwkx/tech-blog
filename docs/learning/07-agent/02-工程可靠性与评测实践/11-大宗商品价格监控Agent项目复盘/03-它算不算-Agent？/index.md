---
article_id: kp-ff0e210a6fe4a776
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-4cd0a37cb105
learning_sourceId: 4cd0a37cb105
learning_order: 2
learning_objective: 理解并验证：它算不算 Agent？
---

# 它算不算 Agent？

> **学习目标**：能够解释「它算不算 Agent？」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的五要素、[05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的状态与历史分离、[07-Agent工程化与可靠性设计](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md) 的降级与限流。
>
> **所属主题**：-大宗商品价格监控Agent项目复盘 · 核心概念

## 本次只学这一点

用 [01](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的五要素逐个对照：

| 要素 | 项目中的对应物 | 是否具备 |
| --- | --- | --- |
| Prompt | 无（没有自然语言指令） | ❌ |
| LLM | 无（`ai_analysis.py` 是纯规则计算，名字里的「AI」是营销用语） | ❌ |
| Memory | `commodity_state.json` + `commodity_history.json` | ✅（外部状态/历史记忆） |
| Planning | 固定的阈值规则 `price < buy_threshold` / `price > sell_threshold` | ⚠️ 有决策，但规则由人写死 |
| Action | `requests.post` 推送微信、写 JSON 文件 | ✅ |

结论：它是一个**规则驱动的感知—决策—行动循环**，属于 [01](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 1.2 节里的「反应型 Agent」——根据当前环境状态做出直接反应（温度调节器那一类），而不是目标导向型 Agent。这个判断很重要：**它已经具备 Agent 的骨架，缺的只是「规划由模型生成」这一层**。也正因如此，它非常适合作为「手写循环 → LLM 驱动循环」的改造起点。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「它算不算 Agent？」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md)
