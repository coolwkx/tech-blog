---
article_id: kp-c54c1032c5f4805f
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-cf848e0fe35f
learning_sourceId: cf848e0fe35f
learning_order: 7
learning_objective: 理解并验证：示例输入里的轨迹记录
---

# 示例输入里的轨迹记录

> **学习目标**：能够解释「示例输入里的轨迹记录」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的六段流水线与四道一致性闸门、SHA-256 与规范化（canonicalization）的基本概念、JSON/JSONL 基础。
>
> **所属主题**：-用Manifest保证评测可复现 · Manifest 字段逐个讲解

## 本次只学这一点

Manifest 之外，输入还有两种形态。JSONL 用显式 `recordType` 逐行承载，且**禁止混用 `run` 与 `result`**：

```jsonl
{"recordType":"manifest","data":{"schema":"agent-eval-lab-manifest-v1","experimentId":"..."}}
{"recordType":"task","data":{"taskId":"easy-01","difficulty":"easy","objective":"...","requiredEvidence":["title"]}}
{"recordType":"run","data":{"runId":"baseline-easy-01-r1","taskId":"easy-01","condition":"baseline","repeatId":"r1","seed":1,"status":"completed","events":[]}}
```

解析规则里有几条很实用的细节：空行与 `#` 开头的注释行被跳过；必须**恰好**包含 1 条 `manifest`；可以一条 `task` 都没有（但 `results-v1` 输入带 `task` 记录会被拒绝）；任意一行 JSON 语法错误都会带上行号 `$line[17]`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「示例输入里的轨迹记录」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md)
