---
article_id: kp-e1f35b7ee08024d8
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-9a522c2cae70
learning_sourceId: 9a522c2cae70
learning_order: 6
learning_objective: 理解并验证：tool schema 的字段含义
---

# tool schema 的字段含义

> **学习目标**：能够解释「tool schema 的字段含义」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的 Action 环节、[../llm/05-大模型API与调用实践.md](../../../../../06-llm/06-提示工程/05-大模型API与调用实践.md) 的 `messages` 角色约定。
>
> **所属主题**：-Function-Calling与工具调用 · 关键机制

## 本次只学这一点

`tools` 是一个列表，每一项遵循 OpenAI 的函数定义格式。以下是从天气示例还原出的完整结构（补全了被排版打散的层级）：

| 字段 | 层级 | 作用 | 天气示例的值 |
| --- | --- | --- | --- |
| `type` | 顶层 | 固定为 `function` | `"function"` |
| `function.name` | 第二层 | 函数名，模型回传时的唯一标识 | `"get_current_weather"` |
| `function.description` | 第二层 | **给模型看的自然语言说明**，决定何时选中该工具 | `"获取给定位置的当前天气"` |
| `function.parameters()` | 第二层 | JSON Schema，描述参数结构 | `{"type": "object", ...}` |
| `parameters.type` | 第三层 | 参数整体类型 | `"object"` |
| `parameters.properties` | 第三层 | 各参数的名称、类型与说明 | `{"location": {...}}` |
| `parameters.required` | 第三层 | 必填参数列表 | `["location"]` |
| `properties.<name>.type` | 第四层 | 参数类型 | `"string"` |
| `properties.<name>.description` | 第四层 | 参数含义，影响模型填值准确率 | `"城市或区，例如北京、海淀"` |

三条经验规则：

1. **`description` 就是给模型的 API 文档**，写得越具体，误选与参数填错越少；
2. `required` 不是形式约束——模型会据此判断「信息不足时是否应该先向用户追问」；
3. 参数名要与真实函数的形参名完全一致，否则 `**kwargs` 展开时会直接抛 `TypeError`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「tool schema 的字段含义」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)
