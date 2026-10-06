---
article_id: kp-2e5537323e7132e0
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-8fca08e90f95
learning_sourceId: 8fca08e90f95
learning_order: 19
learning_objective: 理解并验证：代码实现
---

# 代码实现

> **学习目标**：能够解释「代码实现」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的评测器判定顺序与证据信任链、[02 篇](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md) 的 `taskId + repeatId + seed` 配对主键、二项分布与 Bootstrap 重采样的基础。
>
> **所属主题**：-失败归因与显著性检验实战 · 聚类 Bootstrap CI：重采样单位必须是 taskId

## 本次只学这一点

```python
"""以 taskId 为聚类单位的百分位 Bootstrap，以及用于对照的 i.i.d. 版本。"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class Pair:
    task_id: str
    repeat_id: str
    seed: int
    baseline_passed: bool
    optimized_passed: bool

    @property
    def pair_key(self) -> str:
        return f"{self.task_id}::{self.repeat_id}::{self.seed}"


def percentile(sorted_values: Sequence[float], probability: float) -> float:
    """与 agent-eval-lab 一致的百分位口径：floor(p * n)，夹在 [0, n-1]。"""
    return sorted_values[min(len(sorted_values) - 1, max(0, int(probability * len(sorted_values))))]


def bootstrap_delta(pairs: Sequence[Pair], cluster_by_task: bool = True,
                    iterations: int = 2000, confidence_level: float = 0.95,
                    seed: int = 20260819) -> dict[str, float]:
    """cluster_by_task=True 是正确做法；False 是错误做法（i.i.d.，仅作对照）。

    正确做法三步：①按 taskId 折叠成任务簇，簇内保留全部计数；
    ②有放回抽「任务」（抽够原任务数），整簇进出；③每次重采样内先池化再作差。
    """
    if iterations < 100:
        raise ValueError("iterations 必须 >= 100")
    if not 0.0 < confidence_level < 1.0:
        raise ValueError("confidence_level 必须落在 (0, 1)")

    units: dict[str, list[int]] = {}                   # [baseline 通过数, optimized 通过数, 配对数]
    for pair in pairs:
        key = pair.task_id if cluster_by_task else pair.pair_key
        unit = units.setdefault(key, [0, 0, 0])
        unit[0] += int(pair.baseline_passed)
        unit[1] += int(pair.optimized_passed)
        unit[2] += 1
    keys = sorted(units)
    rng = random.Random(seed)

    deltas: list[float] = []
    for _ in range(iterations):
        baseline_pass = optimized_pass = drawn = 0
        for _ in range(len(keys)):                     # 重采样样本量 = 原单元数
            unit = units[keys[rng.randrange(len(keys))]]
            baseline_pass += unit[0]                    # 整簇进出，不拆分
            optimized_pass += unit[1]
            drawn += unit[2]
        deltas.append(optimized_pass / drawn - baseline_pass / drawn)   # 先池化再作差
    deltas.sort()

    alpha = (1.0 - confidence_level) / 2.0
    passed_baseline = sum(1 for pair in pairs if pair.baseline_passed)
    passed_optimized = sum(1 for pair in pairs if pair.optimized_passed)
    return {"estimate": passed_optimized / len(pairs) - passed_baseline / len(pairs),
            "lower": percentile(deltas, alpha), "upper": percentile(deltas, 1.0 - alpha),
            "unit": "task" if cluster_by_task else "pair", "clusters": len(keys)}
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「代码实现」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md)
