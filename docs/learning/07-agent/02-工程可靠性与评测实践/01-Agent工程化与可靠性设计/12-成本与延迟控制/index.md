---
article_id: kp-51e2fbda41e43465
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-0ae5654d8e63
learning_sourceId: 0ae5654d8e63
learning_order: 11
learning_objective: 理解并验证：成本与延迟控制
---

# 成本与延迟控制

> **学习目标**：能够解释「成本与延迟控制」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的工具协议与错误处理、[05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的状态持久化、[08-大宗商品价格监控Agent项目复盘](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md)。
>
> **所属主题**：-Agent工程化与可靠性设计 · 关键机制

## 本次只学这一点

| 手段 | 的位置 | 效果 |
| --- | --- | --- |
| 意图分类后再决定是否检索 | RAG `QueryClassifier` | 通用知识跳过检索与重排 |
| 候选数量上限 | `context_docs[:conf.CANDIDATE_M]` | 控制 prompt 长度 |
| 少于 2 个文档时跳过重排 | `if len(parent_docs) < 2` | 省一次 CrossEncoder 推理 |
| 推理用 CPU/FP16 取舍 | `BGEM3EmbeddingFunction(use_fp16=False, device="cpu")` | 无 GPU 也能跑，代价是速度 |
| 检查间隔与通知间隔解耦 | `check_interval_seconds` / `notify_interval_seconds` | 高频感知、低频打扰 |
| 历史窗口截断 | `history[-max_history_len:]` / `[-500:]` | 防止数据与 token 无限增长 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「成本与延迟控制」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md)
