---
article_id: kp-17c13e5b666b67e2
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-90fdb3fa96e7
learning_sourceId: 90fdb3fa96e7
learning_order: 1
learning_objective: 理解并验证：四种调用方式一览
---

# 四种调用方式一览

> **学习目标**：能够解释「四种调用方式一览」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：命令行基础、环境变量概念、HTTP/REST 基础、Python 与虚拟环境。
>
> **所属主题**：-本地部署与Ollama · 核心概念

## 本次只学这一点

| 方式 | 依赖 | 适用场景 | 关键点 |
|---|---|---|---|
| CLI（`ollama run`） | 无 | 快速验证、手动对话 | 交互式 REPL，`Ctrl+D` 退出 |
| `ollama` Python 库 | `pip install ollama` | Python 项目内调用 | 官方 SDK，最简洁；支持 `Client(host=...)` 远程调用 |
| `requests` 直连 REST | `pip install requests` | 跨语言、精细控制请求体 | `POST /api/chat`、`/api/generate`，可完全控制 `options` |
| LangChain 集成 | `langchain`、`langchain_community` | 构建 RAG/Agent 链路 | `Ollama(base_url=..., model=..., temperature=0)` |

同一个问题「为什么天空是蓝色的？」在四种方式下的写法见第 3 节。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/05-推理与部署/06-本地部署与Ollama.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「四种调用方式一览」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/05-推理与部署/06-本地部署与Ollama.md)
