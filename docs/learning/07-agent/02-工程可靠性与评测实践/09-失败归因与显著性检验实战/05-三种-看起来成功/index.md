---
article_id: kp-a991a48027c4b09f
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-8fca08e90f95
learning_sourceId: 8fca08e90f95
learning_order: 4
learning_objective: 理解并验证：三种"看起来成功"
---

# 三种"看起来成功"

> **学习目标**：能够解释「三种"看起来成功"」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的评测器判定顺序与证据信任链、[02 篇](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md) 的 `taskId + repeatId + seed` 配对主键、二项分布与 Bootstrap 重采样的基础。
>
> **所属主题**：-失败归因与显著性检验实战 · 证据式判定：为什么"状态字符串对了"不算通过

## 本次只学这一点

| 反例 | 表面证据 | 为什么不算通过 | 对应标签 |
| --- | --- | --- | --- |
| 模型直接输出"已完成搜索，共 42 条" | `final.text` 含关键词、`status=completed` | 没有任何 `tool_call`，42 是编的 | `zero_step_termination` |
| 页面加载成功，模型说"页面正常" | 工具返回 200、`status=completed` | 用户要的信息没被提取，`requiredEvidence` 里没有任何 claim 被验证 | `missing_evidence` |
| 遇到登录墙，模型声称"任务完成" | 有一条 `verification` 事件自报 `blocker=登录墙` | 该声明无法绑定到成功 `tool_result` 的产出 | `invalid_evidence_source` |

第三种最隐蔽：它**同时**有一条看起来合法的 `verification` 事件和一句完整的话。如果判定逻辑是"检查最终回答里有没有'完成'且有没有 verification 事件"，它就会通过。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「三种"看起来成功"」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md)
