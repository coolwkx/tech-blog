---
article_id: kp-66d84714fbd9e553
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-46f092adbce1
learning_sourceId: 46f092adbce1
learning_order: 10
learning_objective: 理解并验证：示例二：环境不确定性 → pass@k 与 pass^k 的分叉
---

# 示例二：环境不确定性 → pass@k 与 pass^k 的分叉

> **学习目标**：能够解释「示例二：环境不确定性 → pass@k 与 pass^k 的分叉」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的 Observe-Think-Act 循环、[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的工具协议、[07-Agent工程化与可靠性设计](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md) 的轨迹落盘与结构化日志。
>
> **所属主题**：-为什么Agent评测比LLM评测难 · 可运行示例

## 本次只学这一点

用伯努利模型模拟「同一任务跑 k 次」，比较两种口径。这个例子不需要真的跑 Agent，但它解释了为什么必须报分布而不是单点。

```python
"""pass@k 与 pass^k 的对比：从单次成功率 p 推出两个相反趋势的口径。

依赖：仅标准库。
"""

import random


def pass_metrics(p: float, k: int, n_tasks: int = 20000, seed: int = 20240501) -> dict:
    """对 n_tasks 个任务各采样 k 次，同时返回模拟值与解析解。"""
    rng = random.Random(seed)
    runs_matrix = [[rng.random() < p for _ in range(k)] for _ in range(n_tasks)]
    return {
        "pass@k": sum(any(r) for r in runs_matrix) / n_tasks,
        "pass^k": sum(all(r) for r in runs_matrix) / n_tasks,
        "th_pass@k": 1.0 - (1.0 - p) ** k,
        "th_pass^k": p ** k,
    }


def main() -> None:
    p = 0.70
    fmt = "%-4s %-10s %-10s %-11s %-11s"
    print("单次成功率 p = %.2f，每个任务采样 k 次\n" % p)
    print(fmt % ("k", "pass@k", "pass^k", "th_pass@k", "th_pass^k"))
    print("-" * 50)
    for k in (1, 3, 5, 10):
        m = pass_metrics(p, k)
        print(fmt % (k, "%.4f" % m["pass@k"], "%.4f" % m["pass^k"],
                     "%.4f" % m["th_pass@k"], "%.4f" % m["th_pass^k"]))
    print("\n结论：pass@k 随 k 上升，pass^k 随 k 下降；报指标不写 k 就没有意义。")


if __name__ == "__main__":
    main()
```

输出（`p = 0.70`）：

| k | pass@k | pass^k |
| --- | --- | --- |
| 1 | 0.700 | 0.700 |
| 3 | 0.973 | 0.343 |
| 5 | 0.998 | 0.168 |
| 10 | 1.000 | 0.028 |

同一个系统，同一个能力参数，`pass@10 = 100%` 而 `pass^10 = 2.8%`。前者适合「生成 10 个候选让人挑」的场景，后者才是「自动化跑 10 次都不出错」的概率。**这两个数字来自同一个模型，却指向完全相反的上线结论。**

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/05-评测/01-为什么Agent评测比LLM评测难.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「示例二：环境不确定性 → pass@k 与 pass^k 的分叉」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/05-评测/01-为什么Agent评测比LLM评测难.md)
