---
article_id: kp-192fc62d394c607d
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-757657a4bcd5
learning_sourceId: 757657a4bcd5
learning_order: 8
learning_objective: 理解并验证：示例一：检索侧指标计算器
---

# 示例一：检索侧指标计算器

> **学习目标**：能够解释「示例一：检索侧指标计算器」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[06-RAG作为Agent的知识获取手段](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md) 的检索链路、[02-评测指标设计](../../../../../07-agent/05-评测/02-评测指标设计.md) 的指标口径、[03-评测方法-单元测试与LLM即裁判](../../../../../07-agent/05-评测/03-评测方法-单元测试与LLM即裁判.md) 的 Judge 校准。
>
> **所属主题**：-RAG与多轮对话评测 · 可运行示例

## 本次只学这一点

```python
"""检索侧指标：Recall@k / Precision@k / Hit@k / MRR / nDCG@k。

依赖：仅标准库。
"""

import math
from typing import Dict, List, Sequence


def recall_at_k(retrieved: Sequence[str], relevant: Sequence[str], k: int) -> float:
    gold = set(relevant)
    if not gold:
        return 1.0
    return len(set(retrieved[:k]) & gold) / len(gold)


def precision_at_k(retrieved: Sequence[str], relevant: Sequence[str], k: int) -> float:
    if k <= 0:
        return 0.0
    return len(set(retrieved[:k]) & set(relevant)) / k


def hit_at_k(retrieved: Sequence[str], relevant: Sequence[str], k: int) -> float:
    return 1.0 if set(retrieved[:k]) & set(relevant) else 0.0


def reciprocal_rank(retrieved: Sequence[str], relevant: Sequence[str]) -> float:
    gold = set(relevant)
    for rank, doc in enumerate(retrieved, start=1):
        if doc in gold:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(retrieved: Sequence[str], relevant: Sequence[str], k: int) -> float:
    gold = set(relevant)
    dcg = sum((1.0 if d in gold else 0.0) / math.log2(i + 1)
              for i, d in enumerate(retrieved[:k], start=1))
    ideal = sum(1.0 / math.log2(i + 1) for i in range(1, min(k, len(gold)) + 1))
    return dcg / ideal if ideal > 0 else 0.0


def evaluate(queries: Sequence[Dict], k: int = 5) -> Dict[str, float]:
    """宏平均：先算每个 query 的指标，再对 query 求平均。"""
    keys = ["recall@%d" % k, "precision@%d" % k, "hit@%d" % k,
            "mrr", "ndcg@%d" % k]
    rows = []
    for q in queries:
        r, g = q["retrieved"], q["relevant"]
        rows.append((q["qid"],
                     recall_at_k(r, g, k), precision_at_k(r, g, k),
                     hit_at_k(r, g, k), reciprocal_rank(r, g),
                     ndcg_at_k(r, g, k)))
    n = len(rows)
    macro = {name: sum(row[i + 1] for row in rows) / n
             for i, name in enumerate(keys)}
    return {"rows": rows, "macro": macro}


QUERIES: List[Dict] = [
    # q1：两条相关文档排在前 3 —— 理想情况
    {"qid": "q1", "relevant": ["d1", "d2"],
     "retrieved": ["d1", "d9", "d2", "d7", "d3", "d8", "d4", "d5", "d6", "d10"]},
    # q2：唯一相关文档排在第 10 —— Recall@10 满分但 MRR 只有 0.1
    {"qid": "q2", "relevant": ["d3"],
     "retrieved": ["d9", "d8", "d7", "d6", "d5", "d4", "d2", "d1", "d10", "d3"]},
    # q3：只召回一半
    {"qid": "q3", "relevant": ["d4", "d5"],
     "retrieved": ["d4", "d11", "d12", "d13", "d14"]},
    # q4：完全没有命中
    {"qid": "q4", "relevant": ["d6"],
     "retrieved": ["d11", "d12", "d13", "d14", "d15"]},
    # q5：三条相关全部命中，但位置有偏（nDCG 反映折损）
    {"qid": "q5", "relevant": ["d1", "d2", "d3"],
     "retrieved": ["d2", "d9", "d8", "d1", "d3"]},
    # q6：命中且排第一
    {"qid": "q6", "relevant": ["d8"],
     "retrieved": ["d8", "d1", "d2", "d3", "d4"]},
]


def main() -> None:
    result = evaluate(QUERIES, k=5)
    print("=== 逐 query 指标（k=5）===")
    header = "%-6s %-10s %-12s %-8s %-8s %-9s" % (
        "qid", "recall@5", "precision@5", "hit@5", "mrr", "ndcg@5")
    print(header)
    print("-" * len(header))
    for qid, rc, pr, ht, mrr, ndcg in result["rows"]:
        print("%-6s %-10.3f %-12.3f %-8.1f %-8.3f %-9.3f"
              % (qid, rc, pr, ht, mrr, ndcg))

    print("\n=== 宏平均 ===")
    for name, value in result["macro"].items():
        print("  %-14s %.4f" % (name, value))

    print("\n=== 为什么要同时看 Recall 与 MRR ===")
    q2 = QUERIES[1]
    print("  q2 的 Recall@10 = %.3f（找全了），MRR = %.3f（排在第 10 位）"
          % (recall_at_k(q2["retrieved"], q2["relevant"], 10),
             reciprocal_rank(q2["retrieved"], q2["relevant"])))
    print("  只看 Recall 会认为检索完美；实际用户要翻到第 10 条才看到答案。")
    print("  q2 的 nDCG@10 = %.3f，同时反映了「命中」与「位置差」。"
          % ndcg_at_k(q2["retrieved"], q2["relevant"], 10))


if __name__ == "__main__":
    main()
```

关键结论：`q2` 的 `Recall@10 = 1.0` 而 `MRR = 0.1`。**任何只报召回率的 RAG 评测都会把这种情况判为「检索完美」**，而真实用户体验是「答案藏在第 10 条」。这就是为什么检索侧至少要报「一个覆盖度指标 + 一个位置指标」。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/05-评测/05-RAG与多轮对话评测.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「示例一：检索侧指标计算器」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/05-评测/05-RAG与多轮对话评测.md)
