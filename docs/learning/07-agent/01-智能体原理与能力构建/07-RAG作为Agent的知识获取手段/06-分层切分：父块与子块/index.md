---
article_id: kp-cfc1eb46e251020d
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-d130ec37c55d
learning_sourceId: d130ec37c55d
learning_order: 5
learning_objective: 理解并验证：分层切分：父块与子块
---

# 分层切分：父块与子块

> **学习目标**：能够解释「分层切分：父块与子块」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的外部知识记忆、[04-Agent的规划与任务分解](../../../../../07-agent/02-工具与规划/04-Agent的规划与任务分解.md) 的查询改写策略、[../llm/07-向量数据库与Milvus.md](../../../../../06-llm/07-检索增强RAG/07-向量数据库与Milvus.md)。
>
> **所属主题**：-RAG作为Agent的知识获取手段 · 关键机制

## 本次只学这一点

`process_documents()` 的切分策略是**两层**：

| 层级 | 切分器 | 大小参数 | 用途 |
| --- | --- | --- | --- |
| 父块 | `ChineseRecursiveTextSplitter`（Markdown 文件用 `MarkdownTextSplitter`） | `PARENT_CHUNK_SIZE` | 提供完整语义上下文 |
| 子块 | 同上，更小 | `CHILD_CHUNK_SIZE`，重叠 `CHUNK_OVERLAP` | 参与向量检索，精度更高 |

切分时写入的元数据：

| 字段 | 生成方式 | 作用 |
| --- | --- | --- |
| `parent_id` | `f"doc_{i}_parent_{j}"` | 定位父块 |
| `parent_content` | 父块的 `page_content`（冗余存在子块元数据里） | 命中子块后直接替换为完整上下文，无需二次查库 |
| `id` | `f"{parent_id}_child_{k}"` | 子块唯一标识 |
| `source` / `file_path` / `timestamp` | 加载阶段注入 | 过滤与溯源 |

**为什么值得这么做**：小块的向量表达更聚焦，检索命中率高；但小块缺少上下文，直接交给 LLM 容易答不完整。父子块结构让「小块的召回精度」与「大块的语义完整性」同时成立。代价是元数据冗余存储（每个子块都存一份父块内容）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「分层切分：父块与子块」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md)
