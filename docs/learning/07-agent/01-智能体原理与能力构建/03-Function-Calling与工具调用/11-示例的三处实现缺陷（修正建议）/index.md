---
article_id: kp-c978e9077e7a91ca
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-9a522c2cae70
learning_sourceId: 9a522c2cae70
learning_order: 10
learning_objective: 理解并验证：示例的三处实现缺陷（修正建议）
---

# 示例的三处实现缺陷（修正建议）

> **学习目标**：能够解释「示例的三处实现缺陷（修正建议）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的 Action 环节、[../llm/05-大模型API与调用实践.md](../../../../../06-llm/06-提示工程/05-大模型API与调用实践.md) 的 `messages` 角色约定。
>
> **所属主题**：-Function-Calling与工具调用 · 关键机制

## 本次只学这一点

| 位置 | 原文写法 | 问题 | 修正 |
| --- | --- | --- | --- |
| `get_current_weather` | `result1 = eval(response.text)` | `eval` 会执行任意代码，HTTP 响应不可信 | 改用 `json.loads(response.text)` |
| `parse_response` | `message.tool_calls[0]` | 模型可并行返回多个 tool_call，只处理第一个会丢调用 | `for tool_call in message.tool_calls:` 全部处理 |
| `sql_function_tools.py` | `database_schema_string` 与 `database_schema_string1` 先后定义，前者被覆盖 | 单表与多表两个 schema 变量实际只生效一个，示例语义混乱 | 合并为一个 schema 常量，或按库名分文件维护 |

另外这里把 `to_addr`、`from_addr`、`from_pwd` 直接写进源码（仅部分打码），这在真实项目中属于凭证硬编码，应改为环境变量或密钥管理服务。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「示例的三处实现缺陷（修正建议）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)
