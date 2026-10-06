---
article_id: kp-9c3437a7c08d4e6c
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-90fdb3fa96e7
learning_sourceId: 90fdb3fa96e7
learning_order: 3
learning_objective: 理解并验证：Ollama 与 llama.cpp / GGUF 的关系
---

# Ollama 与 llama.cpp / GGUF 的关系

> **学习目标**：能够解释「Ollama 与 llama.cpp / GGUF 的关系」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：命令行基础、环境变量概念、HTTP/REST 基础、Python 与虚拟环境。
>
> **所属主题**：-本地部署与Ollama · 关键机制

## 本次只学这一点

Ollama 底层基于 **llama.cpp** 推理引擎，模型以 **GGUF** 格式分发：

| 层次 | 说明 |
|---|---|
| 模型文件格式 | GGUF：把权重、量化参数、词表、对话模板打包在一个文件里 |
| 推理引擎 | llama.cpp：CPU/GPU 混合推理，支持多种量化 |
| Ollama 的角色 | 模型管理（拉取/缓存/切换）+ 会话管理 + HTTP 服务 + Modelfile 定制 |

**这解释了三个常见现象**：① 为什么 Ollama 能只靠 CPU 跑（llama.cpp 的 CPU 后端）；
② 为什么模型文件是 `.gguf`、存放在 `~/.ollama/models/blobs`（内容寻址的 blob 存储）；
③ 为什么「换模型」很快——服务端只是卸载旧权重、加载新权重。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/05-推理与部署/06-本地部署与Ollama.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Ollama 与 llama.cpp / GGUF 的关系」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/05-推理与部署/06-本地部署与Ollama.md)
