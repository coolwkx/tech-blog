---
article_id: kp-9876c0dc5e6dcda0
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-3dbf2b7f4206
learning_sourceId: 3dbf2b7f4206
learning_order: 3
learning_objective: 理解并验证：记忆的三个基本操作
---

# 记忆的三个基本操作

> **学习目标**：能够解释「记忆的三个基本操作」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[03-LangChain与工具编排](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md) 的 Memory 组件、[06-RAG作为Agent的知识获取手段](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md) 的向量检索、[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的 messages 角色约定。
>
> **所属主题**：-Agent的记忆与知识管理 · 核心概念

## 本次只学这一点

| 操作 | 说明 | 的例子 |
| --- | --- | --- |
| 写入（Write） | 把新信息加入记忆 | `history.add_user_message("在吗？")` |
| 读取（Read） | 取出记忆拼进 prompt | `history.messages` 回传给模型 |
| 遗忘（Forget） | 裁剪或压缩以控制长度 | `history[-max_history_len:]`、`history[-500:]` |

「遗忘」是初学者最容易忽略的一环，但它是记忆系统能否长期运行的决定因素——详见 2.4 与 2.5。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「记忆的三个基本操作」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md)
