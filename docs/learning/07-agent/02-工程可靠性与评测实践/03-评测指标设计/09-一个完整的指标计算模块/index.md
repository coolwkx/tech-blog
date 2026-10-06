---
article_id: kp-08cae54efb9d48b0
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-c9b612267f80
learning_sourceId: c9b612267f80
learning_order: 8
learning_objective: 理解并验证：一个完整的指标计算模块
---

# 一个完整的指标计算模块

> **学习目标**：能够解释「一个完整的指标计算模块」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-为什么Agent评测比LLM评测难](../../../../../07-agent/05-评测/01-为什么Agent评测比LLM评测难.md) 的结果层 / 过程层 / 系统层三分法与四象限判定。
>
> **所属主题**：-评测指标设计 · 可运行示例

## 本次只学这一点

```python
"""Agent 评测指标计算模块：结果层 / 过程层 / 系统层 / 安全层。

依赖：仅标准库。
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Sequence

PRICE_IN_PER_1K = 0.003      # 输入 token 单价（美元 / 1K）
PRICE_OUT_PER_1K = 0.015     # 输出 token 单价（美元 / 1K）
PRICE_PER_TOOL_CALL = 0.0002  # 每次工具调用的固定成本


@dataclass
class StepRecord:
    """轨迹中的一步。"""
    tool: str
    ok: bool
    tokens_in: int = 0
    tokens_out: int = 0
    seconds: float = 0.0


@dataclass
class RunRecord:
    """一次任务运行的完整记录。"""
    task_id: str
    category: str
    difficulty: str                       # easy / medium / hard
    success: bool
    steps: List[StepRecord]
    expected_tools: Sequence[str]
    optimal_steps: int
    subtask_weights: Sequence[float] = field(default_factory=tuple)
    subtask_done: Sequence[bool] = field(default_factory=tuple)
    violation: bool = False               # 是否发生过越权
    injection_attempts: int = 0
    injection_blocked: int = 0

    @property
    def tokens_in(self) -> int:
        return sum(s.tokens_in for s in self.steps)

    @property
    def tokens_out(self) -> int:
        return sum(s.tokens_out for s in self.steps)

    @property
    def seconds(self) -> float:
        return sum(s.seconds for s in self.steps)

    @property
    def cost(self) -> float:
        return (self.tokens_in / 1000.0 * PRICE_IN_PER_1K
                + self.tokens_out / 1000.0 * PRICE_OUT_PER_1K
                + len(self.steps) * PRICE_PER_TOOL_CALL)

    @property
    def used_tools(self) -> List[str]:
        return [s.tool for s in self.steps]

    @property
    def invalid_steps(self) -> int:
        failed = sum(1 for s in self.steps if not s.ok)
        redundant = max(0, len(self.steps) - self.optimal_steps)
        return failed + redundant


def percentile(values: Sequence[float], q: float) -> float:
    """线性插值分位数，q 取 0-100。"""
    if not values:
        raise ValueError("values 不能为空")
    if not 0.0 <= q <= 100.0:
        raise ValueError("q 必须在 [0, 100] 内")
    xs = sorted(values)
    if len(xs) == 1:
        return float(xs[0])
    pos = (len(xs) - 1) * q / 100.0
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(xs) - 1)
    frac = pos - lo
    return float(xs[lo] + (xs[hi] - xs[lo]) * frac)


@dataclass
class Metrics:
    n_tasks: int = 0
    success_rate: float = 0.0
    partial_rate: float = 0.0
    weighted_partial: float = 0.0
    tool_precision: float = 0.0
    tool_recall: float = 0.0
    tool_f1: float = 0.0
    invalid_step_ratio: float = 0.0
    recovery_rate: float = 0.0
    mean_seconds: float = 0.0
    p50_seconds: float = 0.0
    p95_seconds: float = 0.0
    mean_tokens: float = 0.0
    cost_per_task: float = 0.0
    cost_per_success: float = 0.0
    violation_rate: float = 0.0
    injection_block_rate: float = 0.0

    def as_rows(self) -> List[tuple]:
        return [
            ("结果", "任务成功率", "%.1f%%" % (self.success_rate * 100)),
            ("过程", "工具精确率", "%.3f" % self.tool_precision),
            ("过程", "工具召回率", "%.3f" % self.tool_recall),
            ("过程", "工具 F1", "%.3f" % self.tool_f1),
            ("过程", "无效步占比", "%.1f%%" % (self.invalid_step_ratio * 100)),
            ("过程", "错误恢复率", "%.1f%%" % (self.recovery_rate * 100)),
            ("系统", "平均耗时", "%.2fs" % self.mean_seconds),
            ("系统", "P50 耗时", "%.2fs" % self.p50_seconds),
            ("系统", "P95 耗时", "%.2fs" % self.p95_seconds),
            ("系统", "单任务成本", "$%.4f" % self.cost_per_task),
            ("系统", "每次成功成本", "$%.4f" % self.cost_per_success),
            ("安全", "越权率", "%.1f%%" % (self.violation_rate * 100)),
            ("安全", "注入拦截率", "%.1f%%" % (self.injection_block_rate * 100)),
        ]


def compute(records: Sequence[RunRecord]) -> Metrics:
    """计算全部指标。所有口径写死在函数体内，避免跨报告漂移。"""
    if not records:
        raise ValueError("records 不能为空")
    n = len(records)
    m = Metrics(n_tasks=n)

    # ---------- 结果层 ----------
    m.success_rate = sum(1 for r in records if r.success) / n

    partials = []
    for r in records:
        if r.subtask_done:
            partials.append(sum(r.subtask_done) / len(r.subtask_done))
    m.partial_rate = sum(partials) / n if partials else m.success_rate

    weighted = []
    for r in records:
        if r.subtask_done and r.subtask_weights:
            total_w = sum(r.subtask_weights)
            if total_w > 0:
                weighted.append(sum(w for w, d in zip(r.subtask_weights, r.subtask_done)
                                    if d) / total_w)
    m.weighted_partial = sum(weighted) / n if weighted else m.partial_rate

    # ---------- 过程层 ----------
    hit = used_total = expected_total = 0
    for r in records:
        used = set(r.used_tools)
        exp = set(r.expected_tools)
        hit += len(used & exp)
        used_total += len(used)
        expected_total += len(exp)
    p = hit / used_total if used_total else 0.0
    rc = hit / expected_total if expected_total else 0.0
    m.tool_precision, m.tool_recall = p, rc
    m.tool_f1 = (2 * p * rc / (p + rc)) if (p + rc) > 0 else 0.0

    total_invalid = sum(r.invalid_steps for r in records)
    total_steps = sum(len(r.steps) for r in records)
    m.invalid_step_ratio = total_invalid / total_steps if total_steps else 0.0

    fail = recovered = 0
    for r in records:
        for i, s in enumerate(r.steps):
            if not s.ok:
                fail += 1
                if i + 1 < len(r.steps) and r.steps[i + 1].ok:
                    recovered += 1
    m.recovery_rate = recovered / fail if fail else 1.0

    # ---------- 系统层 ----------
    secs = [r.seconds for r in records]
    m.mean_seconds = sum(secs) / n
    m.p50_seconds = percentile(secs, 50)
    m.p95_seconds = percentile(secs, 95)
    m.mean_tokens = sum(r.tokens_in + r.tokens_out for r in records) / n
    total_cost = sum(r.cost for r in records)
    m.cost_per_task = total_cost / n
    n_success = sum(1 for r in records if r.success)
    m.cost_per_success = total_cost / n_success if n_success else float("inf")

    # ---------- 安全层 ----------
    m.violation_rate = sum(1 for r in records if r.violation) / n
    attempts = sum(r.injection_attempts for r in records)
    blocked = sum(r.injection_blocked for r in records)
    m.injection_block_rate = blocked / attempts if attempts else 1.0

    return m


# ------------------------------------------------------------------ 合成数据
def _s(tool, sec, tin, tout, ok=True):
    return StepRecord(tool, ok, tin, tout, sec)


CFG = ["read_config", "write_config", "verify_config"]
W_CFG = [0.2, 0.5, 0.3]


def build_records() -> List[RunRecord]:
    """12 个任务：故意包含「召回满分但乱调工具」与「越权 + 长尾延迟」。"""
    records = []
    for i in range(8):                                    # 8 个干净解
        records.append(RunRecord(
            "clean-%02d" % i, "config", "easy", True,
            [_s("read_config", 0.4, 400, 100), _s("write_config", 1.2, 900, 200),
             _s("verify_config", 0.6, 700, 150)],
            CFG, 3, W_CFG, [True, True, True]))
    for i in range(2):                                    # 2 个半成品
        records.append(RunRecord(
            "partial-%02d" % i, "config", "medium", False,
            [_s("read_config", 0.4, 400, 100),
             _s("write_config", 1.0, 900, 200, False),
             _s("write_config", 1.1, 900, 200)],
            CFG, 3, W_CFG, [True, True, False]))
    records.append(RunRecord(                             # 乱调工具：召回 1.0
        "spam-tools", "search", "hard", False,
        [_s("search", 1.5, 800, 300), _s("search", 1.5, 800, 300),
         _s("search", 1.5, 800, 300), _s("fetch_doc", 2.5, 1200, 500),
         _s("search", 1.5, 800, 300)],
        ["search", "fetch_doc"], 2, [0.5, 0.5], [True, False],
        injection_attempts=1, injection_blocked=1))
    records.append(RunRecord(                             # 越权 + 长尾重试
        "risky-long", "ops", "hard", True,
        [_s("run_shell", 0.3, 500, 200),
         _s("verify_config", 0.6, 700, 150, False),
         _s("verify_config", 0.6, 700, 150, False),
         _s("verify_config", 85.0, 700, 150)],
        ["write_config", "verify_config"], 2, [0.6, 0.4], [True, True],
        violation=True, injection_attempts=1, injection_blocked=0))
    return records


def main() -> None:
    records = build_records()
    m = compute(records)

    print("=== 指标总体报告（n=%d） ===" % m.n_tasks)
    print("%-6s %-18s %-12s" % ("层", "指标", "值"))
    print("-" * 40)
    for layer, name, value in m.as_rows():
        print("%-6s %-18s %-12s" % (layer, name, value))

    # 难度分层
    print("\n=== 难度分层成功率 ===")
    for level in ("easy", "medium", "hard"):
        subset = [r for r in records if r.difficulty == level]
        if subset:
            rate = sum(1 for r in subset if r.success) / len(subset)
            print("  %-8s n=%-3d 成功率=%.1f%%" % (level, len(subset), rate * 100))

    # 陷阱演示：精确率的分母是「去重工具集」还是「调用次数」
    print("\n=== 陷阱演示：精确率的分母决定结论 ===")
    fmt = "%-14s %-8s %-8s %-10s %-13s %-13s"
    print(fmt % ("task", "calls", "uniq", "expected", "prec(dedup)",
                 "prec(per-call)"))
    print("-" * 70)
    for r in records:
        if r.task_id in ("spam-tools", "risky-long", "clean-00"):
            calls = len(r.used_tools)
            uniq = set(r.used_tools)
            exp = set(r.expected_tools)
            dedup = len(uniq & exp) / len(uniq) if uniq else 0.0
            per_call = len(uniq & exp) / calls if calls else 0.0
            print(fmt % (r.task_id, calls, len(uniq), len(exp),
                         "%.3f" % dedup, "%.3f" % per_call))
    print("\n  spam-tools 把同一个 search 调了 4 次：")
    print("  去重口径的精确率 = 1.000（完全看不见浪费），")
    print("  按调用次数口径的精确率 = 0.400，无效步数也会同步上升。")
    print("  → 指标定义必须写明分母，否则同一个名字会给出两个结论。")


if __name__ == "__main__":
    main()
```

运行后的读数要点：

1. **总体成功率不高，但每次成功成本被算了出来**——`cost_per_success = 总成本 / 成功任务数`，分母只数成功任务，失败任务的开销被摊进分子，所以这个数字永远大于等于单任务成本。
2. **P95 远高于均值**：`risky-long` 里有一步耗时 85 秒（重试三次才成功），均值会被 11 个正常任务稀释，但 P95 会把它暴露出来。
3. **`spam-tools` 演示了「分母口径」这个坑**：它的工具召回率是 1.000（`search` 与 `fetch_doc` 都出现过）。若精确率按**去重后的工具集合**算，它也拿到 1.000——重复调用完全不可见；只有把分母换成**调用次数**，精确率才降到 0.400。同一份轨迹、同一个指标名、两个相反结论，差别只在分母定义。这就是为什么指标定义必须把口径写死，也为什么精确率要搭配无效步数一起看。
4. **安全指标独立于结果指标**：`risky-long` 最终成功了，结果层给它满分，但 `violation_rate` 捕捉到了越权，`injection_block_rate` 捕捉到了未拦截的注入——这两个数字在只看成功率时完全不可见。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/05-评测/02-评测指标设计.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「一个完整的指标计算模块」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/05-评测/02-评测指标设计.md)
