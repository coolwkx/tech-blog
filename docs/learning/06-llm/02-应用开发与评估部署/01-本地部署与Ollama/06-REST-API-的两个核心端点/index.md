---
article_id: kp-7bd26203d4d0dbb9
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-90fdb3fa96e7
learning_sourceId: 90fdb3fa96e7
learning_order: 5
learning_objective: 理解并验证：REST API 的两个核心端点
---

# REST API 的两个核心端点

> **学习目标**：能够解释「REST API 的两个核心端点」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：命令行基础、环境变量概念、HTTP/REST 基础、Python 与虚拟环境。
>
> **所属主题**：-本地部署与Ollama · 关键机制

## 本次只学这一点

| 端点 | 用途 | 关键字段 |
|---|---|---|
| `POST /api/generate` | 单轮文本补全 | `model`、`prompt`、`stream`、`options` |
| `POST /api/chat` | 多轮对话（推荐） | `model`、`messages`、`stream`、`options` |
| `GET /api/tags` | 列出本地模型 | — |
| `POST /api/pull` | 拉取模型 | `name` |
| `POST /api/embed` | 生成 embedding（用于 RAG） | `model`、`input` |
| `GET /api/version` | 服务版本（可用于健康检查） | — |

**`options` 里放的是采样参数**：`temperature`、`top_p`、`num_ctx`（上下文长度）、`num_predict`（最大生成 token）等。
的注释很直白：`temperature`「为 0 表示不让模型自由发挥，输出结果相对较固定，>0 的话，输出的结果会比较放飞自我」。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/05-推理与部署/06-本地部署与Ollama.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「REST API 的两个核心端点」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/05-推理与部署/06-本地部署与Ollama.md)
