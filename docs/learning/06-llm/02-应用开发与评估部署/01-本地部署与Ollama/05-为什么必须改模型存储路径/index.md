---
article_id: kp-740e168b22ca791c
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-90fdb3fa96e7
learning_sourceId: 90fdb3fa96e7
learning_order: 4
learning_objective: 理解并验证：为什么必须改模型存储路径
---

# 为什么必须改模型存储路径

> **学习目标**：能够解释「为什么必须改模型存储路径」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：命令行基础、环境变量概念、HTTP/REST 基础、Python 与虚拟环境。
>
> **所属主题**：-本地部署与Ollama · 关键机制

## 本次只学这一点

| 项 | 说明 |
|---|---|
| 默认路径 | Windows：`C:\Users\%username%\.ollama\models`；Linux/macOS：`~/.ollama/models` |
| 环境变量 | `OLLAMA_MODELS`（**必须配置**，明确要求） |
| 示例值 | `D:\Work\ollama\models` |
| 为什么 | 7B 模型量化后也是数 GB，13B/70B 更大；装在系统盘会持续挤占空间并影响电脑运行速度 |

**关键操作顺序**：先**退出 Ollama**（右下角图标 → Quit Ollama）再改环境变量，
否则配置无法生效；改完后从「开始」菜单重新启动 Ollama。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/05-推理与部署/06-本地部署与Ollama.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「为什么必须改模型存储路径」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/05-推理与部署/06-本地部署与Ollama.md)
