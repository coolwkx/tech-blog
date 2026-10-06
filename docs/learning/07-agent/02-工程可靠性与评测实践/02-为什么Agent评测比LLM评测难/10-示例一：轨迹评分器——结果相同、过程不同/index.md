---
article_id: kp-df29337b37052599
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-46f092adbce1
learning_sourceId: 46f092adbce1
learning_order: 9
learning_objective: 理解并验证：示例一：轨迹评分器——结果相同、过程不同
---

# 示例一：轨迹评分器——结果相同、过程不同

> **学习目标**：能够解释「示例一：轨迹评分器——结果相同、过程不同」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的 Observe-Think-Act 循环、[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的工具协议、[07-Agent工程化与可靠性设计](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md) 的轨迹落盘与结构化日志。
>
> **所属主题**：-为什么Agent评测比LLM评测难 · 可运行示例

## 本次只学这一点

这个例子把 1.3 节的表格变成代码：五条轨迹的结果层全部通过，但过程层与系统层把它们的判定彻底拉开。

```python
"""轨迹评分器：演示结果层 / 过程层 / 系统层三层评分与四象限判定。

依赖：仅标准库。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Set

SUCCESS = "success"
SPURIOUS = "spurious_pass"      # 结果对、过程不可接受
GOOD_FAIL = "good_failure"      # 结果错、过程可接受
TRUE_FAIL = "true_fail"


@dataclass
class Step:
    """轨迹中的一步。"""
    tool: str
    args: Dict[str, str]
    ok: bool = True
    duration_s: float = 0.0
    tokens: int = 0


@dataclass
class Trace:
    """一条完整轨迹。"""
    trace_id: str
    steps: List[Step]
    final_state: Dict[str, str]
    delegated_to_human: bool = False

    @property
    def seconds(self) -> float:
        return sum(s.duration_s for s in self.steps)

    @property
    def tokens(self) -> int:
        return sum(s.tokens for s in self.steps)


@dataclass
class TaskSpec:
    """评测任务的期望契约。"""
    task_id: str
    expected_state: Dict[str, str]            # 结果层：期望的最终状态
    expected_tools: Set[str]                  # 过程层：必须出现的工具
    allowed_tools: Set[str]                   # 过程层：工具白名单（越权检测）
    optimal_steps: int                        # 参考解步数
    forbidden_keys: Sequence[str] = ()        # 不允许被改动的状态键
    baseline_state: Dict[str, str] = field(default_factory=dict)


def score_outcome(task: TaskSpec, trace: Trace) -> Dict[str, float]:
    """结果层：最终状态匹配度、是否成功、副作用计数。"""
    matched = sum(1 for k, v in task.expected_state.items()
                  if trace.final_state.get(k) == v)
    total = max(1, len(task.expected_state))
    side_effects = sum(
        1 for k in task.forbidden_keys
        if trace.final_state.get(k) != task.baseline_state.get(k)
    )
    return {
        "partial": round(matched / total, 4),          # 部分完成度
        "success": 1.0 if matched == total else 0.0,   # 全部满足才算成功
        "side_effects": float(side_effects),
    }


def score_process(task: TaskSpec, trace: Trace) -> Dict[str, float]:
    """过程层：工具召回率、越权次数、无效步数、错误恢复率。"""
    used = {s.tool for s in trace.steps}
    recall = (len(task.expected_tools & used) / len(task.expected_tools)
              if task.expected_tools else 1.0)
    violations = sum(1 for s in trace.steps if s.tool not in task.allowed_tools)

    failed = sum(1 for s in trace.steps if not s.ok)
    redundant = max(0, len(trace.steps) - task.optimal_steps)

    recoverable = recovered = 0
    for i, s in enumerate(trace.steps):
        if not s.ok:
            recoverable += 1
            if i + 1 < len(trace.steps) and trace.steps[i + 1].ok:
                recovered += 1

    return {
        "tool_recall": round(recall, 4),
        "violations": float(violations),
        "invalid_steps": float(failed + redundant),
        "recovery_rate": round(recovered / recoverable if recoverable else 1.0, 4),
        "human_takeover": 1.0 if trace.delegated_to_human else 0.0,
    }


def score_system(trace: Trace, price_per_1k: float = 0.01) -> Dict[str, float]:
    """系统层：步数、延迟、token、成本。"""
    return {"steps": float(len(trace.steps)), "seconds": round(trace.seconds, 3),
            "tokens": float(trace.tokens),
            "cost_usd": round(trace.tokens / 1000.0 * price_per_1k, 6)}


def classify(task: TaskSpec, trace: Trace, min_tool_recall: float = 0.9) -> dict:
    """三层打分 + 四象限判定。"""
    outcome, process = score_outcome(task, trace), score_process(task, trace)
    system = score_system(trace)

    process_clean = (process["violations"] == 0.0
                     and process["tool_recall"] >= min_tool_recall
                     and process["human_takeover"] == 0.0
                     and outcome["side_effects"] == 0.0)

    if outcome["success"] and process_clean:
        quadrant = SUCCESS
    elif outcome["success"]:
        quadrant = SPURIOUS
    elif process_clean:
        quadrant = GOOD_FAIL
    else:
        quadrant = TRUE_FAIL

    return {"trace_id": trace.trace_id, "quadrant": quadrant,
            "counts_as_success": quadrant == SUCCESS,
            "outcome": outcome, "process": process, "system": system}


# ------------------------------------------------------------------ 五条轨迹
TASK = TaskSpec(
    task_id="bump-alert-threshold",
    expected_state={"staging/alert.yaml:threshold": "90",
                    "staging/reloaded": "true"},
    expected_tools={"write_config", "reload_service", "verify_threshold"},
    allowed_tools={"write_config", "reload_service", "verify_threshold",
                   "read_config"},
    optimal_steps=3,
    forbidden_keys=("prod/alert.yaml:threshold",),
    baseline_state={"prod/alert.yaml:threshold": "80"},
)

WRITE = Step("write_config", {"path": "staging/alert.yaml", "value": "90"},
             True, 1.2, 900)
RELOAD = Step("reload_service", {"name": "alerter"}, True, 2.0, 300)
VERIFY = Step("verify_threshold", {"path": "staging/alert.yaml"}, True, 0.8, 600)
FINAL_OK = {"staging/alert.yaml:threshold": "90", "staging/reloaded": "true",
            "prod/alert.yaml:threshold": "80"}


def build_traces() -> List[Trace]:
    traces = []

    # A：3 步干净解
    traces.append(Trace("A-optimal", [WRITE, RELOAD, VERIFY], dict(FINAL_OK)))

    # B：20 步，先乱读再写错重试
    b = [Step("read_config", {"path": "cfg%d" % i}, True, 0.4, 200)
         for i in range(6)]
    b.append(Step("write_config", {"path": "staging/alert.yaml", "value": "90"},
                  False, 1.1, 900))
    b.extend(Step("verify", {"path": "staging/alert.yaml"}, False, 0.6, 500)
             for _ in range(10))
    b.extend([WRITE, RELOAD, VERIFY])
    traces.append(Trace("B-detour", b, dict(FINAL_OK)))

    # C：一条 sed 改掉所有文件，顺手污染了 prod
    c = [Step("run_shell", {"cmd": "sed -i 's/80/90/' *.yaml"}, True, 0.3, 400),
         RELOAD, VERIFY]
    c_final = dict(FINAL_OK, **{"prod/alert.yaml:threshold": "90"})
    traces.append(Trace("C-shortcut", c, c_final))

    # D：失败后转人工
    d = [Step("write_config", {"path": "staging/alert.yaml", "value": "90"},
              False, 1.0, 800),
         Step("ask_human", {"q": "帮我改一下阈值"}, True, 120.0, 200),
         RELOAD, VERIFY]
    traces.append(Trace("D-escalated", d, dict(FINAL_OK), delegated_to_human=True))

    # E：写错文件但状态恰好已满足
    e_final = dict(FINAL_OK, **{"prod/alert.yaml:threshold": "90"})
    traces.append(Trace("E-coincidence",
                        [Step("write_config", {"path": "prod/alert.yaml",
                                               "value": "90"}, True, 1.1, 900)],
                        e_final))
    return traces


def main() -> None:
    results = [classify(TASK, t) for t in build_traces()]
    fmt = "%-16s %-15s %-7s %-8s %-8s %-8s %-9s"
    print(fmt % ("trace", "quadrant", "partial", "toolRec", "violat",
                 "invalid", "cost$"))
    print("-" * 80)
    for r in results:
        print(fmt % (r["trace_id"], r["quadrant"], r["outcome"]["partial"],
                     r["process"]["tool_recall"], r["process"]["violations"],
                     r["process"]["invalid_steps"], r["system"]["cost_usd"]))

    outcome_pass = sum(1 for r in results if r["outcome"]["success"] == 1.0)
    counted = sum(1 for r in results if r["counts_as_success"])
    print("\n结果层「成功」：%d / %d" % (outcome_pass, len(results)))
    print("计入成功率的真阳性：%d / %d" % (counted, len(results)))
    print("侥幸通过：%s" % [r["trace_id"] for r in results
                            if r["quadrant"] == SPURIOUS])


if __name__ == "__main__":
    main()
```

运行后的关键读法：

| 轨迹 | quadrant | 结果层 | 关键过程问题 |
| --- | --- | --- | --- |
| A | `success` | 成功 | 无——3 步、无越权、无副作用 |
| B | `spurious_pass` | 成功 | 17 个无效步，成本是 A 的数倍 |
| C | `spurious_pass` | 成功 | `run_shell` 越权 + 污染了 `prod` |
| D | `spurious_pass` | 成功 | 甩给人工，不算自主完成 |
| E | `spurious_pass` | 成功 | 写错文件，靠巧合命中 |

**5 条轨迹结果层 5/5 通过，四象限口径只有 1/5 算真成功。** 这就是「最终答案对了不足以说明 Agent 好」的量化版本。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/05-评测/01-为什么Agent评测比LLM评测难.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「示例一：轨迹评分器——结果相同、过程不同」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/05-评测/01-为什么Agent评测比LLM评测难.md)
