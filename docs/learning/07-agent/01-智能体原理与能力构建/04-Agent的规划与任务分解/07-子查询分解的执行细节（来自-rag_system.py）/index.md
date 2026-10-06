---
article_id: kp-595a93eec4ed550d
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-21455d0f58d4
learning_sourceId: 21455d0f58d4
learning_order: 6
learning_objective: 理解并验证：子查询分解的执行细节（来自 rag_system.py）
---

# 子查询分解的执行细节（来自 rag_system.py）

> **学习目标**：能够解释「子查询分解的执行细节（来自 rag_system.py）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的五要素、[03-LangChain与工具编排](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md) 的 Task/Crew、[06-RAG作为Agent的知识获取手段](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md) 的检索流程。
>
> **所属主题**：-Agent的规划与任务分解 · 关键机制

## 本次只学这一点

给出的子查询检索实现包含四个动作：

| 步骤 | 代码位置 | 关键细节 |
| --- | --- | --- |
| 1. 生成子查询 | `subquery_prompt` + LLM | 提示词要求「每行一个子查询」，随后按 `\n` 切分并过滤空行 |
| 2. 逐个检索 | `for sub_q in subqueries` | 每个子查询都做一次 `hybrid_search_with_rerank`（含混合检索 + 重排），**开销与子查询数量成正比** |
| 3. 去重合并 | `{doc.page_content: doc for doc in all_docs}` | 用一个 dict 按内容去重；按对象地址去重不可靠，因为内容相同但对象不同无法去重 |
| 4. 数量裁剪 | `final_context_docs = ranked_sub_chunks[:conf.CANDIDATE_M]` | 统一在 `retrieve_and_merge` 末尾限制送入 prompt 的候选数量 |

第 3 步的去重策略值得记住：**用内容做 key**（或更严谨地用文档 ID），而不是用对象哈希。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/02-工具与规划/04-Agent的规划与任务分解.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「子查询分解的执行细节（来自 rag_system.py）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/02-工具与规划/04-Agent的规划与任务分解.md)
