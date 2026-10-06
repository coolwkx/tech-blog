---
article_id: kp-7c1a0504f3e25b66
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-ab1dbc27d73f
learning_sourceId: ab1dbc27d73f
learning_order: 13
learning_objective: 理解并验证：用 Cross-Encoder 做精排
---

# 用 Cross-Encoder 做精排

> **学习目标**：能够解释「用 Cross-Encoder 做精排」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇的 TF-IDF 与余弦相似度、第 04 篇的词向量、第 08 篇的 attention、第 09 篇的 BERT 与句对任务。
>
> **所属主题**：文本相似度与语义匹配 · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install transformers torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2" # 换中文可用 BAAI/bge-reranker-base
tok = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL).eval

query = "如何治疗感冒"
candidates = ["感冒了应该怎么办", "感冒药怎么吃", "今天天气怎么样"]

# 关键：query 与每个候选拼成一个序列一起送入，这就是「交互式」
pairs = [[query, c] for c in candidates]
inputs = tok(pairs, padding=True, truncation=True, max_length=256, return_tensors="pt")

with torch.no_grad:
 scores = model(**inputs).logits.view(-1).float

for c, s in sorted(zip(candidates, scores.tolist()), key=lambda x: -x[1]):
 print(f"{s:+.4f} {c}")
```

对比 3.2 与 3.3 的写法，能直观看出两种路线的工程差异：**3.2 的候选向量可离线算好、重复使用；3.3 每换一个 query 都必须把全部候选对重新前向一次**。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/10-文本相似度与语义匹配.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「用 Cross-Encoder 做精排」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/10-文本相似度与语义匹配.md)
