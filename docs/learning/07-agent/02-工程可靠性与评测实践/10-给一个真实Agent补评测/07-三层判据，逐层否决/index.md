---
article_id: kp-d67b7856cb1666f5
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-727eecd00fa8
learning_sourceId: 727eecd00fa8
learning_order: 6
learning_objective: 理解并验证：三层判据，逐层否决
---

# 三层判据，逐层否决

> **学习目标**：能够解释「三层判据，逐层否决」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的证据式判定与多标签归因、[02 篇](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md) 的 Manifest 与配对主键、[03 篇](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md) 的 McNemar 与聚类 Bootstrap、[大宗商品价格监控 Agent 复盘](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md) 的规则驱动监控循环。
>
> **所属主题**：-给一个真实Agent补评测 · 成功判据与证据要求

## 本次只学这一点

```text
第一层 完整性门：轨迹非空 / 有 tool_call / final 非空
      ↓ 不过 → missing_trajectory · zero_step_termination · empty_final_answer
第二层 状态断言：finalState 的每个 key 等于期望值
      ↓ 不过 → assertion_failed
第三层 证据门：每条 requiredEvidence 都来自成功 tool_result、值/哈希一致、被 final 引用
      ↓ 不过 → invalid_evidence_source · missing_evidence
      ↓ 全过 → PASS
```

**为什么状态断言也要有证据？** 因为状态是系统自己写的。`state.notifyDelivered=true` 完全可能在 HTTP 请求**之前**就写好了（1.3 节的"状态推进了、副作用没发生"）。判据必须成对：**断言说"结果是什么"，证据说"这个结果怎么来的"。**

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/04-给一个真实Agent补评测.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「三层判据，逐层否决」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/04-给一个真实Agent补评测.md)
