---
article_id: kp-0f5016e671d1fb03
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-21455d0f58d4
learning_sourceId: 21455d0f58d4
learning_order: 12
learning_objective: 理解并验证：任务分解器：分解 → 检索 → 去重 → 裁剪
---

# 任务分解器：分解 → 检索 → 去重 → 裁剪

> **学习目标**：能够解释「任务分解器：分解 → 检索 → 去重 → 裁剪」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的五要素、[03-LangChain与工具编排](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md) 的 Task/Crew、[06-RAG作为Agent的知识获取手段](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md) 的检索流程。
>
> **所属主题**：-Agent的规划与任务分解 · 可运行示例

## 本次只学这一点

下面的例子把 RAG 子查询检索的骨架抽出来，用假 LLM 与假检索器实现，**仅依赖标准库，可直接运行**。

```python
"""任务分解与合并去重的骨架实现（对应 RAG 子查询检索策略）。

依赖：仅标准库。
"""

import json

# ---------- 假知识库 ----------
KNOWLEDGE_BASE = [
{"id": "d1", "text": "Milvus 是面向向量检索的数据库，支持亿级向量的近似最近邻搜索。"},
{"id": "d2", "text": "Milvus 采用分布式架构，可通过增加 query node 水平扩展检索吞吐。"},
{"id": "d3", "text": "Zilliz Cloud 是全托管的 Milvus 服务，免去集群运维，按量计费。"},
{"id": "d4", "text": "Zilliz Cloud 提供自动扩缩容与备份恢复，适合中小团队快速上线。"},
{"id": "d5", "text": "选择向量数据库时需要权衡成本、运维复杂度与数据规模。"},
]

def fake_retriever(query, k=2):
    """极简关键词检索：按查询词与文档的重合度排序，返回 top-k。"""
    tokens = set(query.replace("？", "").replace("，", "").replace(" ", ""))
    scored = []
    for doc in KNOWLEDGE_BASE:
        overlap = len(tokens & set(doc["text"]))
        if overlap:
            scored.append((overlap, doc))
            scored.sort(key=lambda pair: pair[0], reverse=True)
            return [doc for _, doc in scored[:k]]

        # ---------- 假 LLM：把复杂查询拆成子查询 ----------
        def fake_llm_decompose(query):
            if "比较" in query and "优缺点" in query:
                return "Milvus 的优缺点是什么\nZilliz Cloud 的优缺点是什么"
            return query

        def retrieve_with_subqueries(query, k=2, candidate_m=4):
            """子查询检索：分解 → 逐个检索 → 按内容去重 → 裁剪数量。"""
            subqueries_text = fake_llm_decompose(query)
            subqueries = [q.strip() for q in subqueries_text.split("\n") if q.strip()]
            print("生成的子查询:", subqueries)

            all_docs = []
            for sub_q in subqueries:
                docs = fake_retriever(sub_q, k=k)
                print("子查询 %r 检索到 %d 个文档" % (sub_q, len(docs)))
                all_docs.extend(docs)

                # 按内容去重（比按对象地址去重更可靠）
                unique_docs = list({doc["text"]: doc for doc in all_docs}.values())
                print("共检索到 %d 个文档, 去重后剩 %d 个" % (len(all_docs), len(unique_docs)))

                final_docs = unique_docs[:candidate_m]
                print("最终选取 %d 个文档作为上下文" % len(final_docs))
                return final_docs

            if __name__ == "__main__":
                result = retrieve_with_subqueries("比较 Milvus 和 Zilliz Cloud 的优缺点")
                print(json.dumps(result, ensure_ascii=False, indent=2))
```

预期输出（要点）：

```text
生成的子查询: ['Milvus 的优缺点是什么', 'Zilliz Cloud 的优缺点是什么']
子查询 'Milvus 的优缺点是什么' 检索到 2 个文档
子查询 'Zilliz Cloud 的优缺点是什么' 检索到 2 个文档
共检索到 4 个文档, 去重后剩 4 个
最终选取 4 个文档作为上下文
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/02-工具与规划/04-Agent的规划与任务分解.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「任务分解器：分解 → 检索 → 去重 → 裁剪」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/02-工具与规划/04-Agent的规划与任务分解.md)
