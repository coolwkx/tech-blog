---
article_id: kp-790a4ad345a1a751
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-727eecd00fa8
learning_sourceId: 727eecd00fa8
learning_order: 12
learning_objective: 理解并验证：统计、门槛与 CLI
---

# 统计、门槛与 CLI

> **学习目标**：能够解释「统计、门槛与 CLI」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的证据式判定与多标签归因、[02 篇](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md) 的 Manifest 与配对主键、[03 篇](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md) 的 McNemar 与聚类 Bootstrap、[大宗商品价格监控 Agent 复盘](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md) 的规则驱动监控循环。
>
> **所属主题**：-给一个真实Agent补评测 · 评测脚本骨架与基线运行

## 本次只学这一点

```python
def mcnemar_exact_p(fail_to_pass: int, pass_to_fail: int) -> float:
    """双侧 exact p：2 * P(X <= min(b, c)), X ~ Binomial(b + c, 0.5)。"""
    discordant, lower = fail_to_pass + pass_to_fail, min(fail_to_pass, pass_to_fail)
    if discordant == 0:
        return 1.0
    if discordant <= 1024:
        return min(1.0, 2.0 * sum(math.comb(discordant, k)
                                  for k in range(lower + 1)) / float(2 ** discordant))
    log_largest = (math.lgamma(discordant + 1) - math.lgamma(lower + 1)
                   - math.lgamma(discordant - lower + 1) - discordant * math.log(2.0))
    scaled, ratio = 1.0, 1.0
    for k in range(lower, 0, -1):
        ratio *= k / (discordant - k + 1)
        scaled += ratio
    return min(1.0, 2.0 * math.exp(log_largest) * scaled)


def _percentile(values: Sequence[float], probability: float) -> float:
    return values[min(len(values) - 1, max(0, int(probability * len(values))))]


def compare_paired(results: Sequence[dict[str, Any]], iterations: int = 2000,
                   seed: int = 20260819) -> dict[str, Any]:
    """严格配对 + 多标签汇总 + McNemar exact + task-cluster Bootstrap。"""
    baseline = {r["pairKey"]: r for r in results if r["condition"] == "baseline"}
    optimized = {r["pairKey"]: r for r in results if r["condition"] == "optimized"}
    for name, table in (("baseline", baseline), ("optimized", optimized)):
        if len(table) != sum(1 for r in results if r["condition"] == name):
            raise InputError(f"{name} 配对主键重复")
    if set(baseline) != set(optimized):
        raise InputError(f"配对不完整：缺 optimized {sorted(set(baseline) - set(optimized))}；"
                         f"缺 baseline {sorted(set(optimized) - set(baseline))}")

    keys = sorted(baseline)
    fail_to_pass = sum(1 for k in keys if not baseline[k]["passed"] and optimized[k]["passed"])
    pass_to_fail = sum(1 for k in keys if baseline[k]["passed"] and not optimized[k]["passed"])

    clusters: dict[str, list[int]] = {}               # [baseline 通过数, optimized 通过数, 配对数]
    for key in keys:
        cluster = clusters.setdefault(baseline[key]["taskId"], [0, 0, 0])
        cluster[0] += int(baseline[key]["passed"])
        cluster[1] += int(optimized[key]["passed"])
        cluster[2] += 1
    task_ids = sorted(clusters)
    rng = random.Random(seed)
    deltas: list[float] = []
    for _ in range(iterations):
        base = opt = drawn = 0
        for _ in range(len(task_ids)):                # 有放回抽任务簇，整簇进出
            cluster = clusters[task_ids[rng.randrange(len(task_ids))]]
            base += cluster[0]
            opt += cluster[1]
            drawn += cluster[2]
        deltas.append(opt / drawn - base / drawn)     # 先池化再作差
    deltas.sort()

    summary: dict[str, Any] = {}
    for name, table in (("baseline", baseline), ("optimized", optimized)):
        picked = [table[k] for k in keys]
        passed = [r for r in picked if r["passed"]]
        failures: dict[str, int] = {}
        for r in picked:                              # 按全部标签计数：同一次失败进多个类别
            for violation in r["violations"]:
                failures[violation["code"]] = failures.get(violation["code"], 0) + 1
        summary[name] = {"runs": len(picked), "passed": len(passed),
                         "successRate": len(passed) / len(picked),
                         "avgSteps": sum(r["steps"] for r in picked) / len(picked),
                         "failures": failures}

    return {"baseline": summary["baseline"], "optimized": summary["optimized"],
            "paired": {"pairs": len(keys), "failToPass": fail_to_pass, "passToFail": pass_to_fail,
                       "successDelta": summary["optimized"]["successRate"]
                       - summary["baseline"]["successRate"],
                       "mcnemarExactP": mcnemar_exact_p(fail_to_pass, pass_to_fail),
                       "taskClusterCI": {"unit": "task", "clusters": len(task_ids),
                                         "lower": _percentile(deltas, 0.025),
                                         "upper": _percentile(deltas, 0.975)},
                       "regressions": [k for k in keys
                                       if baseline[k]["passed"] and not optimized[k]["passed"]]},
            "results": list(results)}


def build_report(document: dict[str, Any], iterations: int = 2000,
                 seed: int = 20260819) -> dict[str, Any]:
    tasks = {item["taskId"]: _task(item) for item in document["tasks"]}
    runs = [_run(item) for item in document["runs"]]
    if unknown := sorted({run["taskId"] for run in runs} - set(tasks)):
        raise InputError(f"存在没有 TaskSpec 的任务：{unknown}")
    if uncovered := sorted(set(tasks) - {run["taskId"] for run in runs}):   # 应跑全集
        raise InputError(f"任务未执行：{uncovered}")
    return compare_paired([evaluate(tasks[run["taskId"]], run) for run in runs],
                          iterations=iterations, seed=seed)


def gate(report: dict[str, Any], budget: dict[str, Any]) -> list[str]:
    """回归门槛：任何 pass->fail 或低于预算都算失败。"""
    problems = [f"回归：{key} 由通过变为失败" for key in report["paired"]["regressions"]]
    floor, ceiling = float(budget.get("minSuccessRate", 0.0)), float(budget.get("maxAvgSteps", 1e9))
    if report["optimized"]["successRate"] < floor:
        problems.append(f"成功率 {report['optimized']['successRate']:.1%} 低于预算 {floor:.1%}")
    if report["optimized"]["avgSteps"] > ceiling:
        problems.append(f"平均步数 {report['optimized']['avgSteps']:.2f} 超过预算 {ceiling}")
    return problems


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="commodity-monitor 评测器")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="reports/commodity-monitor-report.json")
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260819)
    args = parser.parse_args(argv)
    try:
        document = json.loads(Path(args.input).read_text(encoding="utf-8"))
        report = build_report(document, iterations=args.iterations, seed=args.seed)
    except (InputError, KeyError) as error:
        print(f"输入不合法：{error!r}", file=sys.stderr)
        return 2

    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    before, after, paired = report["baseline"], report["optimized"], report["paired"]
    ci = paired["taskClusterCI"]
    print(f"baseline  {before['successRate']:.1%} ({before['passed']}/{before['runs']})"
          f"  平均步数 {before['avgSteps']:.2f}")
    print(f"optimized {after['successRate']:.1%} ({after['passed']}/{after['runs']})"
          f"  平均步数 {after['avgSteps']:.2f}")
    print(f"配对 {paired['pairs']}：fail->pass={paired['failToPass']}"
          f" pass->fail={paired['passToFail']}  p={paired['mcnemarExactP']:.4f}")
    print(f"task-cluster 95% CI = [{ci['lower']:+.4f}, {ci['upper']:+.4f}]"
          f"（{ci['clusters']} 个任务簇）")
    for name in CONDITIONS:                           # 失败标签按全部标签计数
        if counters := report[name]["failures"]:
            print(f"{name} 失败标签：" + "、".join(
                f"{code}={count}" for code, count in sorted(counters.items())))
    problems = gate(report, document.get("budget", {}))
    for problem in problems:
        print(f"[回归门槛] {problem}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/04-给一个真实Agent补评测.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「统计、门槛与 CLI」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/04-给一个真实Agent补评测.md)
