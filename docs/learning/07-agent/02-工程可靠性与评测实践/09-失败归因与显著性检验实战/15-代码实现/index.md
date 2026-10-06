---
article_id: kp-31cee7bd2ab6f62b
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-8fca08e90f95
learning_sourceId: 8fca08e90f95
learning_order: 14
learning_objective: 理解并验证：代码实现
---

# 代码实现

> **学习目标**：能够解释「代码实现」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的评测器判定顺序与证据信任链、[02 篇](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md) 的 `taskId + repeatId + seed` 配对主键、二项分布与 Bootstrap 重采样的基础。
>
> **所属主题**：-失败归因与显著性检验实战 · McNemar exact test

## 本次只学这一点

```python
"""McNemar exact test：小样本走精确组合数，大样本切对数空间防溢出。"""
from __future__ import annotations

import math


def mcnemar_exact_p(fail_to_pass: int, pass_to_fail: int) -> float:
    """双侧 exact p-value：2 * P(X <= min(b, c)), X ~ Binomial(b + c, 0.5)。"""
    if not isinstance(fail_to_pass, int) or not isinstance(pass_to_fail, int):
        raise TypeError("McNemar 计数必须是整数")
    if fail_to_pass < 0 or pass_to_fail < 0:
        raise ValueError("McNemar 计数必须非负")

    discordant, lower = fail_to_pass + pass_to_fail, min(fail_to_pass, pass_to_fail)
    if discordant == 0:
        return 1.0
    if discordant <= 1024:
        # Python 整数是任意精度，组合数不溢出；但 2**n 转 float 在 n≈1024 以上溢出
        tail = sum(math.comb(discordant, k) for k in range(lower + 1)) / float(2 ** discordant)
        return min(1.0, 2.0 * tail)

    # 大样本路径：算最大项的对数，再按相邻项比值累加
    log_largest = (math.lgamma(discordant + 1) - math.lgamma(lower + 1)
                   - math.lgamma(discordant - lower + 1) - discordant * math.log(2.0))
    scaled = ratio = 1.0
    for k in range(lower, 0, -1):
        ratio *= k / (discordant - k + 1)     # term(k-1) / term(k)
        scaled += ratio
        if ratio == 0.0:                      # 相对项已下溢，后续可忽略
            break
    return min(1.0, 2.0 * math.exp(log_largest) * scaled)
```

两条路径必须一致。用 `n=19, lower=5` 交叉验证：

```text
mcnemar_exact_p(14, 5)                              = 0.063568
大样本对数空间路径(n=19, lower=5)                     = 0.063568   ← 逐位一致
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「代码实现」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md)
