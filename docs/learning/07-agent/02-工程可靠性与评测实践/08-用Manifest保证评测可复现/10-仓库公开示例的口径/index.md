---
article_id: kp-2a5e4180cdcd61df
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-cf848e0fe35f
learning_sourceId: cf848e0fe35f
learning_order: 9
learning_objective: 理解并验证：仓库公开示例的口径
---

# 仓库公开示例的口径

> **学习目标**：能够解释「仓库公开示例的口径」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的六段流水线与四道一致性闸门、SHA-256 与规范化（canonicalization）的基本概念、JSON/JSONL 基础。
>
> **所属主题**：-用Manifest保证评测可复现 · 数据集哈希与提示词哈希的计算方式

## 本次只学这一点

`examples/public-evidence/README.md` 把哈希推导规则写得很直白，可以逐位复核：

- `promptHash`：字符串 `Evaluate each synthetic trajectory using evidence-bound completion rules.` 的 SHA-256；
- `dataset.hash`：稳定数据集标识 `agent-eval-lab-public-synthetic-v1` 的 SHA-256。

注意 `dataset.hash` 这里哈希的是**一个标识字符串**，不是数据集内容。这是一个**公开演示的简化**：它证明"哈希链路可复算"，但不提供"内容一变哈希就变"的防篡改能力。生产实验应该哈希内容本身，见 3.4。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「仓库公开示例的口径」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md)
