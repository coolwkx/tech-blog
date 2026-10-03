> **一句话总结**：评测方法的选择顺序是**先确定性、后模糊**——凡是终态可断言、产物可校验的一律用单元测试式判题，只有「没有唯一正确答案」的输出才交给 LLM-as-a-Judge，而 Judge 自己必须先与人工标注对齐（Cohen's Kappa）并接受显著性检验（McNemar / Bootstrap）才算合格。
> **前置知识**：[01-为什么Agent评测比LLM评测难](01-为什么Agent评测比LLM评测难.md) 的三层评测与四象限、[02-评测指标设计](02-评测指标设计.md) 的口径固定与 `pass@k` / `pass^k`。
> **学完能做到**：
> 1. 把一项 Agent 能力拆成「输入与环境 + 允许工具 + 终态/序列/产物断言」的可执行用例，并写成一个可复用的评测 harness。
> 2. 设计一份带行为锚点的评分 rubric，识别并缓解 Judge 的位置偏差、长度偏差与自我偏好偏差。
> 3. 用 Cohen's Kappa 验证 Judge 与人工的一致性，用 McNemar 精确检验与配对 Bootstrap 判断 A/B 差异是否显著。

---

## 1. 核心概念

### 1.1 单元测试式评测：把能力拆成可断言用例

Agent 评测最常见的工程化路径，就是把它变成软件工程里最成熟的实践：**单元测试**——把「Agent 是否具备某项能力」翻译成「给定初始环境与任务描述，运行结束后环境是否满足断言」。

| 用例字段 | 含义 | 为什么必须有 |
| --- | --- | --- |
| `case_id` | 稳定标识 | 多次运行结果要能逐条配对比较（McNemar 的前提） |
| 输入与初始环境 | 任务描述 + 环境快照（文件、数据库、页面状态） | 环境是评测的一部分；不固定就无法复现 |
| 工具白名单 | 允许的工具（名称 + 版本 + 权限范围） | 越权检测依据；也是分数可比性的前提 |
| 必须调用的工具 | 关键工具集（序列断言用） | 捕捉「结果对但没走该走的路」 |
| 期望终态 | 键值对形式的可比对状态 | 结果层判分的直接依据 |
| 超时与预算 | `max_steps`、`timeout_s`、`budget_usd` | 系统层门槛，兼防无限循环烧钱 |

三类断言，按可靠性从高到低：

| 断言类型 | 断言方式 | 可靠性 | 典型场景 |
| --- | --- | --- | --- |
| 终态断言 | 对比运行后的环境状态与期望状态 | **最高**（确定性、与路径无关） | 改配置、建表、写文件、下单成功 |
| 序列断言 | 关键工具**被调用过**；白名单外工具**未被调用** | 中（对合法多解敏感） | 必须先查再改、必须调用校验工具 |
| 产物断言 | 校验生成物：文件内容、返回值结构、编译通过、测试通过 | 高（若有可执行验证器） | 代码生成、报告生成、结构化输出 |

**关键取舍：序列断言要用「包含 / 不包含」而不是「严格全序」。** 同一个目标通常有多条合法路径，写成严格全序会把合法解判为失败，把评测变成「猜参考解」。只有确实存在强制顺序时才用全序（例如「必须先备份再删除」）。

### 1.2 确定性判题 vs 模糊判题的适用边界

| 输出形态 | 判题方式 | 理由 | 示例 |
| --- | --- | --- | --- |
| 代码执行结果 | 确定性（跑测试） | 有唯一可执行的验证器 | SWE 类任务的 `FAIL_TO_PASS` |
| 环境/文件/数据库状态 | 确定性（状态对比） | 可直接读回并比对 | 配置值、表结构、订单状态 |
| API / 工具返回值 | 确定性（结构 + 值断言） | schema 与取值可校验 | JSON 字段、状态码、错误类型 |
| 检索 / 排序结果 | 确定性（Recall@k、MRR） | 有 gold 集合可比 | RAG 检索评测（见 [05](05-RAG与多轮对话评测.md)） |
| 开放式长文 | **模糊**（Judge 或人工） | 无唯一正确答案 | 摘要、报告、解释 |
| 多轮共情与澄清质量 | **模糊** | 与上下文强耦合 | 对话策略评估 |

判据可以写成一句话：**如果两个有经验的工程师对「通过与否」会给出不同结论，就不是确定性问题。** 这类输出不要硬写成规则——硬写的规则一定在边界上出错，而且错得隐蔽（例如用关键词命中当通过条件，模型学会堆关键词就能刷分）。因此实用策略是**分层判题**，把 Judge 的使用面积压到最小：

```text
第一层：确定性前置校验（必须全部通过，否则直接 fail）
        - 输出可解析（JSON / 代码语法 / 必填字段）；无越权、无超预算
第二层：确定性终态 / 产物断言（有 gold 时优先）→ 通过则直接判 pass
第三层：模糊判题（仅对没有唯一答案的维度）
        - 用 rubric + LLM-as-a-Judge，分数经校准后映射为 pass/fail
```

### 1.3 LLM-as-a-Judge 完整设计

rubric 的质量决定 Judge 的上限。四个必要成分：**明确且互不重叠的评分维度**（不是笼统的「回答质量」）；**行为化锚点**（每档写可观察行为而非形容词，例如「4 分：所有事实陈述都能在资料中找到原文依据」）；**分值与升降档边界**（例如「有任一事实性错误即不高于 2 分」）；以及**先输出理由再输出分数**。第四点常被忽略：生成理由时会「锁定」判断，反之先给分数再补理由，理由会变成对分数的合理化（post-hoc rationalization）。

一个 4 档 rubric 示例（基于给定资料的问答）：

| 档位 | 事实正确性 | 引用与依据 | 切题程度 |
| --- | --- | --- | --- |
| 4 优秀 | 全部事实陈述正确 | 关键结论都能对应到资料原文 | 直接回答，无冗余铺垫 |
| 2 及格 | 1 处影响结论的错误 | 主要结论缺少资料支撑 | 部分回答，需读者自行推断 |
| 1 不及格 | ≥2 处影响结论的错误，或编造资料中不存在的信息 | 结论主要来自模型自身知识 | 未回答所问，或答非所问 |

few-shot 校准的要点：给 1-3 个示例，且**必须覆盖边界档，而不只是满分档**。示例全是 4 分时，Judge 会倾向给所有答案高分；给出一个「看起来很长但事实错误 → 2 分」的例子，Judge 才知道长不等于好。建议组合：4 分（说明为何每处结论都有依据）、2 分（**长且有文采但有一处关键事实错误** → 降档）、3 分（边界案例）。第二个示例是校准核心，它同时压制长度偏差并教会 Judge「错误优先于风格」。

三类偏差与缓解手段：

| 偏差 | 机制 | 缓解手段 |
| --- | --- | --- |
| 位置偏差 | Judge 对候选项出现顺序敏感，pairwise 比较时倾向先出现的那个 | 交换 A/B 位置各评一次，取**一致**结论；不一致记为平局 |
| 长度偏差 | 训练数据中详细的长答案更常被评为好 | rubric 显式声明长度不计分；few-shot 放入「长但错误 → 低分」示例；对长度做分层分析 |
| 自我偏好 | 模型识别出与自身风格相似的输出 | 用**不同族**模型做裁判；或对同族结果单独标注并报告 |

另两点实操经验：**绝对评分**能回避位置偏差，但会引入分数尺度漂移（同一段文本在不同批次得分不同），需定期用固定锚点样本重校准；**Judge 模型不应与被测模型相同**，否则自我偏好与能力盲区会叠加。

---

## 2. 关键机制

### 2.1 Judge 可靠性验证：Cohen's Kappa

**为什么不能只看准确率。** 设 100 条样本中 90 条的正确答案是「通过」。一个把所有输出都判为「通过」的懒惰 Judge 准确率是 90%，看起来很好，但它没有任何判别能力——准确率在类别不平衡时会严重虚高。Cohen's Kappa 通过**扣除随机一致的期望**来修正：

```text
1) 观察一致率 p_o = 两者判定相同的样本数 / n
2) 随机一致率 p_e（假设两者独立，用各自边际分布估计）
   对每个类别 c：Judge 判 c 的比例 p_c(J)，人工判 c 的比例 p_c(H)
   独立时恰好都判 c 的概率 = p_c(J) × p_c(H)，故 p_e = Σ_c p_c(J) × p_c(H)
3) κ = (p_o − p_e) / (1 − p_e)
   分子是「实际超出随机一致的部分」，分母是「随机一致之外还剩多少空间」
```

回到懒惰 Judge（90 条该判「通过」的全部判「通过」）：`p_o = 0.90`，`p_e = 1.00 × 0.90 + 0.00 × 0.10 = 0.90`，于是 `κ = (0.90 − 0.90)/(1 − 0.90) = 0`——**准确率 90%，判别能力为 0**。

| Kappa | 一致性强度 | 是否可用于正式评测 |
| --- | --- | --- |
| 0.00 – 0.20 | 轻微 | 不可用 |
| 0.21 – 0.40 | 尚可 | 仅可粗筛（召回明显错误） |
| 0.41 – 0.60 | 中等 | 可用于内部迭代，不建议对外 |
| 0.61 – 0.80 | 显著 | 可用于正式评测 |
| 0.81 – 1.00 | 几乎完全一致 | 可替代人工（仍建议抽检） |

Kappa 的已知局限：某类别极稀少时 `p_e` 接近 1，Kappa 不稳定甚至为负。因此**报告时应同时给出 `p_o`、`p_e`、`κ` 与混淆矩阵**，让读者判断 Kappa 低是因为 Judge 差，还是类别分布极端。

### 2.2 用已知答案的对照集校准 Judge

| 分组 | 占比建议 | 内容 | 检验目标 |
| --- | --- | --- | --- |
| 明显正确 | ~30% | 标准答案 | Judge 是否会给低分（假阴性） |
| 明显错误 | ~30% | 含事实错误、答非所问 | Judge 是否能识别（假阳性） |
| 边界案例 | ~30% | 部分正确、风格怪异但正确、啰嗦但不犯错 | Judge 与人工的差异集中区 |
| 对抗样本 | ~10% | 格式完美但空洞；很长但错误；正确但极短 | 检验长度偏差与格式偏差 |

对抗样本是最有价值的部分：它们专门为「Judge 容易上当」而设计。若 Judge 给「格式完美但内容空洞」打高分，说明 rubric 需要加「空洞内容判低分」的锚点。校准通过建议标准：`κ ≥ 0.6` 且「明显正确组」假阴性率 < 5%；未达标就回去改 rubric 与 few-shot，而不是直接上线。

### 2.3 显著性检验一：McNemar 检验

**为什么不能用两个独立比例检验。** A 与 B 跑的是**同一批任务**，属于配对数据。任务难度是共同变量：两者都会在同一个难任务上失败。独立比例检验（如两比例 z 检验）假设两组样本独立，会**高估方差**，从而低估显著性，把真实改进误判为「无差异」。McNemar 只看**不一致**的两格：

|  | B 通过 | B 失败 |
| --- | --- | --- |
| **A 通过** | a（都通过） | b（A 过 B 挂） |
| **A 失败** | c（A 挂 B 过） | d（都失败） |

`a` 与 `d` 是一致格，对「A 与 B 是否有差异」不提供信息；只有 `b` 与 `c` 携带差异信号，因此检验只基于 `b + c`：

```text
H0：A 与 B 能力相同 ⇒ 在不一致的样本中，b 与 c 期望各占一半
大样本用连续性校正的卡方：χ² = (|b − c| − 1)² / (b + c)，df = 1
小样本用精确二项检验（推荐默认）：
    p = 2 × Σ_{i=0}^{min(b,c)} C(b+c, i) × 0.5^(b+c)，最后取 min(1, p) 截断
```

经验阈值：`b + c < 25` 时用精确检验，否则两者差别不大。精确检验无需近似，在评测集只有几十个任务时（Agent 评测的常态）更可靠。

### 2.4 显著性检验二：配对 Bootstrap 置信区间

McNemar 回答「差异是否显著」，Bootstrap 回答「差异有多大、区间是多少」：

```text
1) 每个任务表示成一对 (outcome_A_i, outcome_B_i)，i = 1..n，取值 0/1
2) 重复 B 次（通常 10000 次）：
   a) 从任务索引 0..n-1 中有放回抽 n 个索引
   b) 用同一批索引同时取 A 和 B 的结果（「配对」的关键）
   c) 计算 Δ* = mean(B*) − mean(A*)
3) 把 B 个 Δ* 排序，取第 2.5 与 97.5 百分位作为 95% CI
4) CI 不包含 0 则差异在 5% 水平上显著
```

三个必须说清的点：①**重采样单位是任务**，不是步骤、不是采样次数——任务内部的多个步骤高度相关，按步骤重采样会打破相关性，得到过窄的区间（假显著）；②**配对重采样（同一批索引）能大幅降方差**，因为任务难度的共同波动被抵消；③非配对 Bootstrap 也能用但区间更宽，只有在 A、B 任务集不完全相同时才必须用它（此时要在共同子集上比较，见 [04](04-评测基准全景.md) 的可比性诊断）。

### 2.5 完整评测流程

```text
① 定义能力与任务：从生产日志抽样、标注类别与难度，每类 ≥30 条；
   写清环境契约（镜像 / 快照 / 工具集与版本 / 超时 / 预算）
② 写用例：输入 + 初始环境 + 工具白名单 + 三类断言
   终态断言优先；序列断言用包含/不包含；产物断言接可执行验证器
③ 跑评测：固定 seed，每个 case 前 reset 环境，记录完整轨迹
   （工具名、参数、返回值、耗时、token、成本）；同一批任务上跑所有待比较版本
④ 分层判题：确定性前置校验 → 确定性终态/产物断言 → LLM-as-a-Judge
⑤ 验证 Judge：金标签对照集上算 Kappa（< 0.6 就改 rubric）；
   抽 50-100 条与人工比对，检查位置/长度/自我偏好偏差
⑥ 显著性：统计 b 与 c；McNemar 精确检验得 p 值；配对 Bootstrap 得差值 95% CI；
   两者结论一致才下「有显著改进」的结论，不一致时增大样本量
⑦ 报告与门禁：成功率（95% CI，n，k）+ 每次成功成本 + P95 延迟 + 越权次数；
   过程与安全指标设为上线门禁，而不只是观察指标
```

---

## 3. 可运行示例

### 3.1 依赖说明

两个示例**只依赖 Python 标准库**（`math`、`random`、`typing`）。精确二项检验用 `math.comb` 实现，不依赖 scipy。

### 3.2 示例一：单元测试式评测 harness
```python
"""单元测试式 Agent 评测 harness（最小可用版）：五类断言。

依赖：仅标准库。用例与运行结果都用 dict 表示，便于序列化到 JSON。
"""

from typing import Callable, Dict, List, Sequence


def assert_final_state(case: Dict, run: Dict) -> Dict:
    """结果层：终态是否满足期望（确定性）。"""
    bad = {k: (w, run["final_state"].get(k))
           for k, w in case["expected_state"].items()
           if run["final_state"].get(k) != w}
    return {"name": "final_state", "passed": not bad,
            "detail": "" if not bad else "不匹配 %s" % bad}


def assert_no_side_effects(case: Dict, run: Dict) -> Dict:
    """结果层：期望之外的既有状态是否被改动。"""
    changed = [k for k, v in case["initial_state"].items()
               if k not in case["expected_state"]
               and run["final_state"].get(k) != v]
    return {"name": "no_side_effects", "passed": not changed,
            "detail": "" if not changed else "被改动 %s" % changed}


def assert_required_tools(case: Dict, run: Dict) -> Dict:
    """过程层：必须调用的工具是否都出现过。"""
    missing = sorted(set(case["required_tools"]) - set(run["tools"]))
    return {"name": "required_tools", "passed": not missing,
            "detail": "" if not missing else "漏调 %s" % missing}


def assert_no_violation(case: Dict, run: Dict) -> Dict:
    """过程/安全层：是否用了白名单之外的工具。"""
    illegal = sorted(set(run["tools"]) - set(case["allowed_tools"]))
    return {"name": "no_violation", "passed": not illegal,
            "detail": "" if not illegal else "越权工具 %s" % illegal}


def assert_budget(case: Dict, run: Dict) -> Dict:
    """系统层：步数与成本是否在预算内。"""
    ok = (len(run["tools"]) <= case["max_steps"]
          and run["cost_usd"] <= case["budget_usd"])
    return {"name": "budget", "passed": ok,
            "detail": "" if ok else "steps=%d cost=%.4f"
                      % (len(run["tools"]), run["cost_usd"])}


ASSERTIONS: Sequence[Callable[[Dict, Dict], Dict]] = (
    assert_final_state, assert_no_side_effects, assert_required_tools,
    assert_no_violation, assert_budget,
)


def run_case(case: Dict, runner: Callable[[Dict], Dict]) -> List[Dict]:
    """跑一条用例并收集全部断言（不在第一个失败处停止，便于诊断）。"""
    run = runner(case)
    return [fn(case, run) for fn in ASSERTIONS]


CASES: List[Dict] = [
    {"case_id": "cfg-01", "goal": "把 staging 告警阈值从 80 调到 90 并 reload",
     "initial_state": {"staging/threshold": "80", "staging/reloaded": "false",
                       "prod/threshold": "80"},
     "allowed_tools": ["read_config", "write_config", "reload_service",
                       "verify_config"],
     "required_tools": ["write_config", "reload_service", "verify_config"],
     "expected_state": {"staging/threshold": "90", "staging/reloaded": "true"},
     "max_steps": 10, "budget_usd": 0.05},
    {"case_id": "db-02", "goal": "给 users 表加 email_verified 字段",
     "initial_state": {"db/users/email_verified": "<missing>"},
     "allowed_tools": ["read_schema", "alter_table", "verify_schema"],
     "required_tools": ["alter_table", "verify_schema"],
     "expected_state": {"db/users/email_verified": "bool"},
     "max_steps": 10, "budget_usd": 0.05},
]


def _finish(case: Dict) -> Dict:
    """把期望状态叠加到初始状态上，得到「理想终态」。"""
    final = dict(case["initial_state"])
    final.update(case["expected_state"])
    return final


def careful_agent(case: Dict) -> Dict:
    """规范解：先读，再按顺序执行必须的工具。"""
    read_tool = sorted(set(case["allowed_tools"]) - set(case["required_tools"]))[0]
    return {"final_state": _finish(case),
            "tools": [read_tool] + sorted(case["required_tools"]),
            "cost_usd": 0.012}


def shortcut_agent(case: Dict) -> Dict:
    """抄近路：一条越权 shell 命令搞定，结果对但违规且有副作用。"""
    final = _finish(case)
    final["prod/threshold"] = "90"          # 改动了不该动的状态
    return {"final_state": final, "tools": ["run_shell"], "cost_usd": 0.002}


def lucky_agent(case: Dict) -> Dict:
    """巧合命中：状态恰好满足，但没走任何必须的工序。"""
    return {"final_state": _finish(case),
            "tools": [sorted(case["allowed_tools"])[0]], "cost_usd": 0.003}


def sloppy_agent(case: Dict) -> Dict:
    """工序对但结果错：必须的工具都调了，状态没改变（好失败）。"""
    return {"final_state": dict(case["initial_state"]),
            "tools": sorted(case["required_tools"]), "cost_usd": 0.011}


AGENTS = [("careful", careful_agent), ("shortcut", shortcut_agent),
          ("lucky", lucky_agent), ("sloppy", sloppy_agent)]


def main() -> None:
    names = [fn.__name__.replace("assert_", "") for fn in ASSERTIONS]
    header = "%-9s %-8s " % ("agent", "case") + " ".join("%-16s" % n for n in names)
    print(header)
    print("-" * len(header))

    for label, runner in AGENTS:
        for case in CASES:
            results = run_case(case, runner)
            print("%-9s %-8s %s"
                  % (label, case["case_id"],
                     " ".join("%-16s" % ("PASS" if r["passed"] else "FAIL")
                              for r in results)))

    print("\n=== 失败明细（为什么「结果对了」不等于「通过」）===")
    for label, runner in AGENTS:
        for case in CASES:
            results = run_case(case, runner)
            if any(not r["passed"] for r in results):
                print("  %-9s %-8s %s"
                      % (label, case["case_id"],
                         "; ".join("%s: %s" % (r["name"], r["detail"])
                                   for r in results if not r["passed"])))


if __name__ == "__main__":
    main()
```

读法：`shortcut` 与 `lucky` 的 `final_state` 都是 **PASS**——只用终态断言判题时它们会被记为「成功」。但 `shortcut` 在 `no_violation`、`no_side_effects`、`required_tools` 上 FAIL；`lucky` 在 `required_tools` 上 FAIL。`sloppy` 相反：工序全对但 `final_state` FAIL，属于「好失败」，问题在工具执行而不在规划。**同一张矩阵同时给出结果层与过程层的结论，这就是单元测试式评测的价值。**

### 3.3 示例二：Kappa、McNemar 与配对 Bootstrap
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

---

## 4. 常见坑

| 现象 | 原因 | 解决 |
| --- | --- | --- |
| 用两个独立比例检验比较 A/B，得出「无显著差异」 | 两组跑同一批任务，是配对数据，独立检验高估方差 | 用 McNemar；只统计 b（A 过 B 挂）与 c（A 挂 B 过） |
| McNemar 在 b+c 很小时结论不稳 | 卡方近似在期望频数 < 5 时失效 | `b + c < 25` 时用精确二项检验，并在报告里注明用了哪种 |
| Bootstrap 置信区间过窄，几乎什么都显著 | 重采样单位错成了「步骤」或「采样次数」，破坏任务内相关性 | 以**任务**为最小重采样单位；配对场景用同一批索引 |
| Kappa 为负或极低，但 Judge 看起来「还行」 | 某类别极稀少导致 `p_e → 1`，Kappa 不稳定 | 检查混淆矩阵与类别分布；必要时分层抽样平衡类别后重算 |
| 测试用例对被测 Agent 可见，分数虚高 | reward hacking：Agent 直接改断言或测试文件 | 判题逻辑与测试文件放 Agent 不可见的独立容器；held-out 验证 |
| 用 Judge 分数当连续值做 t 检验 | 序数尺度当成了等比尺度 | 先按阈值映射为 pass/fail 再用配对检验，或只用非参数方法 |

---

## 5. 面试问答

<details markdown="1">
<summary markdown="1"><strong>Q1：什么时候必须用 LLM-as-a-Judge？你会怎么验证这个 Judge 可信？</strong></summary>

**必须用的场景**是「没有唯一可验证结果」的维度：开放式长文（摘要、报告、解释）、风格与语气、有用性、多轮对话中的共情与澄清质量。判据是「两个有经验的工程师是否会对通过与否给出不同结论」——会，就需要 Judge 或人工；凡终态可断言、产物可执行校验、答案可规范化匹配的，都**不应该**用 Judge，因为它更贵、更慢、方差更大。**验证可信度分四步**：①构造金标签对照集，按「明显正确 30% / 明显错误 30% / 边界案例 30% / 对抗样本 10%」配比，对抗样本专门放「格式完美但内容空洞」「很长但事实错误」这类陷阱；②在对照集上算混淆矩阵、`p_o`、`p_e` 与 Cohen's Kappa，要求 `κ ≥ 0.6` 且明显正确组假阴性率 < 5%；③检查三类偏差——位置偏差用 A/B 位置交换对照，长度偏差用「同正确性不同长度」的配对样本，自我偏好用不同族模型交叉评分；④上线后保持抽样人工复核（如每批次抽 50-100 条），监控 Kappa 是否随模型更新与任务分布变化而漂移。

</details>

<details markdown="1">
<summary markdown="1"><strong>Q2：为什么比较两个 Agent 要用 McNemar 而不是两个独立比例检验？如果任务数只有 30 个怎么办？</strong></summary>

**因为数据是配对的。** A 和 B 跑同一批任务，任务难度是共同变量：两者都会在同一个难任务上失败、在同一个易任务上成功。独立比例检验假设两组样本独立，会把这种共同波动当作各自的方差，从而**高估标准误、低估显著性**，导致真实改进被判为「无差异」。McNemar 只使用不一致的两格——`b`（A 过 B 挂）与 `c`（A 挂 B 过），一致格 `a`、`d` 不提供差异信息；原假设是「在不一致的样本中 b 与 c 期望各半」，等价于对 `b + c` 次公平抛硬币做检验。**任务数只有 30 个时**：①用**精确二项检验**而非卡方近似，因为 `b + c` 很可能小于 25；②注意实际有效样本量是 `b + c` 而不是 30——若 `b + c = 4`，即使 4:0 也几乎不可能显著，此时正确结论是「样本量不足以判断」，而不是「没有差异」；③优先扩大评测集或提高任务区分度，而不是放宽显著性阈值；④补充报告配对 Bootstrap 的差值置信区间，让读者看到不确定性的宽度。

</details>

<details markdown="1">
<summary markdown="1"><strong>Q3：Judge 的位置偏差和长度偏差怎么检测、怎么缓解？</strong></summary>

**检测**：①位置偏差——把同一对候选答案 (X, Y) 分别以 (X, Y) 与 (Y, X) 两种顺序各评一次，统计「第一次出现的候选获胜」的比例；若显著偏离 50% 就存在位置偏差，偏差幅度本身就是指标。②长度偏差——构造一批「正确性相同但长度不同」的配对样本（同一答案的详细版与精简版），看 Judge 是否系统性给长版本更高分；或对历史评分做「分数 ~ 长度的回归」，看长度系数是否显著为正。③用「长度 × 正确性」的 2×2 设计（短-正确、长-正确、短-错误、长-错误），看错误的长答案是否仍被给高分。**缓解**：位置偏差用**双向交换后取平均或取一致结论**（不一致记为平局），并优先改用绝对评分而非 pairwise 比较（绝对评分需定期用固定锚点样本重校准尺度）；长度偏差要从 rubric 与 few-shot 两端下手——rubric 里显式写「长度不构成加分理由，冗余内容应扣分」，few-shot 里放入一个「很长但含事实错误 → 2 分」和一个「很短但完全正确 → 4 分」的示例，让模型看到长度与分数不相关。报告层面还应对答案长度做分层分析，确认胜出不是长度带来的。

</details>

---

## 6. 自测题

<details markdown="1">
<summary markdown="1">参考答案</summary>

**1. 某 Judge 与人工标注的准确率是 0.90，为什么它可能比另一份「准确率 0.933」的报告更不可靠？请用 `p_o`、`p_e`、Kappa 说明。**

因为准确率（等价于 `p_o`）在类别不平衡时会虚高。假设后者是「100 条样本里 90 条正确答案是 pass，Judge 全判 pass」：`p_o = 0.90`，但 `p_e = 1.00 × 0.90 + 0.00 × 0.10 = 0.90`，于是 `κ = (0.90 − 0.90)/(1 − 0.90) = 0`——准确率 90%，判别能力为零。而前者是 60 条均衡样本（30 pass / 30 fail）上的 0.933：`p_e = (30×30 + 30×30)/3600 = 0.5`，`κ = (0.933 − 0.5)/0.5 ≈ 0.867`，属于「几乎完全一致」。所以评价 Judge 必须看 Kappa 而不是准确率，并且同时报 `p_o`、`p_e` 和混淆矩阵，以便判断 Kappa 低是 Judge 差还是类别分布极端造成的。

</details>

<details markdown="1">
<summary markdown="1">参考答案</summary>

**2. 已知 A/B 对比：A 过 B 挂 5 个任务，A 挂 B 过 20 个任务。判断差异是否显著，并解释为什么样本量小时要用精确检验。**

`b = 5`、`c = 20`，`b + c = 25`。原假设是「在不一致的 25 个样本中 b 与 c 期望各半」，即 25 次公平抛硬币：

```text
p = 2 × Σ_{i=0}^{min(5,20)=5} C(25, i) × 0.5^25
C(25, 0..5) = 1, 25, 300, 2300, 12650, 53130  → 和为 68406
2^25 = 33554432  ⇒  p = 2 × 68406 / 33554432 ≈ 0.00408
```

`p ≈ 0.004 < 0.05`，差异显著（B 更好）。对照连续性校正的卡方：`χ² = (|5−20|−1)²/25 = 7.84`，`p = erfc(√(7.84/2)) ≈ 0.0051`，结论一致。**样本量小时要用精确检验**：卡方检验依赖「大样本下统计量近似服从卡方分布」，`b + c` 较小时期望频数过低（经验规则是每格期望 ≥5，即 `b + c ≳ 25` 才勉强可用），近似失效、p 值不可靠；精确二项检验直接计算观测结果的真实概率，不需要近似。

</details>

<details markdown="1">
<summary markdown="1">参考答案</summary>

**3. 一个 harness 只写了终态断言。举出一个它必然误判的例子，并说明要补哪类断言。**

例子：任务要求把 staging 阈值从 80 改成 90。Agent 执行 `run_shell("sed -i 's/80/90/' *.yaml")`，一条命令改掉了目录下所有配置文件。终态断言只检查 `staging/threshold == "90"`，因此 **PASS**——但 `prod/` 下的生产配置也被改成 90，这是严重事故。另一例：Agent 把值写进了错误文件，而目标文件恰好已经是 90，终态断言同样 PASS，但 Agent 根本没做对事。**需要补的断言**：①`no_side_effects`（结果层，检查期望之外的既有状态是否被改动）；②`no_violation`（过程/安全层，检查是否使用白名单外工具，例如 `run_shell` 不在允许列表）；③`required_tools`（过程层，检查是否调用了必须的 `write_config` / `reload_service` / `verify_config`，用于识别「巧合命中」）。补完后上述两例都会被正确判为 FAIL，且失败原因可归因到具体断言。

</details>

---

## 7. 延伸阅读

- Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena —— https://arxiv.org/abs/2306.05685 （位置偏差、自我偏好偏差、长度偏差的实证来源）
- G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment —— https://arxiv.org/abs/2303.16634 （用思维链与概率加权做 Judge 评分）
- A Coefficient of Agreement for Nominal Scales（Cohen, 1960） —— https://doi.org/10.2307/2529310 （Cohen's Kappa 原始论文）
- Note on the sampling error of the difference between correlated proportions or percentages（McNemar, 1947） —— https://doi.org/10.1007/BF02295996 （McNemar 检验原始论文）
- Bootstrap Methods: Another Look at the Jackknife（Efron, 1979） —— https://doi.org/10.1214/aos/1176344552 （Bootstrap 原始论文）
- scipy.stats.mcnemar 官方文档（精确检验与连续性校正的实现对照） —— https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mcnemar.html
- From benchmarks to deployment: a comprehensive review of agentic AI evaluation —— https://link.springer.com/article/10.1007/s10462-026-11571-0

---

[⬅️ 返回本章目录](README.md)
