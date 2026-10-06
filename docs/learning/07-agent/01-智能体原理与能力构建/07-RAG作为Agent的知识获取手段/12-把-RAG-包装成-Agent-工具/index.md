---
article_id: kp-6cbf08aa0be024f2
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-d130ec37c55d
learning_sourceId: d130ec37c55d
learning_order: 11
learning_objective: 理解并验证：把 RAG 包装成 Agent 工具
---

# 把 RAG 包装成 Agent 工具

> **学习目标**：能够解释「把 RAG 包装成 Agent 工具」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的外部知识记忆、[04-Agent的规划与任务分解](../../../../../07-agent/02-工具与规划/04-Agent的规划与任务分解.md) 的查询改写策略、[../llm/07-向量数据库与Milvus.md](../../../../../06-llm/07-检索增强RAG/07-向量数据库与Milvus.md)。
>
> **所属主题**：-RAG作为Agent的知识获取手段 · 关键机制

## 本次只学这一点

> **说明**：本小节超出本节范围，为通用知识补充，用于把 RAG 接进 [02](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的工具协议。

把检索器注册成一个工具，Agent 就能**自主决定何时检索**（而不是像 2.5 那样用固定分类器路由）：

```json
{
 "type": "function",
 "function": {
 "name": "search_knowledge_base",
 "description": "在企业知识库中检索与问题相关的文档片段。当问题涉及、学费、政策等企业私有信息时使用。",
 "parameters": {
 "type": "object",
 "properties": {
 "query": {"type": "string", "description": "检索用的自然语言问题"},
 "source": {"type": "string", "description": "可选，学科过滤，如 ai / java"}
 },
 "required": ["query"]
 }
 }
}
```

两者的差别：

| 方式 | 决策者 | 优点 | 缺点 |
| --- | --- | --- | --- |
| 分类器路由（做法） | 独立小模型 | 快（BERT 一次前向）、成本低、可控 | 只有「检索 / 不检索」两档，不够灵活 |
| 检索即工具 | 主 LLM | 灵活，可多轮检索、可与其他工具组合 | 每次决策都消耗主模型 token，延迟更高 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「把 RAG 包装成 Agent 工具」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md)
