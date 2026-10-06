---
article_id: kp-13b3064730a8fc30
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-8fca08e90f95
learning_sourceId: 8fca08e90f95
learning_order: 10
learning_objective: 理解并验证：primaryFailure 的兼容策略
---

# primaryFailure 的兼容策略

> **学习目标**：能够解释「primaryFailure 的兼容策略」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的评测器判定顺序与证据信任链、[02 篇](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md) 的 `taskId + repeatId + seed` 配对主键、二项分布与 Bootstrap 重采样的基础。
>
> **所属主题**：-失败归因与显著性检验实战 · 多标签 violations 与 primaryFailure 归因

## 本次只学这一点

`EvaluationResult` 同时带 `failureType` 与 `primaryFailure`，且始终相等；`failureType` 是 v0.1/v0.2 的兼容别名。这个策略有两个值得学的点：

1. **兼容字段不删，但明确标注废弃。** 类型定义上写了 `/** @deprecated 使用 primaryFailure。保留该字段以兼容 v0.1/v0.2 消费方。 */`。旧消费者继续工作，新消费者看到废弃标记。
2. **导入路径严查两者一致。** `if (failureType !== primaryFailure) fail(...)`。这让"兼容"不至于变成"两个字段可以不一致"的漏洞。

同样的严格性还体现在三个自洽性检查上：

```ts
if (passed && (primaryFailure !== "none" || violations.length > 0)) fail(path, "passed=true 时 primaryFailure 必须为 none 且 violations 必须为空");
if (!passed && primaryFailure === "none") fail(`${path}.primaryFailure`, "passed=false 时不能为 none");
if (!passed && violations[0]?.code !== primaryFailure) fail(`${path}.violations[0].code`, "首个 violation 必须与 primaryFailure 一致");
if (JSON.stringify(reasons) !== JSON.stringify(violationReasons)) fail(`${path}.reasons`, "必须与 violations 的 message 按顺序完全一致");
```

这四条合起来保证：**一份能通过校验的输入文件，其 `passed`、`primaryFailure`、`violations`、`reasons` 四者不可能互相矛盾。** 换句话说，导入路径虽然把判定权交给了外部，但把"自洽性"牢牢攥在手里。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「primaryFailure 的兼容策略」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md)
