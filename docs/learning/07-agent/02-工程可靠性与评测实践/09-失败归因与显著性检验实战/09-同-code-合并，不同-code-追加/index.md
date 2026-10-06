---
article_id: kp-ab18e29f6b0e74c6
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-8fca08e90f95
learning_sourceId: 8fca08e90f95
learning_order: 8
learning_objective: 理解并验证：同 code 合并，不同 code 追加
---

# 同 code 合并，不同 code 追加

> **学习目标**：能够解释「同 code 合并，不同 code 追加」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的评测器判定顺序与证据信任链、[02 篇](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md) 的 `taskId + repeatId + seed` 配对主键、二项分布与 Bootstrap 重采样的基础。
>
> **所属主题**：-失败归因与显著性检验实战 · 多标签 violations 与 primaryFailure 归因

## 本次只学这一点

`addViolation` 做两件事：

```ts
const addViolation = (code, message, evidenceIds?) => {
  const existingIndex = violations.findIndex((v) => v.code === code);
  if (existingIndex !== -1) {
    // 同 code：message 去重拼接，evidenceIds 求并集
    violations[existingIndex] = {
      code,
      message: existing.message.includes(message) ? existing.message
                                                  : `${existing.message}；${message}`,
      ...(mergedIds.length === 0 ? {} : { evidenceIds: mergedIds }),
    };
    return;
  }
  violations.push({ code, message, ...(evidenceIds === undefined ? {} : { evidenceIds }) });
};
```

所以 `missing_evidence` 只会在列表里出现一次，哪怕它由两个独立检查触发（缺验证、缺引用）：message 变成 `"缺少已验证证据：query、count；最终回答未引用证据：count"`，而 `evidenceIds` 是 `["query", "count"]`（并集去重）。直接后果是：

> **`violations.length` 是"不同类别数"，不是"违规条目数"。**

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「同 code 合并，不同 code 追加」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md)
