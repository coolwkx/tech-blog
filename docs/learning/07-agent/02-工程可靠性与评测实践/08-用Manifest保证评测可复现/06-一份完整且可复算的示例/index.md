---
article_id: kp-654983841cc0d94d
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-cf848e0fe35f
learning_sourceId: cf848e0fe35f
learning_order: 5
learning_objective: 理解并验证：一份完整且可复算的示例
---

# 一份完整且可复算的示例

> **学习目标**：能够解释「一份完整且可复算的示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的六段流水线与四道一致性闸门、SHA-256 与规范化（canonicalization）的基本概念、JSON/JSONL 基础。
>
> **所属主题**：-用Manifest保证评测可复现 · Manifest 字段逐个讲解

## 本次只学这一点

下面这份 Manifest 不是编的——它是仓库 `examples/public-evidence/input-results.json` 里的真实内容，两个哈希都可以用第 3 节的代码逐位复算：

```json
{
  "schema": "agent-eval-lab-manifest-v1",
  "experimentId": "public-synthetic-evidence-v1",
  "createdAt": "2026-08-19T00:00:00.000Z",
  "model": { "provider": "fixture", "name": "deterministic-synthetic-agent", "revision": "v1" },
  "promptHash": "sha256:59385ca68f462dd301e9866b7e918dafd1cc466d5779d9a2d8d7acbe7091fedc",
  "codeCommit": "74f4a3a",
  "dataset": {
    "name": "agent-eval-lab-public-synthetic-v1",
    "hash": "sha256:af71072674c8e544ed7154cc99a7bf815c050c9dc693e2ca7ff38f783f24ddb2"
  },
  "taskIds": ["easy-title", "medium-search", "hard-block"],
  "seeds": [1],
  "repeatCount": 1,
  "evaluatorVersion": "0.3.0",
  "data": { "classification": "synthetic", "containsPrivateData": false, "redacted": true },
  "notes": ["完全合成的公开演示；不代表真实 Agent 表现。", "哈希推导规则记录在 examples/public-evidence/README.md。"]
}
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「一份完整且可复算的示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md)
