---
article_id: kp-1c2776202e396c37
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-90fdb3fa96e7
learning_sourceId: 90fdb3fa96e7
learning_order: 6
learning_objective: 理解并验证：Modelfile：把 Prompt 与参数固化成一个新模型
---

# Modelfile：把 Prompt 与参数固化成一个新模型

> **学习目标**：能够解释「Modelfile：把 Prompt 与参数固化成一个新模型」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：命令行基础、环境变量概念、HTTP/REST 基础、Python 与虚拟环境。
>
> **所属主题**：-本地部署与Ollama · 关键机制

## 本次只学这一点

`ollama create` 的核心是 Modelfile（类似 Dockerfile 的思路）。

| 指令 | 作用 | 示例 |
|---|---|---|
| `FROM` | 指定基座模型或 GGUF 文件（**必需**） | `FROM qwen2:7b` |
| `SYSTEM` | 固定系统提示词 | `SYSTEM 你是一名严谨的金融分析师。` |
| `TEMPLATE` | 对话模板（不同模型格式不同） | `TEMPLATE """{{ .System }}\n{{ .Prompt }}"""` |
| `PARAMETER` | 默认推理参数 | `PARAMETER temperature 0.2`、`PARAMETER num_ctx 8192` |
| `ADAPTER` | 加载 LoRA adapter（把微调结果接上） | `ADAPTER ./lora-adapter` |
| `LICENSE` / `MESSAGE` | 许可信息 / 预置对话示例 | `MESSAGE user 你好` |

```text
# 文件名：Modelfile.finance
FROM qwen2:7b
PARAMETER temperature 0.2
PARAMETER num_ctx 8192
PARAMETER top_p 0.9
SYSTEM """你是一名严谨的金融文本分析助手。
只依据用户提供的原文作答，原文未提及的信息一律回答「原文中未提及」。
输出使用简体中文，不使用营销化措辞。"""
```

```bash
ollama create finance-qwen -f Modelfile.finance
ollama run finance-qwen
```

**为什么要这样做**：把「系统提示 + 参数」从应用代码里挪到模型定义里，
可以让同一个应用通过**切换模型名**就获得不同的角色与参数，避免 prompt 在代码中四处散落、难以版本管理。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/05-推理与部署/06-本地部署与Ollama.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Modelfile：把 Prompt 与参数固化成一个新模型」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/05-推理与部署/06-本地部署与Ollama.md)
