---
article_id: kp-7d160f4099f46dd5
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-6495f5dc2b1b
learning_sourceId: 6495f5dc2b1b
learning_order: 9
learning_objective: 理解并验证：手算 PPL，理解公式
---

# 手算 PPL，理解公式

> **学习目标**：能够解释「手算 PPL，理解公式」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：概率论中的链式法则与条件概率、softmax、交叉熵、Python 基础（列表/字典/循环）。
>
> **所属主题**：-大模型基础与演进 · 可运行示例

## 本次只学这一点

```python
# 依赖：仅标准库
import math

# 一个极简 unigram 概率表（模拟语料统计结果，共 12 个词次）
unigram = {
"I": 1/12, "have": 1/12, "a": 3/12, "pen": 1/12,
"He": 1/12, "has": 1/12, "book": 1/12,
"She": 1/12, "cat": 1/12,
}

sentences = [
["I", "have", "a", "pen"],
["He", "has", "a", "book"],
["She", "has", "a", "cat"],
]

total_log_prob, total_tokens = 0.0, 0
for sentence in sentences:
    for word in sentence:
        total_log_prob += math.log(unigram[word]) # 累加对数概率
        total_tokens += 1

        # PPL = exp(-1/N * sum(log p))
        perplexity = math.exp(-total_log_prob / total_tokens)
        print("困惑度 PPL =", round(perplexity, 4))
```

要点：**先取对数再平均再取指数**，避免多词概率连乘下溢为 0；这也说明为什么训练时用
cross-entropy loss 与用 PPL 做评估是同一件事。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/01-大模型基础与演进.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「手算 PPL，理解公式」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/01-大模型基础与演进.md)
