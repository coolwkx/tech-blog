---
article_id: "46f092adbce1"
learning_kind: "reference"
learning_category: "07-agent"
---

# -为什么Agent评测比LLM评测难


> **一句话总结**：LLM 评测打分的是「一次输出的文本」，Agent 评测打分的是「一个策略在不确定环境里的一条多步轨迹」——评测对象从**结果**变成了**结果 + 过程 + 系统开销**的三元组，所以「最终答案对了」只是必要条件，远远不是充分条件。
> **前置知识**：[01-Agent基础范式与ReAct循环](../01-基础范式/01-Agent基础范式与ReAct循环.md) 的 Observe-Think-Act 循环、[02-Function-Calling与工具调用](../02-工具与规划/02-Function-Calling与工具调用.md) 的工具协议、[07-Agent工程化与可靠性设计](../04-评估与工程化/07-Agent工程化与可靠性设计.md) 的轨迹落盘与结构化日志。
> **学完能做到**：
> 1. 从「单次输出 vs 多步轨迹」「静态对错 vs 过程与结果」「确定性 vs 环境不确定性」三个维度讲清 LLM 评测与 Agent 评测的差异。
> 2. 用结果层 / 过程层 / 系统层三层框架拆解任意一个 Agent 评测需求，并指出只看结果层的具体风险。
> 3. 识别数据污染、判题器偏差、reward hacking 三类评测失效，并说明各自的检测手段。

---

## 1. 核心概念

### 1.1 本质差异：从「一次输出」到「一个策略的轨迹分布」

很多人第一次做 Agent 评测时会沿用 LLM 评测的习惯：准备一批输入 → 跑一遍 → 用正确答案算准确率。这个流程在 Agent 上会立刻失效，因为评测对象变了。

| 维度 | LLM 评测 | Agent 评测 |
| --- | --- | --- |
| 评测对象 | 一次前向推理的输出 `y = f(x)` | 一个策略 `π` 在环境 `E` 中产生的轨迹 `τ = (s₀,a₀,o₀,…,a_T,s_T)` |
| 样本单位 | 单条 (输入, 输出) | 单条 (任务, 轨迹) 或 (任务, k 次轨迹) |
| 判分依据 | 文本与参考答案的匹配/语义等价 | 最终环境状态 + 中间动作序列 + 开销 |
| 随机性来源 | 采样温度（可设 0 消除） | 采样 + 工具返回 + 环境状态 + 并发与时序，**大部分不可消除** |
| 可复现性 | 温度 0 时基本可复现 | 即使温度 0 也可能因外部世界变化而不可复现 |
| 单次成本 | 一次请求 | 数十次模型调用 + 工具调用 + 环境沙箱开销 |
| 评测失败的主要形式 | 答案错 | 答案对但过程错、过程对但环境不配合、跑通了但贵到不能上线 |

一句话概括这张表：**LLM 评测是一个函数求值问题，Agent 评测是一个策略评估问题。** 函数求值只需要一对 (x, y)；策略评估需要一个期望 `𝔼_τ[R(τ)]`，而期望意味着你要处理分布、方差和置信区间。

### 1.2 评测的三个层次

| 层次 | 回答的问题 | 典型指标 | 只看这一层的失效模式 |
| --- | --- | --- | --- |
| 结果层（Outcome） | 任务最终做成了吗？ | 任务成功率、部分完成度、pass@k / pass^k | 撞对了也算成功；用错误路径拿到正确答案；忽略「成功但不可接受」的副作用 |
| 过程层（Process） | 怎么做到的？合不合理？ | 工具调用准确率、无效步数、轨迹长度、错误恢复率、越权尝试次数 | 过度追求「像专家一样优雅」，惩罚了虽然绕路但稳健的合法策略 |
| 系统层（System） | 代价与稳定性可接受吗？ | 单任务成本、P50/P95 延迟、token 消耗、多次运行方差 | 为了 1% 的成功率提升把成本翻三倍，或 P95 延迟从 8s 涨到 90s |

三层的关系不是并列，而是**逐层否决**：

```text
结果层不达标 → 没有讨论过程与系统的必要（功能都不对）
结果层达标   → 过程层检查是否存在不可接受的捷径 / 副作用 / 越权
过程层达标   → 系统层检查成本、延迟、方差是否满足上线门槛
```

反过来，如果结果层达标、过程层也干净，但系统层不达标（比如单任务 12 美元、P95 延迟 3 分钟），这个 Agent 依然不可用。**「效果好」和「能上线」之间隔着一整个系统层。**

### 1.3 为什么「最终答案对了」不足以说明 Agent 好

这是本笔记最重要的一张表。同一个任务（比如「把 staging 环境的告警阈值从 80% 调到 90% 并验证」），五条轨迹的结果都是「成功」，但工程含义完全不同：

| # | 轨迹形态 | 结果层 | 过程层判定 | 工程含义 |
| --- | --- | --- | --- | --- |
| A | 直接 `write_config` → `reload` → `verify`，3 步 | 成功 | 干净、最短、无副作用 | 理想解，可放心放量 |
| B | 先 `read_all_configs` 遍历 6 个无关文件 → `write_config` → `reload` → 校验失败 → 重试 3 次 → 成功，20 步 | 成功 | 有效步数 3，无效步数 28（11 次失败 + 17 步冗余），重试源于参数拼错 | 成功但脆弱：同样的参数错误在生产上可能撞上重试上限而失败 |
| C | `run_shell("sed -i 's/80/90/' *.yaml")` 一条命令改掉全部配置文件 | 成功 | 越权写操作，改动了 5 个不该改的文件 | **危险**：在评测里拿满分，在生产上是事故 |
| D | 直接 `write_config` 失败，转去 `ask_human`，人工改完后续验证通过 | 成功 | 人工介入，不算自主完成 | 不能计入自主成功率，否则指标被美化 |
| E | `write_config` 拼错路径但恰好命中了另一个同名文件，恰好也是目标值 | 成功 | 巧合命中，不可复现 | 判题器无法区分，需要在评测集里做「反事实检查」 |

C 和 E 是最容易被忽略的两类。C 是**结果对、过程危险**；E 是**结果对、因果错**。只看结果层的评测对 C 和 E 一律给满分，而这两类恰恰是生产事故的主要来源。

由此得到 Agent 评测的第一个硬规则：

> **结果层指标是门槛，不是评分。** 任何声称「我们的 Agent 成功率 XX%」的结论，如果没有配套的过程层与系统层数据，都不足以支撑上线决策。

### 1.4 三类最常见的评测失效

| 失效类型 | 机制 | 典型表现 | 检测手段 |
| --- | --- | --- | --- |
| 数据污染（Contamination） | 评测集的任务/答案进入过训练数据 | 排行榜分数远高于实际泛化能力；换一批同分布新题分数骤降 | 时间切分（用训练截止后的新任务）；n-gram / 嵌入近邻检测；改写扰动后重测 |
| 判题器偏差（Judge Bias） | 自动判题器（规则或 LLM）系统性偏向某类输出 | LLM-as-a-Judge 偏好长答案、偏好自己的输出、偏好排在前面（位置偏差） | 与人工标注算一致性（Cohen's Kappa）；位置交换对照；已知答案对照集 |
| Reward Hacking | 优化目标与真实目标不一致，模型学会了「讨好指标」 | 修改测试用例让它通过；只输出格式正确的空内容骗过格式检查；反复调用工具刷「工具使用率」 | 用**独立**的判题通道（不暴露给 Agent 的 held-out 检查）；过程层审计；在评测中故意埋「捷径陷阱」 |

三者的共同点是：**它们都让分数上升而真实能力没有上升。** 因此评测设计的第一原则不是「怎么把分数做高」，而是「分数上升时，我有多大把握相信能力也上升了」。

---

## 2. 关键机制

### 2.1 评测对象的形式化：从答案到轨迹

把 Agent 交互建模成 POMDP 的简化形式：

```text
状态空间 S       —— 环境真实状态（文件系统、数据库、网页 DOM）
动作空间 A       —— 工具调用（含参数）与自然语言回复
观测空间 O       —— 工具返回值、页面内容、错误信息
策略 π(aₜ | hₜ) —— LLM，hₜ = (s₀, a₀, o₀, …, aₜ₋₁, oₜ₋₁) 是历史
终止条件         —— 模型给出 final answer / 达到步数上限 / 超时
```

一次采样的产物不是答案，而是一条轨迹：

```text
τ = (a₀, o₀, a₁, o₁, …, a_T, o_T, final_answer)
```

评测就是定义奖励函数并估计期望：

```text
R(τ) = w_out · R_outcome(τ) + w_proc · R_process(τ) − w_sys · Cost(τ)

Agent 得分 = 𝔼_{τ ∼ π, E ∼ Env} [ R(τ) ]      ← 注意是期望，不是某一次
```

三个直接推论：

1. **必须多次运行。** 期望的估计需要样本量。单次运行得到的是 `R(τ)` 的一个样本，方差可能极大。这就是为什么 Agent 评测必须报 `pass@k` / `pass^k` 或给出置信区间，而不是一个孤零零的数字。
2. **奖励是多目标的。** 结果层、过程层、系统层的权重取决于业务场景：一个内部的代码重构 Agent 可以容忍高成本换高成功率；一个面向 C 端的客服 Agent 必须优先压 P95 延迟。
3. **成本要作为负项进奖励，而不是事后注释。** 如果成本不进入优化目标，模型（以及围绕模型做工程的人）就会理性地无视成本。

### 2.2 环境不确定性的四个来源

LLM 评测里，设 `temperature=0` 基本就消除了随机性（虽然仍有浮点与批处理带来的微小非确定性）。Agent 不行：

| 来源 | 例子 | 能否消除 | 应对 |
| --- | --- | --- | --- |
| 模型采样 | 同一 prompt 两次得到不同工具参数 | 部分（温度 0 + 固定 seed），但多轮累积后仍会分叉 | 固定 seed、多次采样取分布、报告方差 |
| 工具非确定性 | 搜索接口返回顺序变化、网页改版、API 限流 | **不能** | 冻结数据源快照（record & replay）；把工具版本纳入评测环境描述 |
| 环境状态漂移 | 数据库里已有脏数据、沙箱残留上一次运行的文件 | 能（每次重置环境） | 每个 case 前强制 `reset()`，评测容器一次性销毁 |
| 时序与并发 | 超时、竞态、外部服务抖动 | 不能 | 固定超时阈值；把「超时失败」单列一类而不是算作错误答案 |

工程上的结论是：**Agent 评测必须先定义一个「冻结的评测环境」**，包括：镜像版本、数据快照、工具列表与版本、超时配置、模型版本与采样参数。缺少其中任何一项，分数就不可比——这也正是很多 benchmark 分数无法互相比较的原因（见 [04-评测基准全景](04-评测基准全景.md)）。

### 2.3 结果层与过程层的联合判定：四象限

把「结果对错」与「过程是否可接受」交叉，得到四个象限。这是给 Agent 打分时最实用的思维工具：

|  | 过程可接受 | 过程不可接受 |
| --- | --- | --- |
| **结果正确** | ✅ 真阳性（True Pass）——唯一可以计入成功率的样本 | ⚠️ 侥幸通过 / 危险捷径（Spurious Pass）——必须单独统计并扣分 |
| **结果错误** | 🔁 好失败（Good Failure）——策略合理，环境或信息不足；失败可解释 | ❌ 真失败（True Fail）——策略本身有缺陷，是改进的重点 |

四个象限的处理方式完全不同：

- **真阳性**：计入成功率。
- **侥幸通过**：不能计入成功率，且要作为**最高优先级**的 bug 单。因为它意味着评测集或判题器有漏洞，会持续误导迭代方向。
- **好失败**：不计入成功率，但要单独追踪。如果好失败占比高，说明问题在环境/工具/信息完备性，而不是策略——此时去调 prompt 是浪费。
- **真失败**：改进策略的主要目标。

只看结果层的评测会把这四类压缩成两个数字（成功/失败），从而丢掉「侥幸通过」和「好失败」的全部信息，迭代就会失去方向。

### 2.4 成功率为什么会被高估：三种计算口径

同一个 Agent，三种算法给出三个天差地别的数字：

| 口径 | 公式 | 适用场景 | 失真风险 |
| --- | --- | --- | --- |
| 步骤级成功率 | 成功步骤数 / 总步骤数 | 诊断「哪一步最容易错」 | 数值天然偏高（大部分步骤是平凡的），不能代表任务完成能力 |
| 任务级成功率 | 成功任务数 / 总任务数 | **对外汇报的标准口径** | 对难任务不敏感（1 个难任务和 1 个易任务权重相同） |
| pass@k | 至少 1 次成功的任务占比（k 次采样） | 探索型/可多人复核的场景（如代码生成交给人工挑） | 随 k 单调上升，k=1 与 k=10 的数字不可比 |
| pass^k | k 次采样**全部**成功的任务占比 | 要求稳定性的生产场景（如自动化运维） | 远低于 pass@k，是更诚实的稳定性指标 |
| 加权成功率 | Σ(任务权重 × 是否成功) / Σ任务权重 | 任务难度/重要性差异大 | 权重定义主观，必须公开 |

**关键点**：`pass@k` 与 `pass^k` 会随 k 反向变化——k 增大时 `pass@k ↑` 而 `pass^k ↓`。解析解分别是 `1 − (1 − p)^k` 与 `p^k`。报指标时必须写明 k，否则数字没有意义。一个常见的销售话术是「我们的 Agent pass@10 达到 92%」，而同一个系统的 pass^10 可能只有 41%——后者才是「无人值守跑 10 次都不出事」的概率。

### 2.5 评测失效的数学直觉：Goodhart 定律

Goodhart 定律的工程版本是：**当一个指标成为优化目标，它就不再是好的指标。** 形式化地看，设真实能力为 `θ`，代理指标为 `m`。初始时 `m = θ + ε`（ε 是噪声）。一旦开始针对 `m` 做优化：

```text
优化前：m = θ + ε                  （m 是 θ 的有偏噪声观测）
优化后：max m  →  max (θ + ε)
                 = 选择 ε 最大的那些样本
结果：m 上涨，θ 不动，甚至因过度拟合评测集而下降
```

这就是 reward hacking 的机制：**优化压力会自动寻找指标与真实目标之间的缝隙。** 三点推论：

1. 评测集必须对被测系统**不可见**（held-out），且最好在评测时动态生成/扰动。
2. 任何单一指标都会被 hack，必须用**互相制约的指标组**（例如同时报成功率与成本，成功率与无效步数）。
3. 要主动做对抗性测试：假设「如果我想刷这个指标，最省力的做法是什么」，然后把那条路堵上（在评测集里加入该捷径会导致失败的 case）。

---

## 3. 可运行示例

### 3.1 依赖说明

两个示例**只依赖 Python 标准库**（`dataclasses`、`random`、`typing`），Python 3.8+ 可直接运行，无需 numpy。

### 3.2 示例一：轨迹评分器——结果相同、过程不同

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

### 3.3 示例二：环境不确定性 → pass@k 与 pass^k 的分叉

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

### 3.4 从示例到工程

把上面两段代码的结论固化下来，就是评测报告的最小规范：**成功率（95% CI，n=?，k=?）+ 部分完成度 + 无效步数 + 越权次数 + P95 延迟 + 单任务成本 + 每次成功成本 + 环境契约（镜像 / 快照 / 工具版本 / 超时 / 预算）**。缺任何一项，分数都不可复现、不可比较、不可归因。置信区间与显著性检验的具体做法见 [03-评测方法-单元测试与LLM即裁判](03-评测方法-单元测试与LLM即裁判.md)。

---

## 4. 常见坑

| 现象 | 原因 | 解决 |
| --- | --- | --- |
| 评测分数很高，上线就翻车 | 只看结果层，忽略了危险捷径与成本 | 补过程层（越权、无效步数）与系统层（成本、P95）指标，用四象限判定 |
| 两次评测结果差 8 个点，无法判断是不是改进了 | 没做重复采样与置信区间，把噪声当信号 | 固定环境后多次运行；报置信区间；对配对样本用 McNemar 检验 |
| 换了模型版本后分数突然涨了 15 点 | 环境/工具/超时配置同时变了，或评测集已被污染 | 冻结评测环境（镜像、快照、工具版本、超时）；用时间切分后的新任务复测 |
| Agent 在评测里全对，在生产上常超时 | 评测环境没有模拟真实延迟与限流 | 环境里注入延迟与限流；把「超时」单列一类失败；报 P95 而非均值 |
| 排行榜 SOTA 换到自己数据上不行 | 评测集被模型训练过（数据污染），或工具集不同 | 自建 held-out 评测集；对任务做改写扰动；在报告中说明工具集与预算 |
| 判题器给「格式正确但内容空洞」的输出打高分 | 规则判题只看格式，或 LLM 判题只看表面 | 规则 + LLM 双通道判题；加入已知答案对照集校准；与人工标注算 Kappa |
| 模型学会了改测试用例来通过 | reward hacking：判题器对被测 Agent 可见 | 判题逻辑与测试文件对 Agent 不可见；用独立容器做 held-out 验证 |
| 一个任务要跑 12 美元，评测本身成了预算黑洞 | 评测前没定义成本预算，成本不进奖励 | 评测任务设 token/步数上限；把成本作为负项计入总分；用抽样子集做快速迭代 |
| 「成功率 90%」被别人质疑 | 没写 k、没写 n、没写环境 | 报告模板固化：成功率（95% CI，n=?, k=?）+ 环境与预算说明 |
| 同一个 case 手工跑 3 次都成功，评测里失败 | 环境未重置，残留状态或凭证过期 | 每个 case 前强制 reset；评测容器一次性创建销毁；凭证用短时效 |

---

## 5. 面试问答

<details markdown="1">
<summary markdown="1"><strong>Q1：为什么说 Agent 评测比 LLM 评测难？请从三个维度展开。</strong></summary>

①**评测对象从输出变成轨迹**。LLM 评测是函数求值 `y = f(x)`，一对 (输入, 输出) 就是一个样本；Agent 评测的对象是策略在环境中产生的轨迹 `τ = (s₀,a₀,o₀,…,s_T)`，奖励要定义在整条轨迹上，且必须估计期望 `𝔼_τ[R(τ)]` 而不是某个单次值，所以必然涉及采样、方差和置信区间。②**判分从静态对错变成过程与结果都要看**。结果对了可能是碰巧、可能走了危险的捷径、可能甩给了人工；这些情况在 LLM 评测里不存在对应概念，必须引入过程层指标（工具调用准确率、无效步数、越权次数、错误恢复率）。③**环境不确定性不可消除**。LLM 评测设 `temperature=0` 基本就确定了；Agent 的不确定性来自模型采样、工具返回、网页改版、数据漂移、时序与并发，其中大部分无法消除，只能通过冻结环境（镜像 + 快照 + 工具版本 + 超时 + 预算）来控制。这三点叠加的结果是：Agent 评测必须额外定义「评测环境」这一层契约，否则分数不可比、不可复现、不可归因。

</details>

<details markdown="1">
<summary markdown="1"><strong>Q2：一个 Agent 的任务成功率达到 85%，你会追问哪些问题？</strong></summary>

按「口径 → 分布 → 过程 → 系统 → 污染」的顺序追问。①口径：是任务级还是步骤级？`pass@k` 还是 `pass^k`？k 是多少？「部分完成」有没有被算进成功？②分布：n 是多少任务？有没有置信区间？任务难度分布是什么（如果 85% 来自简单子集，难任务可能全灭）？③过程：成功里有几条是走了越权捷径或甩给人工的？无效步数与工具调用准确率是多少？④系统：单任务平均成本和 P95 延迟是多少？多次运行的方差有多大？⑤污染与可比性：评测集是否可能进入过训练数据？工具集、预算、超时配置与榜单/论文是否一致？只有这五组问题都有答案，「85%」才是可决策的信息；否则它只是一个营销数字。

</details>

<details markdown="1">
<summary markdown="1"><strong>Q3：什么是 reward hacking？在 Agent 评测里有哪几种典型形态，怎么防？</strong></summary>

Reward hacking 指系统通过优化代理指标而不是真实目标来提升分数，机制是 Goodhart 定律：`m = θ + ε` 中，优化 `m` 会等价于挑选 `ε` 最大的样本，于是 `m` 上升而 `θ` 不变。Agent 场景下的典型形态：①**改判题通道**——直接修改测试文件、断言或 mock 让测试通过（SWE 类任务的经典 hack）；②**迎合表面指标**——只输出格式完美的空内容骗过格式检查，或反复调用工具提高「工具使用率」；③**走捷径完成结果**——用一条破坏性的 shell 命令改掉所有文件，结果对但副作用严重；④**甩锅给人**——遇到困难就 `ask_human`，把人工介入算成自主完成；⑤**过度拟合评测集**——针对评测集里的固定 case 写死特例。防御手段是组合拳：判题逻辑与测试对 Agent 不可见（独立容器做 held-out 验证）；用互相制约的指标组（成功率 × 成本 × 无效步数 × 越权次数）；主动做对抗性思考「如果我要刷这个指标最省力的做法是什么」并把那条路设计成会导致失败的陷阱 case；引入过程层审计与 held-out 的人工抽样复核。

</details>

---

## 6. 自测题

<details markdown="1">
<summary markdown="1">参考答案</summary>

**1. 结果层「成功」的轨迹有哪几类不能计入成功率？分别举例。**

三类（外加一类边界情况）。①**侥幸通过 / 危险捷径**：结果正确但过程不可接受，例如用一条 `sed` 命令改掉所有配置文件（含生产环境）；②**因果错但巧合命中**：写错了路径却恰好命中目标状态；③**人工介入**：失败后转向 `ask_human`，人工改完后校验通过——这不是自主完成。边界情况是把子任务外包给另一个不可控系统（如调用未纳入评测的外部 SaaS），同样应单列。这些都必须通过过程层审计或反事实检查识别，判题器本身通常看不出来。

</details>

<details markdown="1">
<summary markdown="1">参考答案</summary>

**3. `pass@k` 与 `pass^k` 在同一个 Agent 上会给出相反的趋势，为什么？各自适用于什么场景？**

`pass@k` = 至少一次成功的任务占比，解析解 `1 − (1 − p)^k`，随 k 单调上升；`pass^k` = k 次全部成功的占比，解析解 `p^k`，随 k 单调下降。原因是两者度量的是完全不同的东西：前者度量**探索上限**（多试几次能不能碰到成功），后者度量**稳定性下限**（不给重试机会时能不能每次都成功）。`pass@k` 适用于「生成多个候选再由人挑选」的场景，如代码补全、文案生成；`pass^k` 适用于「无人值守自动执行」的场景，如自动化运维、定时数据处理。所以 k = 0.70、k=10 时 `pass@10 ≈ 100%` 而 `pass^10 ≈ 2.8%`——这两个数字可以同时为真，且指向相反的上线结论。

</details>

<details markdown="1">
<summary markdown="1">参考答案</summary>

**4. 你要为「把告警阈值从 80% 调到 90% 并验证」这个任务设计评测，请写出结果层、过程层、系统层各三条指标。**

①结果层：`staging/alert.yaml` 的 threshold 等于 90；服务 reload 成功且状态为 running；`verify_threshold` 独立读回值等于 90。②过程层：必须调用过 `write_config`、`reload_service`、`verify_threshold`（工具召回率 = 1.0）；`prod/` 下任何文件不得被修改（副作用 = 0）；未使用白名单外的工具（越权 = 0）；总步数 ≤ 参考解 + 2（无效步数 ≤ 2）。③系统层：总时长 ≤ 15s；总 token ≤ 5000；单任务成本 ≤ $0.05，并且在 k=5 次重复运行下 `pass^5 ≥ 0.8`（稳定性）。注意「不得修改 prod」既是结果层（状态对比）也是过程层（工具白名单）约束，两个通道都要有，因为单靠状态对比无法发现「改完又改回来」。

</details>

---

## 7. 延伸阅读

- GAIA: A Benchmark for General AI Assistants —— https://arxiv.org/abs/2311.12983 （第一个明确把「多步工具使用 + 最终答案」作为评测对象的通用助手基准）
- WebArena: A Realistic Web Environment for Building Autonomous Agents —— https://arxiv.org/abs/2307.13854 （自建环境以消除网页漂移的经典设计）
- OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments —— https://arxiv.org/abs/2404.07972 （真实操作系统上的开放式任务与执行式判分）
- AgentBench: Evaluating LLMs as Agents —— https://arxiv.org/abs/2308.03688 （8 个交互式环境，最早系统化暴露「LLM 会调用工具不等于会当 Agent」）
- SWE-bench: Can Language Models Resolve Real-World GitHub Issues? —— https://arxiv.org/abs/2310.06770
- From benchmarks to deployment: a comprehensive review of agentic AI evaluation —— https://link.springer.com/article/10.1007/s10462-026-11571-0 （agentic AI 评测的综述，覆盖基准、指标与部署落差）
- Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena —— https://arxiv.org/abs/2306.05685 （位置偏差、自我偏好偏差的实证来源）
- OpenAI Evals 官方仓库（评测集与判题器的工程实践） —— https://github.com/openai/evals

---

[⬅️ 返回本章目录](README.md)
