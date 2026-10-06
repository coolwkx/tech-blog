---
article_id: kp-87fd411801ba122a
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-6495f5dc2b1b
learning_sourceId: 6495f5dc2b1b
learning_order: 8
learning_objective: 理解并验证：用 nltk 计算 BLEU（含累计 BLEU）
---

# 用 nltk 计算 BLEU（含累计 BLEU）

> **学习目标**：能够解释「用 nltk 计算 BLEU（含累计 BLEU）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：概率论中的链式法则与条件概率、softmax、交叉熵、Python 基础（列表/字典/循环）。
>
> **所属主题**：-大模型基础与演进 · 可运行示例

## 本次只学这一点

```python
# 依赖：pip install nltk
from nltk.translate.bleu_score import sentence_bleu, cumulative_bleu

reference = [["today", "is", "a", "nice", "day"]] # 参考译文（列表的列表）
candidate = ["it", "is", "a", "nice", "day", "today"] # 候选译文

# 单阶 BLEU：nltk 的 weights 需要 4 元组，对应 1~4-gram 权重
bleu_1 = sentence_bleu(reference, candidate, weights=(1, 0, 0, 0))
bleu_2 = sentence_bleu(reference, candidate, weights=(0.5, 0.5, 0, 0))
bleu_3 = sentence_bleu(reference, candidate, weights=(0.33, 0.33, 0.33, 0))

# 累计 BLEU：对 1~4-gram 取几何平均并施加简短惩罚
c_bleu = cumulative_bleu(reference, candidate, weights=(0.25, 0.25, 0.25, 0.25))

print("BLEU-1:", round(bleu_1, 4))
print("BLEU-2:", round(bleu_2, 4))
print("BLEU-3:", round(bleu_3, 4))
print("cumulative BLEU:", round(c_bleu, 4))
```

> 注意函数名是 `cumulative_bleu`（语料里 OCR 成了 `cumulative_blue`）。另外 `sentence_bleu` 要求
> 参考译文是「列表的列表」，直接传 `[ref_sentence]` 会报维度错误。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/01-大模型基础与演进.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「用 nltk 计算 BLEU（含累计 BLEU）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/01-大模型基础与演进.md)
