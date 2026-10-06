---
article_id: kp-ce92fa114c7c43fd
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-727eecd00fa8
learning_sourceId: 727eecd00fa8
learning_order: 11
learning_objective: 理解并验证：判定核心
---

# 判定核心

> **学习目标**：能够解释「判定核心」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的证据式判定与多标签归因、[02 篇](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md) 的 Manifest 与配对主键、[03 篇](../../../../../07-agent/06-评测实战/03-失败归因与显著性检验实战.md) 的 McNemar 与聚类 Bootstrap、[大宗商品价格监控 Agent 复盘](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md) 的规则驱动监控循环。
>
> **所属主题**：-给一个真实Agent补评测 · 评测脚本骨架与基线运行

## 本次只学这一点

```python
"""commodity-monitor 评测器骨架：轨迹 -> 证据式判定 -> 配对统计 -> 回归门槛。

输入：含 tasks / runs 的 JSON（JSONL 按行拆包后调用 build_report 即可）。
退出码：0 通过门槛 / 1 触发回归门槛 / 2 输入不合法。仅依赖标准库。
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence

CONDITIONS = ("baseline", "optimized")


class InputError(ValueError):
    """输入不满足最小 Schema。"""


def _run(raw: dict[str, Any]) -> dict[str, Any]:
    if raw["condition"] not in CONDITIONS:
        raise InputError(f"$.runs[{raw['runId']}].condition: 必须是 {' | '.join(CONDITIONS)}")
    events = []
    for item in raw.get("events", []):
        if item["type"] in ("tool_result", "verification") and "success" not in item:
            raise InputError(f"$.{item.get('eventId')}: {item['type']} 必须声明 success")
        events.append({
            "id": item["eventId"], "type": item["type"], "step": int(item["step"]),
            "success": item.get("success"), "text": item.get("text", ""),
            "citations": list(item.get("citations", [])),
            "evidence": [{"claim": e["claimId"], "value": e["value"],
                          "source": e["sourceEventId"], "hash": e.get("contentHash")}
                         for e in item.get("evidence", [])]})
    return {"runId": raw["runId"], "taskId": raw["taskId"], "condition": raw["condition"],
            "pairKey": f"{raw['taskId']}::{raw['repeatId']}::{raw['seed']}",
            "status": raw["status"], "state": dict(raw.get("finalState", {})), "events": events}


def _task(raw: dict[str, Any]) -> dict[str, Any]:
    if not raw.get("requiredEvidence"):
        raise InputError(f"$.tasks[{raw.get('taskId')}].requiredEvidence: 必须是非空数组")
    return {"taskId": raw["taskId"], "required": list(raw["requiredEvidence"]),
            "assertions": dict(raw.get("assertions", {}))}


def evaluate(task: dict[str, Any], run: dict[str, Any]) -> dict[str, Any]:
    """三层判据：完整性门 -> 状态断言 -> 证据门。违规按固定顺序追加，首项即主归因。"""
    findings: list[tuple[str, str, tuple[str, ...]]] = []

    def add(code: str, message: str, ids: Iterable[str] = ()) -> None:
        merged = tuple(dict.fromkeys(ids))
        for index, (old_code, old_message, old_ids) in enumerate(findings):
            if old_code == code:                      # 同一标签合并，不同标签追加
                text = old_message if message in old_message else f"{old_message}；{message}"
                findings[index] = (code, text, tuple(dict.fromkeys(old_ids + merged)))
                return
        findings.append((code, message, merged))

    # 只有执行成功的 tool_result 才产出可信证据，且来源必须自指
    source = {(i["id"], r["claim"]): (r["value"], r["hash"])
              for i in run["events"] if i["type"] == "tool_result" and i["success"] is True
              for r in i["evidence"] if r["source"] == i["id"]}
    declared = [r for i in run["events"]
                if i["type"] == "verification" and i["success"] is True for r in i["evidence"]]
    invalid = [r for r in declared if source.get((r["source"], r["claim"])) != (r["value"], r["hash"])]
    verified = {r["claim"] for r in declared if r not in invalid}

    calls = [i for i in run["events"] if i["type"] == "tool_call"]
    finals = [i for i in run["events"] if i["type"] == "final"]
    final = finals[-1] if finals else None

    if not run["events"]:
        add("missing_trajectory", "轨迹为空")
    if not calls:
        add("zero_step_termination", "没有执行任何工具步骤")
    if final is None or not final["text"].strip():
        add("empty_final_answer", "最终回答为空")
    if invalid:
        add("invalid_evidence_source", "证据未绑定成功的 tool_result 或内容被篡改",
            (r["claim"] for r in invalid))
    missing = [c for c in task["required"] if c not in verified]
    if missing:
        add("missing_evidence", f"缺少已验证证据：{'、'.join(missing)}", missing)
    unchecked = [c for c in task["required"] if c not in (final["citations"] if final else [])]
    if unchecked:
        add("missing_evidence", f"最终回答未引用证据：{'、'.join(unchecked)}", unchecked)
    failed = [k for k, want in task["assertions"].items() if run["state"].get(k) != want]
    if failed:
        add("assertion_failed", "最终状态断言未满足：" + "、".join(
            f"{k}(期望 {task['assertions'][k]!r}，实际 {run['state'].get(k)!r})" for k in failed))
    if run["status"] == "failed" and any(
            i["type"] == "tool_result" and i["success"] is False for i in run["events"]):
        add("tool_error", "工具错误后未恢复")
    if run["status"] == "blocked":
        add("blocked", "任务被明确阻断")
    if run["status"] == "failed":
        add("goal_not_completed", "运行状态未完成")

    return {"runId": run["runId"], "taskId": run["taskId"], "condition": run["condition"],
            "pairKey": run["pairKey"], "passed": not findings,
            "primaryFailure": findings[0][0] if findings else "none",
            "violations": [{"code": c, "message": m, "evidenceIds": list(i)} for c, m, i in findings],
            "steps": len({i["step"] for i in calls})}
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/04-给一个真实Agent补评测.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「判定核心」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/04-给一个真实Agent补评测.md)
