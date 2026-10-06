---
article_id: kp-b3ee0841a40125cc
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-e94c0577cb2f
learning_sourceId: e94c0577cb2f
learning_order: 11
learning_objective: 理解并验证：双通道融合 + 流式输出
---

# 双通道融合 + 流式输出

> **学习目标**：能够解释「双通道融合 + 流式输出」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 工程化基础、向量检索原理（Embedding / 余弦相似度 / ANN）、LangChain 的 Document 与 TextSplitter 抽象、FastAPI 基础、MySQL 与 Redis 基本操作。
>
> **所属主题**：项目实战笔记 01：法律咨询 RAG 问答系统 · 核心实现

## 本次只学这一点

```python
class IntegratedQASystem:
    def query(self, query, source_filter=None, session_id=None):
        history = self.get_session_history(session_id) if session_id else []
        answer, need_rag = self.bm25_search.search(query, threshold=0.85)
        if answer: # FAQ 命中，一次性返回
            if session_id: self.update_session_history(session_id, query, answer)
            yield answer, True
            return
        if need_rag: # 兜底：流式生成
            collected = ""
            for token in self.rag_system.generate_answer(query, source_filter, history):
                collected += token
                yield token, False
                if session_id: self.update_session_history(session_id, query, collected)
                yield "", True
            else:
                yield "未找到答案", True
```

`conversations` 表按 `session_id` 保留最近 5 轮，超出部分在同一个事务里删除：

```sql
DELETE FROM conversations
WHERE session_id = %s AND id NOT IN (
 SELECT id FROM (
 SELECT id FROM conversations WHERE session_id = %s
 ORDER BY timestamp DESC LIMIT %s
 ) AS sub
)
```

**注意**：MySQL 不允许在 `DELETE` 的子查询里直接引用被删的表，必须再套一层派生表 `AS sub`，这是很多人写会话裁剪时会踩的语法坑。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/01-问答与RAG系统/01-项目-法律咨询RAG问答系统.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「双通道融合 + 流式输出」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/01-问答与RAG系统/01-项目-法律咨询RAG问答系统.md)
