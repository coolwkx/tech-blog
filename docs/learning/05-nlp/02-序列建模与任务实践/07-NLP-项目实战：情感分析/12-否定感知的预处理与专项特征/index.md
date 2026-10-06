---
article_id: kp-dd12921390249b22
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-cea0dd524785
learning_sourceId: cea0dd524785
learning_order: 11
learning_objective: 理解并验证：否定感知的预处理与专项特征
---

# 否定感知的预处理与专项特征

> **学习目标**：能够解释「否定感知的预处理与专项特征」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇 TF-IDF、第 05 篇文本分类流水线与评估指标、第 08/09 篇 BERT 微调、第 01 篇的文本数据分析。
>
> **所属主题**：NLP 项目实战：情感分析 · 可运行示例

## 本次只学这一点

```python
import jieba
import re

NEGATIONS = {"不", "没", "没有", "无", "非", "别", "莫", "未", "不要", "不能"}
DEGREE = {"非常": 1.5, "特别": 1.5, "很": 1.3, "太": 1.3,
"比较": 0.8, "有点": 0.6, "稍微": 0.5, "略": 0.5}
CONTRAST = {"但", "但是", "不过", "然而", "可是", "只是", "可惜"}

def negate_join(text: str, window: int = 2) -> str:
    """把否定词与后 window 个词拼接成新 token，让词袋也能感知否定。
    例: '服务 不 好' -> '服务 不_好'
    """
    words = list(jieba.lcut(text))
    out, i = [], 0
    while i < len(words):
        if words[i] in NEGATIONS:
            j = min(i + window, len(words))
            merged = "_".join(words[i:j])
            out.append(merged)
            i = j
        else:
            out.append(words[i])
            i += 1
            return "".join(out)

        def polarity_features(text: str) -> dict:
            """抽出可用于树模型/线性模型的显式情感特征（规则词典原型）"""
            words = list(jieba.lcut(text))
            POS = {"好", "满意", "推荐", "干净", "方便", "舒服", "不错", "热情"}
            NEG = {"差", "脏", "冷漠", "陈旧", "吵", "异味", "不耐烦"}

            score = 0.0
            for k, w in enumerate(words):
                if w in POS:
                    polarity = 1.0
                    # 若前 2 个词内出现否定词，极性翻转
                    if any(p in NEGATIONS for p in words[max(0, k - 2):k]):
                        polarity = -1.0
                        # 若前一个词是程度副词，按权重缩放
                        degree = DEGREE.get(words[k - 1], 1.0) if k > 0 else 1.0
                        score += polarity * degree
                    elif w in NEG:
                        score -= 1.0

                        return {
                    "n_negation": sum(w in NEGATIONS for w in words),
                    "n_contrast": sum(w in CONTRAST for w in words),
                    "degree_sum": sum(DEGREE.get(w, 0.0) for w in words),
                    "rule_score": round(score, 2),
                    "has_contrast": int(any(w in CONTRAST for w in words)),
                    }

                    samples = ["服务 不 好", "房间 非常 干净 ， 但 服务 太 差", "不 推荐 这家 酒店"]
                    for s in samples:
                        print(f"{s!r}\n 否定拼接 -> {negate_join(s)}\n 特征 -> {polarity_features(s)}\n")
```

`negate_join` 的效果可以用对照实验量化：分别用「原始分词」与「否定拼接后」训练同一个模型，比较验证集 macro-F1，就能确定这个改动是否值得保留——**不要凭感觉加特征**。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/11-NLP项目实战-情感分析.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「否定感知的预处理与专项特征」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/11-NLP项目实战-情感分析.md)
