---
article_id: kp-08dcb8d1b788b0c4
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-272ce9acf0c8
learning_sourceId: 272ce9acf0c8
learning_order: 22
learning_objective: 理解并验证：一份可直接跑的清洗脚本骨架
---

# 一份可直接跑的清洗脚本骨架

> **学习目标**：能够解释「一份可直接跑的清洗脚本骨架」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT/MLM 预训练目标、Tokenizer 与词表（vocab）、`[MASK]` token 与 MLM Head、交叉熵损失、基本的分类任务指标（acc / P / R / F1）。
>
> **所属主题**：-指令数据构造与清洗 · 数据清洗清单

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""指令/完形填空数据清洗骨架。依赖：标准库"""
import hashlib
import re
import unicodedata
from collections import Counter


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text)).strip()


def fingerprint(text: str) -> str:
    return hashlib.md5(normalize(text).encode("utf8")).hexdigest()


def token_len(text: str, tokenizer=None) -> int:
    """优先用真实 tokenizer 数 token；没有时用字符数近似（中文误差可接受）。"""
    return len(text) if tokenizer is None else len(tokenizer(text)["input_ids"]) - 2


def clean(records, tokenizer=None, min_len=3, max_len=1024,
          banned_patterns=None, require_fields=("instruction", "output")):
    """records: List[dict]。返回 (清洗后数据, 统计报告)。"""
    banned_patterns = banned_patterns or [r"\{text[AB]\}", r"\{MASK\}", r"<\|.*?\|>"]
    seen, kept, report = set(), [], Counter()

    for r in records:
        if any(not str(r.get(f, "")).strip() for f in require_fields):
            report["缺字段"] += 1
            continue
        text = normalize(" ".join(str(r.get(f, "")) for f in require_fields))
        n = token_len(text, tokenizer)
        if n < min_len:
            report["过短"] += 1
            continue
        if n > max_len:
            report["过长"] += 1
            continue
        if any(re.search(p, text) for p in banned_patterns):
            report["含模板残留"] += 1
            continue
        fp = fingerprint(text)
        if fp in seen:
            report["精确重复"] += 1
            continue
        seen.add(fp)
        kept.append(r)
    report["保留"] = len(kept)
    return kept, dict(report)


def semantic_dedup(texts, embed_fn, threshold: float = 0.95):
    """基于向量相似度的贪心去重（阈值经验见 5.2）。embed_fn: List[str] -> List[List[float]]"""
    import numpy as np
    vecs = np.asarray(embed_fn(texts), dtype="float32")
    vecs /= (np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-9)
    kept = []
    for i, v in enumerate(vecs):
        if not kept or float((vecs[kept] @ v).max()) < threshold:
            kept.append(i)
    return [texts[i] for i in kept]


def validate_dialogue(msgs) -> list:
    """多轮对话的角色与字段校验，返回问题列表（空列表表示通过）。"""
    if not msgs:
        return ["空对话"]
    problems, expect = [], "user"
    for i, m in enumerate(msgs):
        if m.get("role") != expect:
            problems.append(f"第 {i} 轮角色应为 {expect}，实际 {m.get('role')}")
        if not str(m.get("content", "")).strip():
            problems.append(f"第 {i} 轮内容为空")
        expect = "assistant" if expect == "user" else "user"
    if msgs[-1].get("role") != "assistant":
        problems.append("对话未以 assistant 结束，无法构造监督信号")
    return problems


def find_template_leak(train_texts, eval_texts, literal_parts, min_len: int = 4):
    """检查训练集与评测集是否共享模板字面量片段（literal_parts 已去掉插槽）。"""
    return [p for p in literal_parts if len(p) >= min_len
            and any(p in t for t in train_texts) and any(p in t for t in eval_texts)]
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/06-指令数据构造与清洗.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「一份可直接跑的清洗脚本骨架」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/06-指令数据构造与清洗.md)
