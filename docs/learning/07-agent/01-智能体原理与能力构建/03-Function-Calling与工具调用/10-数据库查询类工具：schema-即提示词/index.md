---
article_id: kp-5a01fad666e527ea
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-9a522c2cae70
learning_sourceId: 9a522c2cae70
learning_order: 9
learning_objective: 理解并验证：数据库查询类工具：schema 即提示词
---

# 数据库查询类工具：schema 即提示词

> **学习目标**：能够解释「数据库查询类工具：schema 即提示词」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的 Action 环节、[../llm/05-大模型API与调用实践.md](../../../../../06-llm/06-提示工程/05-大模型API与调用实践.md) 的 `messages` 角色约定。
>
> **所属主题**：-Function-Calling与工具调用 · 关键机制

## 本次只学这一点

第三个示例把 MySQL 表结构写进 `ask_database` 的 `description`：

```text
description: SQL查询提取信息以回答用户的问题。
 查询应该以纯文本返回，而不是JSON。
 SQL应该使用以下数据库模式编写: {database_schema_string}
```

这是「用工具描述注入领域知识」的典型手法，等价于把 schema 作为 few-shot 的一部分交给模型。表结构（`emp` / `DEPT`）声明后，模型就能把「查询一下最高工资的员工姓名及对应的工资」翻译成可执行 SQL，最终返回「KING，工资 5000 元」。

**但必须强调**：让 LLM 生成 SQL 再直接执行，是一条高风险路径。至少要加上只读账号、语句白名单（只允许 `SELECT`）、超时与行数上限。参见 [07-Agent工程化与可靠性设计](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md)。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「数据库查询类工具：schema 即提示词」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)
