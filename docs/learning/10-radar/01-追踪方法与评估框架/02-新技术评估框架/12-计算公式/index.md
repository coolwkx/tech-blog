---
article_id: kp-afb324d427639b06
learning_kind: article
learning_category: 10-radar
learning_direction: foundations
learning_topic: topic-0c9434d9f8fb
learning_sourceId: 0c9434d9f8fb
learning_order: 11
learning_objective: 理解并验证：计算公式
---

# 计算公式

> **学习目标**：能够解释「计算公式」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：先了解本主题的基本术语；示例环境与背景见综合原文。
>
> **所属主题**：新技术评估框架 · 综合计算与定级

## 本次只学这一点

```text
总分 = D1×0.25 + D2×0.25 + D3×0.20 + D4×0.20 + D5×0.10
```

总分落在 1.00–5.00 之间。用可运行代码实现一遍，保证每次算出的分一致：

```python
"""五维加权评分：给定五个维度的分数，输出总分与关注等级。"""

WEIGHTS = {
    "mechanism": 0.25,   # D1 技术机制
    "capability": 0.25,  # D2 能力变化
    "maturity": 0.20,    # D3 成熟度
    "usability": 0.20,   # D4 工程可用性
    "impact": 0.10,      # D5 对我们的影响
}

LEVELS = [
    (4.20, "A 立即跟进"),
    (3.40, "B 排期试点"),
    (2.60, "C 持续观察"),
    (0.00, "D 暂不投入"),
]


def score(scores: dict) -> tuple:
    """scores 的键必须与 WEIGHTS 一致，值为 1-5 的整数。"""
    missing = set(WEIGHTS) - set(scores)
    if missing:
        raise ValueError(f"缺少维度: {sorted(missing)}")
    for name in WEIGHTS:
        if not 1 <= scores[name] <= 5:
            raise ValueError(f"{name} 超出 1-5 范围: {scores[name]}")

    total = sum(scores[name] * weight for name, weight in WEIGHTS.items())
    total = round(total, 2)

    level = LEVELS[-1][1]
    for threshold, name in LEVELS:
        if total >= threshold:
            level = name
            break
    return total, level


if __name__ == "__main__":
    print(score({"mechanism": 5, "capability": 5, "maturity": 3,
                 "usability": 4, "impact": 5}))
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../10-radar/01-追踪方法/02-新技术评估框架.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「计算公式」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../10-radar/01-追踪方法/02-新技术评估框架.md)
