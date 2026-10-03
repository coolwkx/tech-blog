> **一句话总结**：给一个已经在跑的真实 Agent 补评测，不需要重写 Agent——只需要把它已经在写的日志改造成**带证据的结构化轨迹**，然后按「定义任务集 → 定义成功判据（含证据要求）→ 定义指标 → 搭评测脚本 → 跑基线 → 定位失败 → 接进 CI」七步走；本文以一个大宗商品价格监控 Agent 为例，给出 15 条评测用例、可运行的评测脚本与九类真实失败模式的根因。
> **前置知识**：[01 篇](01-项目复盘-AgentEvalLab.md) 的证据式判定与多标签归因、[02 篇](02-用Manifest保证评测可复现.md) 的 Manifest 与配对主键、[03 篇](03-失败归因与显著性检验实战.md) 的 McNemar 与聚类 Bootstrap、[大宗商品价格监控 Agent 复盘](../07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md) 的规则驱动监控循环。
> **学完能做到**：
> 1. 画出一个多源抓价 + 状态机 + 推送 + 落盘 + 看板的 Agent 链路，并列出每一段的失效面。
> 2. 写出 15 条带「期望产物 / 断言 / 证据要求」的评测用例，并解释为什么每条断言都必须有证据支撑。
> 3. 用一份可直接运行的评测脚本跑出基线报告、定位失败类型，并把回归门槛接进 CI。

---

## 1. 目标 Agent：五段链路与失效面

### 1.1 为什么拿它当样本

它具备真实 Agent 的全部麻烦：外部数据不可靠（多源不一致）、有状态（阈值 + 滞回）、有副作用（推送、写文件）、有并发（定时任务 + 看板）、有环境依赖（时区、单位）。现状通常只有一个 `monitor.log`（自由文本）和一张看板——想回答"改了聚合函数之后系统变好了吗"，只能人工翻日志。**补评测的第一步不是写代码，而是承认"我现在没有任何可判定的东西"。**

### 1.2 五段链路

```text
① 采集层   源A 交易所 JSON / 源B 资讯页 HTML / 源C 聚合 API · 超时/重试/降级/限流
                          │ 原始价 + 单位 + 币种 + 时区 + 抓取时刻
② 归一化层 单位换算 · 币种换算 · 时区统一 UTC+8 · 多源一致性（价差/中位数/stale）
                          │ 归一价 + 一致性结论
③ 决策层   状态机 normal/buy/sell/alert + 阈值 + 滞回 + 去抖
          条件A：状态变化→推送   条件B：超时未提醒→重复提醒
                          │ 状态迁移 + 通知意图
④ 行动层   推送（Server 酱/企微/飞书）+ 重试 · JSON 落盘
                          │ 送达回执 + 文件偏移
⑤ 展示层   看板读取 state/history 渲染走势
```

### 1.3 每段的失效面

| 段 | 失效模式 | 表面症状 | 真实后果 |
| --- | --- | --- | --- |
| ① | 主源超时未降级 | 日志一行 `timeout` | 本轮无数据，历史出现空洞 |
| ① | 抓取失败返回 `null`，写成 `price or 0` | 无报错 | **价格 0 触发"买入"** |
| ① | 静默返回上一次缓存值 | 数据看着正常 | stale 数据被当实时数据用 |
| ② | 多源价差 1.8% 未标记，用均值而非中位数 | 平滑的数字 | 极端值污染共识价 |
| ② | 单位换算常数错（lb→吨用 2000 而非 2204.62） | 固定约 10% 偏差 | 阈值长期误触发或永不触发 |
| ② | UTC 时间戳当本地时间落盘 | 时间戳格式合法 | 交易日归属错，日报重复或丢失 |
| ③ | 阈值附近反复穿越，缺滞回 / 限流窗口写错（`>` 写成 `>=`） | 推送风暴 / 边界时刻多推一条 | 用户静音通知，系统失效；难以复现的重复告警 |
| ④ | 推送 502 被吞，state 已更新 | `status=completed` | **状态推进了、副作用没发生**，通知永久丢失 |
| ④ | 重跑导致 history 重复追加 | 文件变长 | 走势图出现假尖峰 |
| ⑤ | 写入竞态，看板读到半截 JSON | 偶发白屏 | 被当成"前端 bug"排查很久 |
| 全链路 | 运行器只看退出码 | 全绿 | **以上 10 条全部不产生告警** |

最后一行是补评测的根本动机：**这些问题都不会让进程返回非零退出码**——它们正好是 [01 篇](01-项目复盘-AgentEvalLab.md) 说的"进程完成 ≠ 目标完成"。

---

## 2. 任务集设计：15 条评测用例

### 2.1 设计原则

1. **每条任务对应一个失效面。** 不要写"抓价正常"，要写"主源超时降级到备源"，让失败能直接定位到代码。
2. **每条任务都有可验证的期望产物。** 期望产物是**状态快照**与**证据 claim**，不是"日志里出现某句话"。
3. **难度按链路层数分层。** easy = 单段；medium = 两段 + 一个边界；hard = 三段以上 + 一个反常输入。
4. **覆盖优先级：行动层 > 决策层 > 归一化层 > 采集层**，因为副作用不可回滚。
### 2.2 完整用例设计表

| # | 任务 ID | 难度 | 输入场景 | 期望产物 | 断言 | 证据要求 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `snap-single-source` | easy | 源 A 返回 `WTI=78.42 USD/bbl` | state 更新 + history 追加 1 行 | `state.status="normal"`；`history.appended=1` | `wti_price`、`persisted_at` |
| 2 | `unit-normalize` | easy | 铜价 `4.35 USD/lb` | 归一价写入 history | `history.unit="USD/tonne"`；`history.value≈9589` | `raw_price`、`normalized_price`、`unit_factor` |
| 3 | `tz-bucket` | easy | 抓取时刻 `2026-03-02T01:30:00Z` | history 归属交易日 | `history.tradeDate="2026-03-02"` | `trade_date`、`history_offset` |
| 4 | `board-read-latest` | easy | state 与 history 均存在 | 看板 payload | `board.stateTs==state.updatedAt`；`board.historyLen=3` | `board_payload_ts`、`board_history_len` |
| 5 | `multi-source-conflict` | medium | 三源 `78.42/79.90/78.31`，价差 1.99% > 1.5% | 共识价 + 分歧标记 | `state.consensusSource="median"`；`state.staleFlag="fresh"` | `source_spread`、`consensus_price`、`stale_flag` |
| 6 | `primary-source-degrade` | medium | 源 A 超时，源 B/C 正常 | 用 B/C 出共识 | `state.consensusSource="degraded"`；`state.sourceCount=2` | `source_attempts`、`active_sources` |
| 7 | `stale-data-guard` | medium | 三源返回 `null`，缓存只有 6 小时前的值 | state 不变 + 标记 stale | `state.status` 不变；`state.staleFlag="stale"`；`state.notified=false` | `stale_flag`、`cache_age_seconds` |
| 8 | `threshold-boundary` | medium | 价格恰好等于 `buy_threshold=800` | 不推送（严格不等号） | `state.status="normal"`；`state.notified=false` | `threshold_compare`、`state_before` |
| 9 | `idempotent-rerun` | medium | 同一 `(runId, 抓取时刻)` 执行两次 | history 只追加 1 行 | `history.appended=1`；`history.duplicateSkipped=1` | `idempotency_key`、`history_offset` |
| 10 | `notify-retry` | hard | 首次推送 502，第二次成功 | 送达 + 尝试次数 | `state.notifyDelivered=true`；`notify.attempts=2` | `notify_attempt`、`notify_delivery_id` |
| 11 | `hysteresis-no-flap` | hard | 价格在阈值附近 5 次小幅穿越 | 至多推送 1 次 | `notify.count<=1`；`state.statusChanges<=1` | `status_change_log`、`notify_count` |
| 12 | `null-not-zero` | hard | 源 A 返回 `null`，源 B/C 正常 | 忽略 A，不使用 0 | `state.price` 不为 0；`state.usedFallback=true` | `null_source_ids`、`consensus_price` |
| 13 | `cross-day-report` | hard | 连续两交易日各 3 次抓取，跨 UTC 午夜 | 日报分属两日，无重复无缺失 | `report.days=2`；`report.duplicatedDates=[]` | `report_dates`、`history_offsets` |
| 14 | `history-append-order` | hard | history 已 100 行，追加第 101 行 | 单调递增的 `appendedAt` | `history.appended=1`；`history.monotonic=true` | `last_offset_before`、`last_offset_after` |
| 15 | `partial-outage` | hard | 源 A 超时 + 源 B stale + 源 C 正常 | 标记部分失效并降级决策 | `state.staleFlag="partial"`；`state.status` 不变 | `source_attempts`、`stale_flag`、`active_sources` |

### 2.3 覆盖矩阵

覆盖分布：① 采集 = 6、7、12、15（4 条）；② 归一化 = 2、3、5（3 条）；③ 决策 = 8、11、15（3 条）；④ 行动 = 1、9、10、14（4 条）；⑤ 展示 = 4（1 条）；跨段/时序 = 13（1 条）。

第 15 条同时覆盖三段——**"多段同时坏"才是 hard 的真正含义**，而不是把单段参数调得更极端。

---

## 3. 成功判据与证据要求

### 3.1 三层判据，逐层否决

```text
第一层 完整性门：轨迹非空 / 有 tool_call / final 非空
      ↓ 不过 → missing_trajectory · zero_step_termination · empty_final_answer
第二层 状态断言：finalState 的每个 key 等于期望值
      ↓ 不过 → assertion_failed
第三层 证据门：每条 requiredEvidence 都来自成功 tool_result、值/哈希一致、被 final 引用
      ↓ 不过 → invalid_evidence_source · missing_evidence
      ↓ 全过 → PASS
```

**为什么状态断言也要有证据？** 因为状态是系统自己写的。`state.notifyDelivered=true` 完全可能在 HTTP 请求**之前**就写好了（1.3 节的"状态推进了、副作用没发生"）。判据必须成对：**断言说"结果是什么"，证据说"这个结果怎么来的"。**

### 3.2 证据 claim 命名规范

| 后缀 | 含义 | 例 |
| --- | --- | --- |
| `_price` / `_spread` | 具体价格值 / 派生差异量 | `wti_price`、`source_spread` |
| `_flag` / `_attempts` | 状态标记 / 尝试次数 | `stale_flag`、`notify_attempt` |
| `_id` | 外部系统返回的标识 | `notify_delivery_id` |
| `_offset` / `_len` | 文件位置 / 长度 | `history_offset`、`board_history_len` |
| `_ts` / `_date` | 时间戳 / 日期 | `persisted_at`、`trade_date` |

两个约定：①每条 claim 必须由 `tool_result` 事件产出，不允许由 `plan` 或 `final` 产出；②**派生量与原始量都要留证据**（既要有 `raw_price` 也要有 `normalized_price` 和 `unit_factor`），否则无法区分"抓错了"和"换算错了"。

### 3.3 一条任务的判据与轨迹

```json
{"taskId": "notify-retry", "difficulty": "hard",
 "objective": "推送 502 后按退避策略重试直至送达，且只在送达后更新状态",
 "requiredEvidence": ["notify_attempt", "notify_delivery_id"],
 "assertions": {"state.notifyDelivered": true}}
```

对应轨迹（节选，省略了 `tool_call` 事件与 `tool` 字段）：

```json
{"runId": "optimized-notify-retry-r1", "taskId": "notify-retry", "condition": "optimized",
 "repeatId": "r1", "seed": 1, "status": "completed",
 "finalState": {"state.notifyDelivered": true},
 "events": [
   {"eventId": "o3-res-1", "type": "tool_result", "step": 1, "success": false},
   {"eventId": "o3-res-2", "type": "tool_result", "step": 2, "success": true, "evidence": [
     {"claimId": "notify_attempt", "value": "2", "sourceEventId": "o3-res-2"},
     {"claimId": "notify_delivery_id", "value": "wx-7712", "sourceEventId": "o3-res-2"}]},
   {"eventId": "o3-ver", "type": "verification", "step": 2, "success": true, "evidence": [
     {"claimId": "notify_attempt", "value": "2", "sourceEventId": "o3-res-2"},
     {"claimId": "notify_delivery_id", "value": "wx-7712", "sourceEventId": "o3-res-2"}]},
   {"eventId": "o3-fin", "type": "final", "step": 2, "text": "第 2 次推送送达 wx-7712",
    "citations": ["notify_attempt", "notify_delivery_id"]}]}
```

三个关键点：失败的 `tool_result` 不产出可信证据；`verification` 的 `sourceEventId` 必须指向 `o3-res-2`（**不是** `o3-call-2`）；`final.citations` 必须列出两条 claim。把 `notify_delivery_id` 改成 `wx-forged`，判定立刻变成 `invalid_evidence_source`。

---

## 4. 指标口径与统计方法

### 4.1 指标表

| 指标 | 定义 | 口径要点 |
| --- | --- | --- |
| 任务成功率 / `pass^k` | 通过运行占比 / 同一任务 k 次全通过占比 | 通过 = 零违规，不是"状态字符串对了" |
| 证据完整率 | `requiredEvidence` 全部验证且被引用的运行占比 | 与成功率的差 = "做对了但没说清" |
| 失败标签分布 | 按 `primaryFailure` 统计 | 各类之和 = 失败运行数，可归一化 |
| 违规标签计数 | 按 `violations` 全量统计 | **同一次失败进多个类别，不可归一化** |
| 平均步数（全量 / 成功） | 两个口径必须同时报告 | 全量会被"提前失败"拉低，造成虚假效率 |
| 多源一致率 · 推送送达率 · 时区正确率 | 非 stale 占比 / 送达数占应有通知数 / `tradeDate` 正确占比 | 数据质量、副作用与时间语义指标，优先级最高 |

### 4.2 统计方法与预算门槛

| 场景 | 方法 | 注意 |
| --- | --- | --- |
| A/B 对比 | 按 `taskId::repeatId::seed` 严格配对 | 重复或孤立主键直接报错，不静默丢弃 |
| 方向性显著性 + 区间 | McNemar exact p-value；以 `taskId` 为聚类单位的 Bootstrap CI | 只看 `fail→pass` 与 `pass→fail`；重采样单位是任务不是运行 |
| 回归 + 成本门槛 | `pass→fail > 0` 直接失败；成功率下限 + 平均步数上限 | 两个成本门槛都要有，否则"更早失败"看起来更省 |

```json
{"budget": {"minSuccessRate": 0.90, "maxAvgSteps": 2.0, "maxRegressions": 0}}
```

`maxRegressions: 0` 是刻意的：**成功率可以因新增难任务而下降并被容忍，但"原本通过的任务现在失败"永远不可接受**，因为它意味着改动破坏了已工作的功能。

---

## 5. 评测脚本骨架与基线运行

脚本完整实现了 [01 篇](01-项目复盘-AgentEvalLab.md) 的判定顺序、[03 篇](03-失败归因与显著性检验实战.md) 的两个统计量，以及"应跑全集不许从分母消失"的闸门。仅依赖标准库。

### 5.1 判定核心

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

### 5.2 统计、门槛与 CLI

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

### 5.3 跑一次基线

四任务（`snap-single-source` / `multi-source-conflict` / `notify-retry` / `timezone-bucket`）各跑 baseline 与 optimized：

```bash
python monitor_eval.py --input monitor-runs.json --output reports/baseline.json
```

```text
baseline  25.0% (1/4)  平均步数 1.00
optimized 100.0% (4/4)  平均步数 1.25
配对 4：fail->pass=3 pass->fail=0  p=0.2500
task-cluster 95% CI = [+0.2500, +1.0000]（4 个任务簇）
baseline 失败标签：assertion_failed=2、goal_not_completed=2、missing_evidence=2、tool_error=1
```

**这份基线最重要的信息不是 100%，而是 `p=0.2500` 和宽度 0.75 的置信区间。** 4 个任务簇给出的区间几乎覆盖整个 `[0, 1]`，说明"提升到 100%"**完全没有统计支撑**——它只是 4 条合成任务的演示。生产接入必须先跑 30–50 条任务再谈显著性（见 [03 篇](03-失败归因与显著性检验实战.md) 5.5 节）。
### 5.4 四道闸门

| 输入 | 退出码 | 输出 |
| --- | ---: | --- |
| 合法轨迹 | 0 | 报告 + 摘要 |
| 删掉 `notify-retry` 的全部 run | 2 | `输入不合法：任务未执行：['notify-retry']` |
| 同一 `pairKey` 出现两次 | 2 | `输入不合法：baseline 配对主键重复` |
| 某条原本通过的任务变失败 | 1 | `[回归门槛] 回归：snap-single-source::r1::1 由通过变为失败` |
| 篡改 `notify_delivery_id` 的值 | 1 | 该运行 `primaryFailure=invalid_evidence_source` |

退出码 2 与 1 的分工很重要：2 是"数据问题，去看那行 JSON"，1 是"功能回归，去看那次改动"。`_run`/`_task` 里那些抛 `InputError` 的检查作用相同——**任何"数据不完整也能出报告"的口子都会被滥用**。

---

## 6. 失败案例、CI 回归与自测

### 6.1 九类典型失败

| # | 现象 | 表面证据 | 根因 | 判定标签 |
| --- | --- | --- | --- | --- |
| 1 | 三源价差 1.8%，共识价却用了均值 | `consensus_price` 有值 | 聚合用 `mean` 不是 `median`，且价差超阈值未标记 | `assertion_failed` |
| 2 | 阈值附近 5 次穿越推了 5 条消息 | 每条推送都成功 | 缺滞回，状态机在边界抖动 | `assertion_failed` |
| 3 | 推送 502 被吞，state 已更新为已提醒 | `status=completed`、`notifyDelivered=true` | HTTP 错误未抛，且**状态在请求前就写了** | `invalid_evidence_source` + `missing_evidence` |
| 4 | UTC 时间戳当本地时间写 history / 铜价换算偏差 10% | 时间戳格式合法 / 换算后价格看着合理 | 缺时区转换（`utcnow()` 直接落盘）；`lb → tonne` 用了 2000 而非 2204.62 | `assertion_failed` |
| 5 | 抓取失败返回 `null`，触发"买入" | 推送成功、日志正常 | `price or 0` 把 `None` 变 0，0 < 阈值 → 买入 | `assertion_failed` |
| 6 | 重跑后 history 出现重复行 / 看板偶发白屏 | 文件行数变多 / 前端报 JSON 解析错 | 幂等键缺失；写入读取竞态（读到半截文件） | `assertion_failed` |
| 7 | 日志显示 `completed` 但什么都没做 | 退出码 0 | 运行器把"没报错"当成功 | `zero_step_termination` |### 6.2 根因归类与修法

| 根因类型 | 案例 | 修法 | 修完加强的用例 |
| --- | --- | --- | --- |
| 聚合算法错 | 1 | 改中位数 + 价差超阈值时标记 `staleFlag` | 5、15 |
| 缺时序保护 | 2、6 | 滞回 + 幂等键 + 原子写（临时文件 + rename） | 9、11、14 |
| 副作用与状态顺序错 | 3 | **先确认送达再更新状态**；错误必须向上抛 | 10 |
| 时间 / 单位 / 空值处理错 | 4、5 | 全链路 UTC 存储；换算常数集中定义 + 单测；`None` 显式判断，禁止 `or 0` | 2、3、12、13 |
| 运行器语义错 | 7 | 完整性门（轨迹非空 / 有工具步骤 / 有最终回答） | 全部 |

第 3 类值得单独强调：**它是唯一一类"成功率看起来很高但生产会静默丢通知"的失败。** 如果判据只有 `state.notifyDelivered == true`，它 100% 通过。只有要求"送达证据由成功的 `tool_result` 产出"才能把它揪出来——这就是 evidence-based judging 的实际价值，不是为了严谨而严谨。
### 6.3 接入 CI

```yaml
name: agent-eval
on: {pull_request: {paths: ["agent/**", "eval/**"]}}
jobs:
  evaluate:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.12"}
      - name: 跑评测（退出码 1 = 有回归或低于预算）
        run: python eval/monitor_eval.py --input eval/fixtures/monitor-runs.json
                     --output reports/monitor-report.json
      - uses: actions/upload-artifact@v4
        if: always()
        with: {name: monitor-eval-report, path: reports/monitor-report.json}
```

四条接入规则：①**固定 Bootstrap seed**（脚本默认 `20260819`），否则统计量每次都在抖，回归判定会变成随机通过；②**报告必须上传为 artifact**，即使失败也要（`if: always()`）；③**两条独立门槛**——脚本内的 `budget`（成功率/步数）可协商，`pass→fail > 0` 不可；④**报告做字段级 diff，不做整文件 diff**（`generatedAt` 每次都变），断言 `pairs`、`failToPass`、`passToFail`、`successRate`、`mcnemarExactP`、`taskClusterCI`。

### 6.4 面试问答

<details>
<summary><strong>Q1：给一个只有文本日志的 Agent 补评测，第一步做什么？</strong></summary>

不是写脚本，而是**把日志改造成带证据的结构化轨迹**：①定义事件类型（`tool_call`/`tool_result`/`verification`/`final`），工具调用成对记录且 `tool_result` 必带 `success`；②每个工具成功时产出 `claimId` + `value` + `sourceEventId`，而不是一句人话；③结束时输出 `final` 并显式 `citations`。

顺序不能反：三层判据的后两层**全部依赖轨迹里有结构化证据**。日志是自由文本时，评测脚本只能做字符串匹配，就退化成了"状态字符串对了算通过"——[01 篇](01-项目复盘-AgentEvalLab.md) 整篇在避免的事。验收判据：**能否用一段代码从日志回答"这个数字怎么算出来的"**（哪次调用、哪个返回值、什么单位）。

</details>

<details>
<summary><strong>Q2：为什么"推送失败未重试"用状态断言查不出来？</strong></summary>

因为**状态是系统自己写的**。典型形状是先 `state.notifyDelivered = true`，再 `http_post(...)`（异常被吞），最后落盘——从断言视角看完全成立，但**"状态推进"与"副作用发生"之间没有因果关系**。

判据必须要求送达有外部证据：`notify_delivery_id` 由**执行成功的 `tool_result`** 产出（502 那次 `success: false`，不产出可信证据），且被 `final.citations` 引用。这样"只写状态没真发出去"会同时命中 `invalid_evidence_source` 与 `missing_evidence`。

原则：**凡副作用（发消息、写外部系统、扣款、删文件）都不能只用内部状态断言，必须有外部回执作证据**——副作用不可回滚，假阳性代价远高于假阴性。

</details>

<details>
<summary><strong>Q3：15 条任务跑出 80% → 88%，能上线吗？</strong></summary>

四组信息缺一不可。①**配对结构**：8 点差是 `(b − c)/N`，必须拿到 2×2 表；重点看 `pass→fail`，若有 3 条原本通过的任务现在失败，说明改动**破坏了已工作的功能**，平均值涨了也不能上（这正是 `maxRegressions: 0` 的理由）。②**聚类 CI**：15 个任务簇的区间会宽到跨 0，要报 `88%（95% CI [x, y]，n=15）`——**增加任务簇数远比增加每任务重复次数有效**。③**失败类型分布**：若 `tool_error` 从 4 降到 0 而 `assertion_failed` 从 1 涨到 3，那是失败**换了个形式**，平均值看不出来。④**系统层与副作用**：全量/成功两种步数口径是否一致？送达率、一致率、时区正确率有没有退化？**成功率涨但送达率跌**是典型的"报了更多、发出去更少"。

</details>

### 6.5 自测题

<details>
<summary>参考答案</summary>

**1. 为什么每条任务都要有 `requiredEvidence`，而不是只写 `assertions`？**

断言检查**结果**，证据检查**结果的来源**。`assertions: {"state.notifyDelivered": true}` 只能证明系统**声称**送达；`requiredEvidence: ["notify_delivery_id"]` 要求这个声称有外部回执支撑——由成功 `tool_result` 产出、被 `verification` 以一致的值和哈希引用、被 `final.citations` 列出。

只有断言时，"先写状态再发请求、异常被吞"100% 通过；只有证据时，无法判断结果是否满足业务期望。**成对才有意义**：断言定义"什么算成功"，证据保证"这个成功是真的"。它还驱动可诊断性——`missing_evidence` 能报出具体缺哪个 claim，而不是笼统的"证据不足"。

</details>

<details>
<summary>参考答案</summary>

**2. `stale-data-guard`（三源 null、缓存 6 小时前）的期望产物应该是什么？**

**state 不变 + 标记 stale + 不推送**，三件事同时成立：

```json
{"assertions": {"state.status": "<与上一次相同>", "state.staleFlag": "stale",
                "state.notified": false},
 "requiredEvidence": ["stale_flag", "cache_age_seconds"]}
```

①**不能用缓存顶上去**：拿 6 小时前的价格做阈值决策，会产生基于过期数据的买卖建议，这是最危险的一类错误。②**不能沉默**：不标记则看板与日报无法区分"没触发"和"没数据"。③**不能推送**：这是数据质量事件而非价格事件，混进价格渠道会污染信任。`cache_age_seconds` 是必需的——它让 `stale_flag` 成为**可验证的派生结论**（"年龄 21600s > 阈值 3600s"），否则测试无法区分"正确判定"和"永远返回 stale"。

</details>

<details>
<summary>参考答案</summary>

**3. 如何让"回归"比"分数下降"更严格？**

把两类失败分开：**功能回归**（`pass→fail > 0`）绝对失败、直接 exit 1；**平均分下降**（`successRate < budget`）可协商，因为可能只是新增了更难的用例。原因是平均值会**掩盖**回归：改坏 2 条并通过修好 5 条得到净 +3 看起来是好事，但那 2 条是**已经上线的功能**，代价远高于多修 5 条。

配套两点：①**历史基线锁**（把上一版 `pairKey → passed` 存成 lock 文件），否则"原本通过"没有依据；②**失败信息要能指向代码**——输出的 `pairKey`（`snap-single-source::r1::1`）配合任务表即可定位到具体断言。

</details>

---

## 7. 延伸阅读

- Agent Eval Lab 仓库 —— https://github.com/coolwkx/agent-eval-lab （本系列四篇的共同参考实现）
- Agent Eval Lab Hard 实验卡 —— https://github.com/coolwkx/agent-eval-lab/blob/main/docs/HARD_SUITE_EXPERIMENT_CARD.md （"能证明什么 / 不能证明什么"的写法范例）
- 大宗商品价格监控 Agent 项目复盘 —— [../07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md](../07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md)
- OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments —— https://arxiv.org/abs/2404.07972 （执行式判分与真实环境副作用）
- GAIA: A Benchmark for General AI Assistants —— https://arxiv.org/abs/2311.12983
- JSON Schema Draft 2020-12 发布说明 —— https://json-schema.org/draft/2020-12/release-notes （把用例定义写成可校验 Schema）
- Bootstrapping (statistics) —— https://en.wikipedia.org/wiki/Bootstrapping_(statistics) （cluster bootstrap 与重采样单位）
- GitHub Actions 工作流语法 —— https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions （`paths` 过滤、`if: always()`、artifact 上传）

---

[⬅️ 返回本章目录](README.md)
