---
article_id: kp-930a5d065a8aa6e5
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-8fca08e90f95
learning_sourceId: 8fca08e90f95
learning_order: 5
learning_objective: 理解并验证：证据信任链
---

# 证据信任链

> **学习目标**：能够解释「证据信任链」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的评测器判定顺序与证据信任链、[02 篇](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md) 的 `taskId + repeatId + seed` 配对主键、二项分布与 Bootstrap 重采样的基础。
>
> **所属主题**：-失败归因与显著性检验实战 · 证据式判定：为什么"状态字符串对了"不算通过

## 本次只学这一点

项目把"证据可信"拆成三段必须同时成立的检查：

```text
第一段：来源必须真实 —— verification 声明的每条 EvidenceRecord 必须能在
        「成功的 tool_result 事件」的产出表里找到，key 是 (sourceEventId, claimId)，
        且要求 record.sourceEventId === 该事件的 eventId
第二段：内容必须一致 —— 来源表里的 value / contentHash 必须等于声明里的值
第三段：必须被引用 —— final 事件的 citations 必须包含任务要求的每个 claim
```

第一段的实现有个容易漏掉的细节——构建来源表时要求 `sourceEventId` **自指**：

```ts
for (const event of run.events) {
  if (event.type !== "tool_result" || event.success !== true) continue;   // 失败工具不产出可信证据
  for (const record of event.evidence ?? []) {
    if (record.sourceEventId !== event.eventId) continue;                 // 必须由本事件产出
    sourceEvidence.set(`${event.eventId}::${record.claimId}`, {
      value: record.value,
      contentHash: record.contentHash,
    });
  }
}
```

没有这道自指检查，一个 `tool_result` 就可以"代持"任意其他事件的证据，来源图立刻失去意义。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「证据信任链」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md)
