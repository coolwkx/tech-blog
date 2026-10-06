---
article_id: kp-80730c435aadd2a5
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-ef5c723af69b
learning_sourceId: ef5c723af69b
learning_order: 8
learning_objective: 理解并验证：自建评测集健全性检查 + 分数可比性诊断
---

# 自建评测集健全性检查 + 分数可比性诊断

> **学习目标**：能够解释「自建评测集健全性检查 + 分数可比性诊断」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-为什么Agent评测比LLM评测难](../../../../../07-agent/05-评测/01-为什么Agent评测比LLM评测难.md) 的环境契约、[03-评测方法-单元测试与LLM即裁判](../../../../../07-agent/05-评测/03-评测方法-单元测试与LLM即裁判.md) 的判题分层与显著性检验。
>
> **所属主题**：-评测基准全景 · 可运行示例

## 本次只学这一点

```python
"""评测集健全性检查 + 分数可比性诊断。

依赖：仅标准库。
"""

import random
from collections import Counter

MIN_PER_CATEGORY = 30          # 每类任务数下限
MAX_DIFFICULTY_SHARE = 0.6     # 单一难度占比上限
BUDGET_USD = 50.0              # 整套评测的成本预算
BUDGET_SECONDS = 3600.0        # 整套评测的时长预算
ASSUMED_SUCCESS_RATE = 0.62    # 用于估算「每次成功成本」
DECLARED_SNAPSHOT = "snap-2024-05"
DECLARED_TOOLS = "default"


def build_tasks() -> list:
    """构造 120 条任务元数据，故意包含失衡与环境契约不一致。"""
    rng = random.Random(11)
    plan = [("config", 50), ("search", 18), ("ops", 14), ("safety", 38)]
    difficulties = ["easy"] * 78 + ["medium"] * 30 + ["hard"] * 12
    rng.shuffle(difficulties)

    tasks, i = [], 0
    for category, n in plan:
        for _ in range(n):
            tasks.append({
                "task_id": "t-%03d" % i,
                "category": category,
                "difficulty": difficulties[i],
                # 每 15 条留 1 条缺终态断言（需人工或 Judge 判分）
                "has_terminal_assert": i % 15 != 0,
                # 少量任务用了旧快照 / 扩展工具集 —— 契约不一致的元凶
                "env_snapshot_id": "snap-2024-03" if i % 15 == 3 else DECLARED_SNAPSHOT,
                "tools_profile": "extended" if i % 20 == 7 else DECLARED_TOOLS,
                "timeout_s": 120,
                "estimated_cost_usd": round(rng.uniform(0.01, 0.09), 4),
                "estimated_seconds": round(rng.uniform(5, 60), 1),
            })
            i += 1
    return tasks


def check_dataset(tasks: list) -> None:
    total = len(tasks)

    print("=== 1) 分层抽样是否达标（每类 >= %d）===" % MIN_PER_CATEGORY)
    for cat, n in sorted(Counter(t["category"] for t in tasks).items()):
        print("  %-8s n=%-4d %s" % (cat, n, "OK" if n >= MIN_PER_CATEGORY
                                    else "不足，结论不稳"))

    print("\n=== 2) 难度分布是否失衡（单一难度 <= %.0f%%）==="
          % (MAX_DIFFICULTY_SHARE * 100))
    for d in ("easy", "medium", "hard"):
        n = sum(1 for t in tasks if t["difficulty"] == d)
        share = n / total
        flag = "  ← 超过阈值，总体成功率会被该层主导" if share > MAX_DIFFICULTY_SHARE else ""
        print("  %-7s n=%-4d 占比 %5.1f%%%s" % (d, n, share * 100, flag))

    print("\n=== 3) 是否有无法自动判定的任务 ===")
    missing = [t["task_id"] for t in tasks if not t["has_terminal_assert"]]
    print("  缺终态断言 %d 条（%.1f%%）：%s%s"
          % (len(missing), len(missing) / total * 100, missing[:5],
             " ..." if len(missing) > 5 else ""))

    print("\n=== 4) 环境契约是否一致（不一致则分数不可比较）===")
    for key in ("env_snapshot_id", "tools_profile", "timeout_s"):
        counts = Counter(t[key] for t in tasks)
        flag = "OK" if len(counts) == 1 else "不一致 → 分数不可直接比较"
        print("  %-16s %-34s %s" % (key, dict(counts), flag))

    print("\n=== 5) 成本与时长预算 ===")
    cost = sum(t["estimated_cost_usd"] for t in tasks)
    secs = sum(t["estimated_seconds"] for t in tasks)
    print("  预计总成本 $%.2f（预算 $%.2f）  %s"
          % (cost, BUDGET_USD, "OK" if cost <= BUDGET_USD else "超预算，需缩减规模"))
    print("  预计总时长 %.0fs ≈ %.1f min（预算 %.0fs）  %s"
          % (secs, secs / 60, BUDGET_SECONDS,
             "OK" if secs <= BUDGET_SECONDS else "超时长，需并发或减规模"))
    print("  每次成功成本期望 ≈ $%.4f（按成功率 %.0f%% 估算）"
          % (cost / (total * ASSUMED_SUCCESS_RATE), ASSUMED_SUCCESS_RATE * 100))


def diagnose_comparability(run_a: dict, run_b: dict, tasks: list) -> None:
    """两轮历史评测的可比性诊断。"""
    by_id = {t["task_id"]: t for t in tasks}

    print("\n=== 6) 两轮评测的可比性诊断 ===")
    for run in (run_a, run_b):
        bad = [tid for tid in run["ran"]
               if by_id[tid]["env_snapshot_id"] != run["env_snapshot_id"]
               or by_id[tid]["tools_profile"] != run["tools_profile"]]
        print("  %s 声明 %s / %s：跑了 %d 条，其中 %d 条契约与声明不符"
              % (run["date"], run["env_snapshot_id"], run["tools_profile"],
                 len(run["ran"]), len(bad)))

    same = (run_a["env_snapshot_id"] == run_b["env_snapshot_id"]
            and run_a["tools_profile"] == run_b["tools_profile"])
    print("  两轮声明契约%s → %s"
          % ("相同" if same else "不同",
             "分数可以直接比较" if same else "分数不可直接比较"))

    common = sorted(set(run_a["ran"]) & set(run_b["ran"]))
    usable = [tid for tid in common
              if by_id[tid]["env_snapshot_id"] == run_a["env_snapshot_id"]
              and by_id[tid]["tools_profile"] == run_a["tools_profile"]]
    print("  共同任务 %d 条，其中契约一致、可比较的 %d 条" % (len(common), len(usable)))
    if len(usable) < len(common):
        print("  → 只能在 %d 条子集上下结论；其余 %d 条需统一契约后重跑"
              % (len(usable), len(common) - len(usable)))


def main() -> None:
    tasks = build_tasks()
    check_dataset(tasks)

    consistent = [t["task_id"] for t in tasks
                  if t["env_snapshot_id"] == DECLARED_SNAPSHOT
                  and t["tools_profile"] == DECLARED_TOOLS]
    stale = [t["task_id"] for t in tasks if t["env_snapshot_id"] == "snap-2024-03"]
    ran = sorted(consistent + stale)

    run_a = {"date": "2024-05-20", "env_snapshot_id": DECLARED_SNAPSHOT,
             "tools_profile": DECLARED_TOOLS, "ran": ran}
    run_b = {"date": "2024-06-18", "env_snapshot_id": DECLARED_SNAPSHOT,
             "tools_profile": DECLARED_TOOLS, "ran": ran}
    diagnose_comparability(run_a, run_b, tasks)

    print("\n  提示：若第二轮只换模型、契约不变 → 分数可比、差异可归因给模型；")
    print("        若同时升级了镜像或工具集，就必须先冻结契约再重跑。")


if __name__ == "__main__":
    main()
```

这份报告的读法：**前三项检查评测集本身是否可信，第四、五项检查跑得起且跑得对，第六项检查历史分数能不能拿来比较。** 在真实项目里，最常见的错误不是「没有评测」，而是「评测集类别失衡 + 契约不一致」，导致分数看起来在动、其实不可解释。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/05-评测/04-评测基准全景.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「自建评测集健全性检查 + 分数可比性诊断」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/05-评测/04-评测基准全景.md)
