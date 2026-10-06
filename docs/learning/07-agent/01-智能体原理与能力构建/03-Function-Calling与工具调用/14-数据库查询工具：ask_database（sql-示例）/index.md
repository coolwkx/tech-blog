---
article_id: kp-fe86607d715c9d0f
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-9a522c2cae70
learning_sourceId: 9a522c2cae70
learning_order: 13
learning_objective: 理解并验证：数据库查询工具：ask_database（sql 示例）
---

# 数据库查询工具：ask_database（sql 示例）

> **学习目标**：能够解释「数据库查询工具：ask_database（sql 示例）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的 Action 环节、[../llm/05-大模型API与调用实践.md](../../../../../06-llm/06-提示工程/05-大模型API与调用实践.md) 的 `messages` 角色约定。
>
> **所属主题**：-Function-Calling与工具调用 · 可运行示例

## 本次只学这一点

**依赖**：`pip install pymysql`。

预期输出（结果展示）：

```text
[{"ename": "KING", "sal": 5000}]
```

模型最终把这个结果组织成自然语言：「根据您的查询，我已经为您找到了工资最高的员工。这位员工的姓名是 KING，他的工资是 5000 元。」

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「数据库查询工具：ask_database（sql 示例）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)
