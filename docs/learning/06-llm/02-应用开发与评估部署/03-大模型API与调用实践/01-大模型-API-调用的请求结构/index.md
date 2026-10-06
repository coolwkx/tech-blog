---
article_id: kp-328c7d2a7b5092fc
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-563344f304a7
learning_sourceId: 563344f304a7
learning_order: 0
learning_objective: 理解并验证：大模型 API 调用的请求结构
---

# 大模型 API 调用的请求结构

> **学习目标**：能够解释「大模型 API 调用的请求结构」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT 与 MLM 预训练目标（见《02-Transformer与注意力机制》）、Python 与 HTTP 基础、PyTorch 训练循环。
>
> **所属主题**：-大模型API与调用实践 · 核心概念

## 本次只学这一点

主流服务（OpenAI、DeepSeek、通义、智谱、以及本地 Ollama）都提供 **OpenAI 兼容**的
`POST /chat/completions` 接口，请求体核心字段如下：

| 字段 | 类型 | 含义 |
|---|---|---|
| `model` | string | 模型标识，如 `gpt-4o-mini`、`deepseek-chat` |
| `messages` | array | 对话消息列表，每项含 `role` 与 `content` |
| `temperature` | float | 采样随机性，0~2 |
| `top_p` | float | 核采样阈值，0~1 |
| `max_tokens` | int | 生成 token 上限 |
| `stream` | bool | 是否流式返回 |
| `stop` | string/array | 命中即停止生成 |
| `frequency_penalty` | float | 按 token 累计出现次数惩罚 |
| `presence_penalty` | float | 只要出现过就惩罚 |
| `n` | int | 返回候选数 |
| `response_format` | object | 约束为 `json_object`（部分服务支持） |

`messages` 中的 `role` 只有三种：

| role | 作用 | 工程建议 |
|---|---|---|
| `system` | 设定角色、任务、输出格式、边界 | 放稳定不变的规则，便于复用与缓存 |
| `user` | 用户输入 / few-shot 示例的输入 | 用户内容**必须**与指令分隔，防提示注入 |
| `assistant` | 模型历史回复 / few-shot 示例的输出 | 用于多轮对话；few-shot 时人工撰写 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/06-提示工程/05-大模型API与调用实践.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「大模型 API 调用的请求结构」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/06-提示工程/05-大模型API与调用实践.md)
