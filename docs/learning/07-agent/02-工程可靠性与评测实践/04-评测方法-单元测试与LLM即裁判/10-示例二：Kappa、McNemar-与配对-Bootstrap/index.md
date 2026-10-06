---
article_id: kp-7983d11667b2dafc
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-12ffa80c1618
learning_sourceId: 12ffa80c1618
learning_order: 9
learning_objective: 理解并验证：示例二：Kappa、McNemar 与配对 Bootstrap
---

# 示例二：Kappa、McNemar 与配对 Bootstrap

> **学习目标**：能够解释「示例二：Kappa、McNemar 与配对 Bootstrap」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-为什么Agent评测比LLM评测难](../../../../../07-agent/05-评测/01-为什么Agent评测比LLM评测难.md) 的三层评测与四象限、[02-评测指标设计](../../../../../07-agent/05-评测/02-评测指标设计.md) 的口径固定与 `pass@k` / `pass^k`。
>
> **所属主题**：-评测方法-单元测试与LLM即裁判 · 可运行示例

## 本次只学这一点

```python
"""LLM-as-a-Judge 一致性检验与 A/B 显著性检验。

依赖：仅标准库。精确 McNemar 用 math.comb 实现，不依赖 scipy。
"""

import math
import random
from typing import Dict, Sequence, Tuple


def cohen_kappa(a: Sequence[str], b: Sequence[str]) -> Tuple[float, float, float]:
    """返回 (观察一致率 p_o, 随机一致率 p_e, Cohen's Kappa)。"""
    if len(a) != len(b):
        raise ValueError("两个标注序列长度必须相同")
    n = len(a)
    if n == 0:
        raise ValueError("序列不能为空")

    labels = sorted(set(a) | set(b))
    idx = {lab: i for i, lab in enumerate(labels)}
    size = len(labels)
    matrix = [[0] * size for _ in range(size)]
    for x, y in zip(a, b):
        matrix[idx[x]][idx[y]] += 1

    po = sum(matrix[i][i] for i in range(size)) / n
    row = [sum(matrix[i]) for i in range(size)]                          # a 的边际
    col = [sum(matrix[r][i] for r in range(size)) for i in range(size)]  # b 的边际
    pe = sum(row[i] * col[i] for i in range(size)) / (n * n)
    return po, pe, ((po - pe) / (1.0 - pe) if pe < 1.0 else 0.0)


def mcnemar_exact(b: int, c: int) -> float:
    """精确双侧 McNemar：p = 2 * sum_{i<=min(b,c)} C(b+c,i) * 0.5^(b+c)。"""
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(b, c) + 1)) * (0.5 ** n)
    return min(1.0, 2.0 * tail)


def mcnemar_chi2(b: int, c: int) -> Tuple[float, float]:
    """连续性校正的 McNemar 卡方统计量与 p 值（1 自由度）。"""
    n = b + c
    if n == 0:
        return 0.0, 1.0
    stat = (abs(b - c) - 1) ** 2 / n
    # 1 自由度卡方：p = 2 * (1 - Phi(sqrt(stat))) = erfc(sqrt(stat / 2))
    return stat, min(1.0, math.erfc(math.sqrt(stat / 2.0)))


def bootstrap_ci_paired(a: Sequence[int], b: Sequence[int], n_boot: int = 10000,
                        alpha: float = 0.05, seed: int = 42) -> Dict[str, float]:
    """配对 Bootstrap：以**任务**为单位重采样，返回差值与其 95% CI。"""
    if len(a) != len(b):
        raise ValueError("两组必须跑在同一批任务上（配对）")
    n = len(a)
    point = sum(b) / n - sum(a) / n
    rng = random.Random(seed)
    diffs = []
    for _ in range(n_boot):
        sa = sb = 0
        for _ in range(n):
            i = rng.randrange(n)      # 同一批索引同时取 A 与 B —— 配对的关键
            sa += a[i]
            sb += b[i]
        diffs.append(sb / n - sa / n)
    diffs.sort()
    lo, hi = diffs[int(alpha / 2 * n_boot)], diffs[int((1 - alpha / 2) * n_boot) - 1]
    return {"diff": point, "lo": lo, "hi": hi,
            "significant": 0.0 if lo <= 0.0 <= hi else 1.0}


def main() -> None:
    # 判读标准：κ ≥ 0.6 才可用于正式评测；κ ≈ 0 说明与随机猜测无异。
    print("=== 1) Judge 与人工的一致性 ===")
    po, pe, k = cohen_kappa(["pass"] * 54 + ["fail"] * 6, ["pass"] * 60)
    print("  懒惰 Judge（类别不平衡）: p_o=%.3f  p_e=%.3f  kappa=%.3f" % (po, pe, k))

    human = ["pass", "fail"] * 30
    judge = list(human)
    for i in (1, 5):                 # 2 条人工 fail 被误判为 pass
        judge[i] = "pass"
    for i in (0, 4):                 # 2 条人工 pass 被误判为 fail
        judge[i] = "fail"
    po, pe, k = cohen_kappa(human, judge)
    print("  合格 Judge（类别均衡）  : p_o=%.3f  p_e=%.3f  kappa=%.3f" % (po, pe, k))

    print("\n=== 2) A/B 显著性检验（200 个任务，配对）===")
    a_only, b_only, both_pass, both_fail = 5, 20, 140, 35
    a = [1] * a_only + [0] * b_only + [1] * both_pass + [0] * both_fail
    bb = [0] * a_only + [1] * b_only + [1] * both_pass + [0] * both_fail
    order = list(range(len(a)))      # 打乱任务排列，配对关系不变
    random.Random(7).shuffle(order)
    a, bb = [a[i] for i in order], [bb[i] for i in order]

    n = len(a)
    print("  基线 A 成功率 = %.1f%%   新方案 B 成功率 = %.1f%%"
          % (sum(a) / n * 100, sum(bb) / n * 100))

    b_cnt = sum(1 for x, y in zip(a, bb) if x == 1 and y == 0)
    c_cnt = sum(1 for x, y in zip(a, bb) if x == 0 and y == 1)
    stat, p_chi2 = mcnemar_chi2(b_cnt, c_cnt)
    p_exact = mcnemar_exact(b_cnt, c_cnt)
    print("  A过B挂 b=%d   A挂B过 c=%d   b+c=%d" % (b_cnt, c_cnt, b_cnt + c_cnt))
    print("  McNemar 精确检验 p = %.6f" % p_exact)
    print("  McNemar 卡方(校正) chi2 = %.4f, p = %.6f" % (stat, p_chi2))
    print("  结论（alpha=0.05）：%s"
          % ("差异显著" if p_exact < 0.05 else "差异不显著"))
    if b_cnt + c_cnt < 25:
        print("  注意：b+c < 25，应以精确检验的 p 值为准。")

    ci = bootstrap_ci_paired(a, bb)
    print("\n  配对 Bootstrap（n_boot=10000，按任务重采样）：")
    print("    差值 = %+.4f   95%% CI = [%+.4f, %+.4f]   %s"
          % (ci["diff"], ci["lo"], ci["hi"],
             "CI 不跨 0 → 显著" if ci["significant"] else "CI 跨 0 → 不显著"))


if __name__ == "__main__":
    main()
```

预期结论：懒惰 Judge 准确率 0.900 但 Kappa **0.000**——准确率完全无法反映它没有判别力；合格 Judge 准确率 0.933、Kappa 约 **0.867**。A/B 场景 `b=5`、`c=20`，精确 McNemar `p ≈ 0.0041 < 0.05`，配对 Bootstrap 的 95% CI `[+0.030, +0.125]` 不跨 0，两个检验给出一致结论：新方案显著更好。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/05-评测/03-评测方法-单元测试与LLM即裁判.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「示例二：Kappa、McNemar 与配对 Bootstrap」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/05-评测/03-评测方法-单元测试与LLM即裁判.md)
