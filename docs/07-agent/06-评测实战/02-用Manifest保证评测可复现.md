> **一句话总结**：评测最大的陷阱不是判分逻辑写错，而是**两次评测根本不在同一个实验里**——模型、提示词、工具版本、数据、种子任何一项漂移，你比较的就是两团噪声；`ExperimentManifest` 的作用是把「这份报告是什么配置产生的」变成输入的一部分，让漂移从"事后回忆"变成"启动即报错"。
> **前置知识**：[01 篇](01-项目复盘-AgentEvalLab.md) 的六段流水线与四道一致性闸门、SHA-256 与规范化（canonicalization）的基本概念、JSON/JSONL 基础。
> **学完能做到**：
> 1. 列出导致评测不可复现的 8 类漂移来源，并说明每一类在 Manifest 里对应哪个字段。
> 2. 独立设计一份 Manifest，并用可运行代码算出提示词哈希与数据集哈希（含规范化规则的取舍）。
> 3. 用 `taskId + repeatId + seed` 做幂等键，把评测产物写成可断点续跑、可去重、可严格配对的形状。

---

## 1. 为什么评测不可复现是最大陷阱

### 1.1 一次典型的"提升 9 个点"

先看一个几乎每个人都遇到过的场景。某 Agent 版本 A 的评测成功率是 62%，改了提示词和两个工具的参数后，版本 B 跑出 71%。团队宣布"提升 9 个百分点"，写进周报。三周后有人想复现，跑出来 58%。

回溯发现的差异清单：

| 项 | 版本 A 评测时 | 版本 B 评测时 | 是否被记录 |
| --- | --- | --- | --- |
| 模型名 | `flash-lite` | `flash-lite` | ✅ 但没记 revision |
| 模型实际版本 | 上游静默灰度到 v2 | v2 | ❌ 无从查证 |
| 系统提示词 | 旧版（在代码里，改了没打 tag） | 新版 | ❌ |
| 采样温度 | 0.2（默认值，后来代码默认改成 0.0） | 0.0 | ❌ |
| 工具版本 | 抓价工具 v3 | 抓价工具 v4（超时 8s → 15s） | ❌ |
| 评测数据集 | 30 条 | 30 条，其中 4 条被改写 | ❌ |
| 随机种子 | 未固定 | 未固定 | ❌ |
| 评测器脚本 | 本地工作区未提交的版本 | 提交后的版本 | ❌ |

结论是那 9 个点**无法归因到提示词改动**：至少四个变量同时变了，其中"温度从 0.2 降到 0.0"和"超时翻倍"都比提示词改动更可能带来提升。

### 1.2 八类漂移来源

| # | 漂移来源 | 典型表现 | Manifest 对应字段 |
| --- | --- | --- | --- |
| 1 | 模型版本 | 上游静默升级；同一 `name` 指向不同权重 | `model.provider` / `model.name` / `model.revision` |
| 2 | 提示词内容 | 提示词散落在代码常量、数据库、环境变量里，改了不留痕 | `promptHash` |
| 3 | 采样参数 | 温度、top_p、max_tokens、并行度 | **需要扩展**（见 1.4） |
| 4 | 工具与依赖版本 | 抓取超时、重试次数、解析规则变更 | 工程约定 + 轨迹里的 `tool` 字段 |
| 5 | 数据 | 任务被改写、增删、难度重分布 | `dataset.name` / `dataset.hash` / `taskIds` |
| 6 | 随机源 | seed 未固定，重跑结果不同 | `seeds` / `repeatCount` |
| 7 | 评测器自身 | 判定规则改了，成功率跟着变 | `evaluatorVersion` |
| 8 | 时序与环境 | 时区、并发、限流、外部服务抖动 | 未覆盖，须另存环境信息 |

前七类可以被"输入的一部分"解决，第八类不行——所以项目在 `docs/ARCHITECTURE.md` 里明确写了：Manifest 能说明"什么配置产生了这份报告"，**但它不会自动证明外部模型服务或私有数据从未变化**；正式实验仍需保存原始轨迹、环境信息和人工复核记录。

### 1.3 为什么 `temperature=0` 不够

一个常见的误解是"设了温度 0 就可复现了"。在 Agent 场景下这是错的，理由有三条：

1. **多轮累积**。即使单次采样在温度 0 下近似确定，只要模型服务端存在批处理、浮点非确定性或负载均衡到不同硬件，第 1 步的工具参数就可能微差，第 5 步就会分叉到完全不同的轨迹。
2. **工具侧的不确定性不可消除**。网页改版、接口返回顺序变化、限流与超时，都不是采样参数能控制的。这部分只能靠冻结数据源快照（record & replay）来治理。
3. **温度本身就是一个会变的配置**。它常常是代码里的默认值，某次重构把 `0.2` 改成 `0.0` 不会有任何告警——于是"温度 0"本身也成了未记录变量。

所以正确的心态是：**温度 0 只是降低噪声，不能替代配置记录。** Manifest 要记录的是"我当时用了什么"，而不是"我以为我用了什么"。

### 1.4 Manifest 不覆盖的那一格：采样参数

这里必须诚实地说清楚一个边界：`ExperimentManifest` 有 `model`、`promptHash`、`codeCommit`、`dataset`、`taskIds`、`seeds`、`repeatCount`、`evaluatorVersion`、`data`，但**没有温度、top_p、max_tokens 这些采样参数**。

它用另一种方式兜住：`promptHash` 覆盖提示词、`codeCommit` 覆盖代码（采样参数通常写在代码或配置里，所以 commit 变了哈希就变）、`model.revision` 覆盖权重。如果你把采样参数放在**独立的运行配置**里而不进版本库，这个字段就漏了。

工程上的补救是很小的改动：额外定义一个 `runConfig`（温度、top_p、超时、最大步数、并发度）纳入 Manifest，并把它一起写进报告。项目本身没有做这件事，接入时值得补上——这条属于"复述该项目时要指出它的边界"，而不是"它做错了"。

---

## 2. Manifest 字段逐个讲解

### 2.1 字段表

| 字段 | 类型与约束 | 不合法时的行为 |
| --- | --- | --- |
| `schema` | 字面量 `agent-eval-lab-manifest-v1` | 报 `$.manifest.schema: 必须是 agent-eval-lab-manifest-v1` |
| `experimentId` | 非空字符串 | 报 `$.manifest.experimentId: 必须是非空字符串` |
| `createdAt` | 可被 `Date.parse` 解析的 ISO 时间 | `$.manifest.createdAt: 必须是有效的 ISO 日期时间` |
| `model.provider` | 非空字符串 | 报错 |
| `model.name` | 非空字符串 | 报错 |
| `model.revision` | 可选字符串 | 缺省合法 |
| `promptHash` | `sha256:<64 位十六进制>` | `$.manifest.promptHash: 必须使用 sha256:<64位十六进制> 格式` |
| `codeCommit` | 7–40 位十六进制 | `$.manifest.codeCommit: 必须是 7–40 位十六进制 Git commit` |
| `dataset.name` | 非空字符串 | 报错 |
| `dataset.hash` | `sha256:<64 位十六进制>` | 报错（与 `promptHash` 同规则） |
| `taskIds` | 非空且去重的字符串数组 | `至少包含一个预期任务 ID` / `taskId 重复：t3` |
| `seeds` | 非空且去重的整数数组 | `至少包含一个确定性 seed` / `seed 重复：1` |
| `repeatCount` | 正整数，且 **≥ `seeds.length`** | `每任务配对重复总数不能少于 seeds 数量` |
| `evaluatorVersion` | 语义化版本号 | `必须是语义化版本号` |
| `data.classification` | `synthetic` / `controlled` / `public` | 枚举报错 |
| `data.containsPrivateData` | 布尔 | 报错 |
| `data.redacted` | 布尔 | 报错 |
| `data` 交叉约束 | `public` 时 `containsPrivateData` 必须为 `false` | `$.manifest.data: public 数据不能标记为包含私有数据` |
| `notes` | 可选字符串数组 | 缺省合法 |

### 2.2 一份完整且可复算的示例

下面这份 Manifest 不是编的——它是仓库 `examples/public-evidence/input-results.json` 里的真实内容，两个哈希都可以用第 3 节的代码逐位复算：

```json
{
  "schema": "agent-eval-lab-manifest-v1",
  "experimentId": "public-synthetic-evidence-v1",
  "createdAt": "2026-08-19T00:00:00.000Z",
  "model": { "provider": "fixture", "name": "deterministic-synthetic-agent", "revision": "v1" },
  "promptHash": "sha256:59385ca68f462dd301e9866b7e918dafd1cc466d5779d9a2d8d7acbe7091fedc",
  "codeCommit": "74f4a3a",
  "dataset": {
    "name": "agent-eval-lab-public-synthetic-v1",
    "hash": "sha256:af71072674c8e544ed7154cc99a7bf815c050c9dc693e2ca7ff38f783f24ddb2"
  },
  "taskIds": ["easy-title", "medium-search", "hard-block"],
  "seeds": [1],
  "repeatCount": 1,
  "evaluatorVersion": "0.3.0",
  "data": { "classification": "synthetic", "containsPrivateData": false, "redacted": true },
  "notes": ["完全合成的公开演示；不代表真实 Agent 表现。", "哈希推导规则记录在 examples/public-evidence/README.md。"]
}
```

### 2.3 关键字段的设计理由

**`taskIds` 是"应跑全集"，不是"实跑清单"。** 这是整个 Manifest 里最重要的一个字段。它声明的是**这次实验应该覆盖哪些任务**；然后工具会拿实际运行结果去和它比对，不相等就报错。这样"删掉最难的任务"这条捷径被彻底堵死——你不可能通过少跑来提高成功率，因为少跑会直接让报告生成失败。

**`seeds` 与 `repeatCount` 是两个不同的概念。** `seeds` 是随机源集合（每个任务必须覆盖全部 seed）；`repeatCount` 是每个任务的配对重复**总数**。约束是 `repeatCount ≥ seeds.length`，也就是**允许同一个 seed 通过不同的 `repeatId` 重复多次**。这个设计允许做两件事：①同一随机源下重复，用于估计"环境噪声"；②多个随机源，用于估计"采样噪声"。两者混在一起时，靠 `repeatId` 区分。

**`evaluatorVersion` 记录的是"实验当时的评测器"，报告里另记"本次生成报告的评测器"。** 两者可能不同——你用 0.3.0 的工具去复算一个 0.2.0 时代的实验，报告必须同时说清"这份结果的判定规则来自 0.2.0"和"这份 JSON 是 0.3.0 生成的"。混淆这两者，会让"评测器改了口径导致成功率变化"被误读成"Agent 改进了"。

**`data` 三件套是发布安全的闸门。** `classification` 区分合成/受控/公开，`containsPrivateData` 与 `redacted` 记录实际内容状态，并强制 `public` 不能包含私有数据。这三项不参与统计，但它们决定了**这份报告能不能被公开**。

### 2.4 示例输入里的轨迹记录

Manifest 之外，输入还有两种形态。JSONL 用显式 `recordType` 逐行承载，且**禁止混用 `run` 与 `result`**：

```jsonl
{"recordType":"manifest","data":{"schema":"agent-eval-lab-manifest-v1","experimentId":"..."}}
{"recordType":"task","data":{"taskId":"easy-01","difficulty":"easy","objective":"...","requiredEvidence":["title"]}}
{"recordType":"run","data":{"runId":"baseline-easy-01-r1","taskId":"easy-01","condition":"baseline","repeatId":"r1","seed":1,"status":"completed","events":[]}}
```

解析规则里有几条很实用的细节：空行与 `#` 开头的注释行被跳过；必须**恰好**包含 1 条 `manifest`；可以一条 `task` 都没有（但 `results-v1` 输入带 `task` 记录会被拒绝）；任意一行 JSON 语法错误都会带上行号 `$line[17]`。

---

## 3. 数据集哈希与提示词哈希的计算方式

### 3.1 核心原则：先规范化，再哈希

哈希很容易写，写出**稳定的**哈希很难。原始内容的换行符（`\n` vs `\r\n`）、BOM、JSON 键顺序、行序、浮点表示、时区写法差一个字符，哈希就完全不同。必须先定义规范化规则，再对规范化结果取哈希。

更重要的是：**规范化口径一旦确定就必须冻结。** 下面会看到，同一段提示词在"原始口径"和"规范化口径"下哈希完全不同（`59385c…` vs `547a99…`）。两者都正确，混用就会让 Manifest 校验失败。

### 3.2 仓库公开示例的口径

`examples/public-evidence/README.md` 把哈希推导规则写得很直白，可以逐位复核：

- `promptHash`：字符串 `Evaluate each synthetic trajectory using evidence-bound completion rules.` 的 SHA-256；
- `dataset.hash`：稳定数据集标识 `agent-eval-lab-public-synthetic-v1` 的 SHA-256。

注意 `dataset.hash` 这里哈希的是**一个标识字符串**，不是数据集内容。这是一个**公开演示的简化**：它证明"哈希链路可复算"，但不提供"内容一变哈希就变"的防篡改能力。生产实验应该哈希内容本身，见 3.4。

### 3.3 可运行实现

```python
"""复现 agent-eval-lab 的两类哈希口径：提示词哈希与数据集哈希。

只依赖标准库。核心约定：先定义规范化规则，再哈希。
"""

from __future__ import annotations

import hashlib
import json
import unicodedata
from pathlib import Path
from typing import Any, Iterable


class HashError(ValueError):
    """哈希输入不满足规范化前置条件。"""


def sha256_text(text: str) -> str:
    """返回 `sha256:<64 位小写十六进制>`，与 Manifest 的格式约束一致。"""
    if not isinstance(text, str):
        raise HashError("sha256_text 只接受 str")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def canonical_json(value: Any) -> str:
    """稳定序列化：键排序、无多余空白、不转义非 ASCII。"""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


# ------------------------------------------------------------- 提示词哈希
def normalize_prompt(text: str) -> str:
    """提示词规范化：统一换行、NFC 归一、去行尾空白、单个结尾换行。"""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = unicodedata.normalize("NFC", text)
    lines = [line.rstrip() for line in text.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"


def prompt_hash(text: str) -> str:
    """推荐口径：对规范化后的提示词取哈希（结尾换行不影响结果）。"""
    return sha256_text(normalize_prompt(text))


def prompt_hash_raw(text: str) -> str:
    """仓库公开示例采用的口径：直接对原始字符串取哈希。"""
    return sha256_text(text)


# ------------------------------------------------------------- 数据集哈希
def dataset_content_hash(records: Iterable[Any]) -> str:
    """内容哈希：记录规范化后排序再整体哈希，与行的物理顺序无关。"""
    normalized = sorted(canonical_json(record) for record in records)
    if not normalized:
        raise HashError("数据集为空，拒绝生成哈希")
    return sha256_text("\n".join(normalized) + "\n")


def dataset_content_hash_from_jsonl(path: str | Path) -> str:
    """从 JSONL 文件读内容哈希：跳过空行与 `#` 注释行，去 BOM，显式 UTF-8。"""
    text = Path(path).read_text(encoding="utf-8").lstrip("\ufeff")
    records = [json.loads(line) for line in text.split("\n")
               if line.strip() and not line.strip().startswith("#")]
    return dataset_content_hash(records)


def dataset_id_hash(identifier: str) -> str:
    """标识哈希：只哈希稳定数据集 ID。仓库公开示例用的是这一种。"""
    if not identifier.strip():
        raise HashError("数据集标识不能为空")
    return sha256_text(identifier)


if __name__ == "__main__":
    prompt = "Evaluate each synthetic trajectory using evidence-bound completion rules."
    identifier = "agent-eval-lab-public-synthetic-v1"
    assert prompt_hash_raw(prompt) == (
        "sha256:59385ca68f462dd301e9866b7e918dafd1cc466d5779d9a2d8d7acbe7091fedc")
    assert dataset_id_hash(identifier) == (
        "sha256:af71072674c8e544ed7154cc99a7bf815c050c9dc693e2ca7ff38f783f24ddb2")
    # 规范化后结尾换行、\r\n 不改变结果；内容哈希与行序、键序无关
    assert prompt_hash(prompt) == prompt_hash(prompt + "\n") == prompt_hash(prompt + "\r\n")
    assert dataset_content_hash([{"taskId": "t1", "seed": 1}, {"seed": 2, "taskId": "t2"}]) == \
        dataset_content_hash([{"seed": 2, "taskId": "t2"}, {"taskId": "t1", "seed": 1}])
    print("self-check OK")
    print("promptHash(raw)   =", prompt_hash_raw(prompt))
    print("promptHash(norm)  =", prompt_hash(prompt))
    print("dataset.hash(id)  =", dataset_id_hash(identifier))
    print("dataset.hash(body)=", dataset_content_hash([{"taskId": "t1", "seed": 1},
                                                       {"taskId": "t1", "seed": 2}]))
```

运行输出（两个哈希与仓库里的 Manifest **逐位相同**）：

```text
self-check OK
promptHash(raw)   = sha256:59385ca68f462dd301e9866b7e918dafd1cc466d5779d9a2d8d7acbe7091fedc
promptHash(norm)  = sha256:547a99eec715132850d9f1e2a8a16487333feaedb237270524efd881a2f72aa7
dataset.hash(id)  = sha256:af71072674c8e544ed7154cc99a7bf815c050c9dc693e2ca7ff38f783f24ddb2
dataset.hash(body)= sha256:1466fcf2593637352a821a05ed26b28cc1a81e6f16ab9466dc326ecbe5b2b5c6
```

### 3.4 两种口径的差别，以及该选哪个

`promptHash(raw)` 与 `promptHash(norm)` 输出的哈希**完全不同**（`59385c…` vs `547a99…`），因为规范化给文本补了一个结尾换行。这不是 bug，是取舍：

| 口径 | 优点 | 代价 | 适用 |
| --- | --- | --- | --- |
| 原始字符串哈希 | 实现最简单；任何字节变化都能检出 | 编辑器自动补的结尾换行、`\r\n` 差异会造成"内容其实没变但哈希变了"的假警报 | 提示词从单一文件读取、有 `.gitattributes` 锁定换行 |
| 规范化后哈希 | 对无害的格式差异免疫，减少假警报 | 规范化规则本身可能漏掉真实变化（例如把行尾空格裁掉，而空格在提示词里是有意义的） | 提示词由多人多工具编辑、需要跨平台复现 |

**建议：用规范化口径，并把规范化函数纳入版本控制。** 提示词里行尾空格通常无意义，但如果你确实依赖它（比如用缩进表达层级），就要在规范化里保留行尾空白，只统一换行符与 Unicode 形式。

数据集哈希则强烈建议用**内容哈希**而非标识哈希：

| 口径 | 能防什么 | 不能防什么 |
| --- | --- | --- |
| 标识哈希（`dataset_id_hash`） | 认错数据集 | 数据集内容被悄悄改写 |
| 内容哈希（`dataset_content_hash`） | 内容任何实质变化 | 不影响语义的物理差异（这是优点） |

内容哈希的实现细节值得注意：每条记录先用 `sort_keys=True` 序列化成 canonical JSON，再**整体排序**，最后拼接哈希。排序这一步让"数据集记录的物理顺序"不影响哈希——这正是我们想要的，因为数据集顺序不该改变实验身份。但要注意：如果你**故意**用顺序表达意义（比如课程学习式从易到难），那就不能排序，必须改用带顺序的拼接。

### 3.5 哈希的三个易错点

1. **BOM 与编码**。UTF-8 BOM 会在文件开头插入 `\ufeff`，读文件时要 `lstrip("\ufeff")`，否则哈希漂移。同时必须显式 `encoding="utf-8"`——依赖平台默认编码（Windows 上常是 GBK）会在跨平台时静默产生不同哈希。
2. **浮点与数值表示**。`1.0` 与 `1` 在 `json.dumps` 下是不同的字符串。任务集里如果有阈值、权重这类数值，必须约定"统一用整数或统一保留几位小数"，并在规范化时强制转换。
3. **时间与时区**。`2026-03-02T09:00:00Z` 与 `2026-03-02T17:00:00+08:00` 是同一时刻但不同字符串。数据里含时间戳时，规范化必须统一到 UTC 并以固定精度格式化，否则同一份数据在不同机器上算出不同哈希。

---

## 4. 用 `taskId + repeatId + seed` 作为幂等键

### 4.1 一次"科学观测"的三要素

工具内部把配对主键定义成三段拼接：

```ts
function pairKey(run: AgentRun): string {
  return `${run.taskId}::${run.repeatId}::${run.seed ?? "none"}`;
}
```

三段各自回答一个问题：

| 段 | 回答的问题 | 少了它会怎样 |
| --- | --- | --- |
| `taskId` | 这是哪个任务？ | 不同任务的结果会互相覆盖 |
| `repeatId` | 这是该任务的第几次重复？ | 同任务的多次重复会互相覆盖，只剩最后一次 |
| `seed` | 这次重复用的哪个随机源？ | 无法保证 A/B 在**同一随机源**上比较，差异里混入了种子差异 |

三者合起来才唯一确定**一次可比较的科学观测**。这台词听着夸张，但对照一下就明白了：如果你要比较两种药物在同一批病人上的效果，必须知道"哪个病人、第几次测量、在什么条件下"，缺一个就没法配对。

### 4.2 幂等键的三重作用

**① 防覆盖。** 统计层构建配对字典时，同一 `pairKey` 出现两次直接抛错：

```ts
for (const result of results) {
  if (byPair.has(result.pairKey)) throw new Error(`Duplicate ${condition} pair key: ${result.pairKey}`);
  byPair.set(result.pairKey, result);
}
```

"重跑覆盖"是最隐蔽的数据污染：文件系统上看起来只多了一个新文件，实际报告里的分母换了。抛错比"以最后一次为准"安全得多——因为它逼你去查**为什么同一个键会出现两次**（通常是调度脚本重复触发或断点续跑没做去重）。

**② 保证配对。** 两侧的 key 集合必须完全相同：

```ts
if (baselineKeys.join("\n") !== optimizedKeys.join("\n")) {
  throw new Error(`Unpaired results: missing optimized [...] ; missing baseline [...]`);
}
```

这一条保证成功率、`fail→pass`/`pass→fail`、McNemar 三者用的是**同一批有效配对**。如果允许"有的 key 只有 baseline、有的只有 optimized"，那么成功率的分母和 McNemar 的样本量就会不同，两个数字之间的任何推断都是错的。

**③ 断点续跑与缓存。** 幂等键是天然的续跑单位：跑完一个 `(taskId, repeatId, seed)` 就落一条结果，中断后重跑时按它去重。这也是它被叫做"幂等键"的原因——同一键重复执行，状态不叠加。

### 4.3 导入路径会重算并强制校验

`results-v1` 输入下 `pairKey` 是显式字段，工具不会盲信，而是**按三段重新计算后比对**：

```ts
const expectedPairKey = `${taskId}::${repeatId}::${seed}`;
if (pairKey !== expectedPairKey) {
  fail(`${path}.pairKey`, `必须由 taskId + repeatId + seed 生成，期望 ${expectedPairKey}`);
}
```

这条校验防的是**通过改主键来改变配对关系**：如果不校验，导入文件可以给两个本该配对的样本编不同的 `pairKey`，让它们变成"孤立配对"从而被统计逻辑忽略——或者更糟，把本该独立的两条编成同一个键。

### 4.4 落到工程：把幂等键用起来

| 场景 | 用法 |
| --- | --- |
| 结果落盘 | 文件名用 `pairKey` 转义后命名，如 `easy-title__r1__1.json` |
| 数据库 | 对 `(condition, pairKey)` 建唯一索引，重复写入直接冲突而不是覆盖 |
| 续跑脚本 | 启动时读已有结果集合，跳过已存在的键 |
| 报告自检 | 断言 `len(results) == len(taskIds) * repeatCount * 2`（两个条件） |
| 缓存 | 以 `(pairKey, promptHash, model.revision)` 为缓存键，任何一项变化就失效 |

`seed` 缺失时工具会把 `pairKey` 写成 `...::none`，但**Manifest 模式下每条运行都必须带 seed**，所以这个分支只对非 Manifest 的宽松场景存在。别依赖它。

---

## 5. 一致性闸门与常见坑

### 5.1 四道闸门

`pipeline.ts` 在实际评测前执行四道检查。它们全部抛 `SchemaValidationError`（CLI 退出码 2），错误信息直接指向字段路径：

| # | 检查 | 实例错误信息 |
| --- | --- | --- |
| 1 | 轨迹输入下 `tasks` 与 `manifest.taskIds` 集合相等 | `$.tasks: TaskSpec 与 manifest.taskIds 不一致；缺少 [hard-block]；多出 []` |
| 2 | 实际运行任务集合与 `manifest.taskIds` 集合相等 | `$.runs: 实际运行任务与 manifest.taskIds 不一致；缺少 [hard-block]` |
| 3 | 每条运行带 seed 且在 `manifest.seeds` 内 | `$.manifest.seeds: 运行 baseline-t1-r1 未声明 seed` |
| 4 | 每任务 `(repeatId, seed)` 数量 = `repeatCount`、覆盖全部 seed、各任务调度一致 | `$.manifest.repeatCount: 任务 t1 声明 2 次配对重复，实际为 1 次` |

### 5.2 可运行的自检脚本

把四道闸门移植成独立脚本，可以在生成评测数据之后、跑评测之前先自检一遍——比等到评测报错再回头查数据要快得多：

```python
"""Manifest 一致性自检：把 agent-eval-lab 的四道闸门做成一段可运行的检查。"""

from __future__ import annotations

import json
from typing import Any, Iterable


class ManifestError(ValueError):
    """Manifest 与实际运行不一致。"""


def check_manifest(manifest: dict[str, Any], runs: Iterable[dict[str, Any]]) -> None:
    runs = list(runs)
    expected = sorted(set(manifest["taskIds"]))

    # 闸门 1/2：实际运行涉及的任务集必须与 Manifest 声明的完全一致
    actual = sorted({run["taskId"] for run in runs})
    missing = [task for task in expected if task not in actual]
    extra = [task for task in actual if task not in expected]
    if missing or extra:
        raise ManifestError(
            f"实际运行任务与 manifest.taskIds 不一致；缺少 {missing}；多出 {extra}"
        )

    # 闸门 3：每条运行必须带 seed，且 seed 在声明集合内
    seeds = set(manifest["seeds"])
    for run in runs:
        if "seed" not in run or run["seed"] is None:
            raise ManifestError(f"运行 {run['runId']} 未声明 seed")
        if run["seed"] not in seeds:
            raise ManifestError(f"运行 {run['runId']} 使用了未声明 seed：{run['seed']}")

    # 闸门 4：每任务 (repeatId, seed) 调度数量与覆盖，且各任务调度完全一致
    schedule: dict[str, set[tuple[str, int]]] = {}
    for run in runs:
        schedule.setdefault(run["taskId"], set()).add((run["repeatId"], run["seed"]))
    repeat_count = manifest["repeatCount"]
    for task_id in expected:
        entries = schedule.get(task_id, set())
        if len(entries) != repeat_count:
            raise ManifestError(
                f"任务 {task_id} 声明 {repeat_count} 次配对重复，实际为 {len(entries)} 次"
            )
        covered = {seed for _, seed in entries}
        if uncovered := sorted(seeds - covered):
            raise ManifestError(f"任务 {task_id} 未覆盖声明 seed：{uncovered}")
    reference = sorted(schedule[expected[0]])
    for task_id in expected[1:]:
        if sorted(schedule[task_id]) != reference:
            raise ManifestError(
                f"任务 {task_id} 的 repeatId/seed 调度与 {expected[0]} 不一致"
            )


if __name__ == "__main__":
    manifest = {"taskIds": ["t1", "t2"], "seeds": [1, 2], "repeatCount": 2}
    runs = [{"runId": f"{c}-{t}-r{r}", "taskId": t, "condition": c, "repeatId": f"r{r}", "seed": s}
            for t in ("t1", "t2") for c in ("baseline", "optimized") for r, s in ((1, 1), (2, 2))]
    check_manifest(manifest, runs)
    print("合法 Manifest：通过")
    cases = {
        "少跑一个任务": (manifest, [r for r in runs if r["taskId"] != "t2"]),
        "多出未声明任务": (manifest, runs + [dict(runs[0], taskId="t3", runId="baseline-t3-r1")]),
        "漏带 seed": (manifest, [{k: v for k, v in r.items() if k != "seed"}
                                 if r["runId"].endswith("r1") else r for r in runs]),
        "用了未声明 seed": (manifest, [dict(r, seed=9) if r["runId"].endswith("r2") else r
                                       for r in runs]),
        "重复次数不足": (dict(manifest, repeatCount=4), runs),
        "任务间调度不一致": (manifest, [dict(r, repeatId="r9")
                                       if r["taskId"] == "t2" and r["repeatId"] == "r2" else r
                                       for r in runs])}
    for label, (bad_manifest, bad_runs) in cases.items():
        try:
            check_manifest(bad_manifest, bad_runs)
        except ManifestError as error:
            print(f"  {label}: 拒绝 -> {error}")
        else:
            print(f"  {label}: 未拒绝（请修检查逻辑）")
```

实际输出：

```text
合法 Manifest：通过
  少跑一个任务: 拒绝 -> 实际运行任务与 manifest.taskIds 不一致；缺少 ['t2']；多出 []
  多出未声明任务: 拒绝 -> 实际运行任务与 manifest.taskIds 不一致；缺少 []；多出 ['t3']
  漏带 seed: 拒绝 -> 运行 baseline-t1-r1 未声明 seed
  用了未声明 seed: 拒绝 -> 运行 baseline-t1-r2 使用了未声明 seed：9
  重复次数不足: 拒绝 -> 任务 t1 声明 4 次配对重复，实际为 2 次
  任务间调度不一致: 拒绝 -> 任务 t2 的 repeatId/seed 调度与 t1 不一致
```

注意每条错误信息都能**直接定位到字段**：`缺少 ['t2']` 告诉你少跑了哪个任务，`使用了未声明 seed：9` 告诉你是哪个值越界。这比一句"Manifest 校验失败"有用得多。

### 5.3 常见坑表

| 现象 | 原因 | 解决 |
| --- | --- | --- |
| 同一份代码两次跑出不同成功率 | seed 未固定，或模型侧仍有非确定性 | 固定 `seeds` 并用 `repeatCount` 覆盖多次；报置信区间而不是单点 |
| 换了提示词但 `promptHash` 没变 | 提示词被拼在代码里，或哈希的是"提示词模板 ID"而不是最终字符串 | 哈希**发送给模型的最终字符串**；把组装后的 prompt 落盘并纳入版本控制 |
| `promptHash` 无故变了 | 编辑器补了结尾换行 / 跨平台换行符不同 / BOM | 用规范化口径；加 `.gitattributes`；读文件时去 BOM 并显式 UTF-8 |
| 数据集改了两条，哈希没变 | 用的是标识哈希 | 改用内容哈希；对每条记录 canonical JSON 序列化后排序再整体哈希 |
| 报告删掉最难的任务后成功率大涨 | Manifest 只声明了"实跑清单" | `taskIds` 必须声明**应跑全集**；实跑集合与之比对，不等即报错 |
| 各任务跑的次数不一样 | 调度脚本按可疑任务灵活跳过 | 强制 `repeatCount` 一致且 `(repeatId, seed)` 序列逐任务相同 |
| A/B 对比里混入了种子差异 | A 用 seed 1、B 用 seed 2 | 配对键含 seed；统计层要求两侧 key 集合完全相等 |
| 上游模型静默升级，历史分数不可比 | 只记了 `model.name` | 记 `model.revision`，并在报告中标注"无法证明服务端未变化" |
| 评测器改了口径，成功率跳变 | 没记录评测器版本 | `evaluatorVersion` 记实验当时版本；报告另记本次生成工具版本 |
| 报告字节每次都不同，无法做 CI diff | `generatedAt` 是真实时间戳 | 对统计量断言 + 字段级 diff（排除时间戳），不要做整文件字符 diff |
| 重复运行结果被静默覆盖 | 落盘按 `runId` 命名，重跑覆盖同名文件 | 用 `pairKey` 命名、加唯一索引；重复键直接抛错 |
| 采样参数漂移无人发现 | 温度/超时/步数上限不在 Manifest 里 | 显式增加 `runConfig` 字段（这是本项目的已知边界） |

---

## 6. 面试问答与自测题

### 6.1 面试问答

<details><summary>参考答案</summary>

**Q1：为什么说"评测不可复现"比"判分逻辑写错"更危险？**

判分逻辑写错通常是**系统性的、可见的**：它在所有样本上一致地错，一查逐条结果就能看出方向，修完就不再犯。不可复现则是**随机的、隐形的**：表现为"同一个改动这次涨 5 点、下次跌 3 点"，你无法从数字本身判断它是信号还是噪声。它会污染整条决策链——基于不可复现数字做出的架构决策、资源分配都会是错的，而且**错误不会暴露**，因为下次评测又是另一个随机数。

更具体地说，它让三种改进无法区分：①真实能力提升；②配置漂移带来的偶然提升（模型灰度、温度变化、超时放宽）；③评测集与判分口径变化带来的虚高。**只有把配置固定成输入的显式一部分，②和③才被排除，①才有讨论的可能。** 这就是 Manifest 存在的全部理由：它不提升能力，只是让"提升"这个词变得有意义。

</details>

<details><summary>参考答案</summary>

**Q2：`seeds` 和 `repeatCount` 有什么区别？为什么 `repeatCount` 允许大于 `seeds.length`？**

`seeds` 是**随机源集合**，约束是"每个任务必须在这几个随机源上都被执行过"（覆盖）。`repeatCount` 是**每个任务的配对重复总数**，约束是"每个任务应产出多少对 baseline/optimized 结果"（样本量）。规则是 `repeatCount ≥ seeds.length`，且每个任务必须覆盖全部声明 seed。

允许大于，是因为同一随机源通过**不同 `repeatId`** 重复是有意义的：同 seed 跑两次若结果不同，差异来自**环境噪声**（工具返回、时序抖动）；换 seed 跑，差异里还含**采样噪声**。把两类噪声分开是方差分析的基础。工程含义是 `repeatId`（第几次重复）与 `seed`（哪个随机源）正交，配对键 `taskId::repeatId::seed` 同时含两者，既不会错配随机源，也不会错配同源的多次重复。

</details>

<details><summary>参考答案</summary>

**Q3：数据集哈希应该哈希"标识"还是"内容"？如果内容是 JSONL 且记录顺序有意义，怎么办？**

应优先哈希**内容**。标识哈希（如 `sha256("my-dataset-v1")`）只能防"认错数据集"——它本质是版本号字符串，内容被悄悄改写（改了两条期望值、删了一条难任务）哈希完全不变，而这恰恰是最常见也最危险的变化。

代价是**需要规范化**，否则无害的物理差异会变成假警报：换行符、BOM、键顺序、行序、浮点表示、时间戳时区。实际形态是"对 `sort_keys=True, separators=(",", ":"), ensure_ascii=False` 序列化后的记录整体排序再拼接哈希"；排序刻意让行序不影响哈希。

如果**记录顺序确实有意义**（课程学习式从易到难、多轮对话的轮次），就**不能排序**，必须在规范化里标注"顺序敏感"。更好的做法是把顺序变成记录里的显式字段（`"order": 3`）——顺序语义进入数据而不是进入物理排列，更可维护。

</details>

### 6.2 自测题

<details><summary>参考答案</summary>

**1. Manifest 里为什么要声明 `taskIds`（应跑全集），而不是直接用实际跑出来的任务列表做分母？**

因为"用实跑列表做分母"等于把**删除难点**变成提高成功率的捷径：只要在调度脚本里跳过失败率最高的几个任务，成功率立刻上升，而报告看起来完全合法——没有任何一行数据是错的。这是最廉价也最难事后发现的作弊方式。

声明应跑全集后，校验变成"实跑任务集合必须与 `taskIds` 完全相等"，少跑任何一个任务都直接抛错、拒绝生成报告。项目专门有一条测试叫「Manifest taskIds 中未执行的任务不能从报告分母消失」，同时覆盖 `trajectories-v1` 与 `results-v1` 两条路径——导入路径同样可以被"删掉整项任务"美化。这也解释了为什么"缺任务"和"少 seed"必须报错而不是警告：**只要存在"数据不全也能出报告"的口子，就一定会有人在压力下用它。**

</details>

<details><summary>参考答案</summary>

**2. 一个评测脚本记录 `model.name = "flash-lite"`，这足够吗？还需要什么？**

不够。`model.name` 只是**可变的营销标签**，上游可以在不改名的情况下灰度新权重，此时历史分数与新分数已不可比，但清单上看不出差异。至少要补三样：①`model.revision`（或 API 返回的模型版本/快照 ID），把"同名不同权重"变成显式可比字段；②**运行时间窗**，因为灰度是时间相关的，两个分数若跨过灰度点，差异无法归因；③**把无法证明的部分写进报告**——项目明确说 Manifest 不会自动证明外部模型服务从未变化。

条件允许时还应记录**服务端返回的指纹**（`system_fingerprint`、snapshot id）与**同批次重复运行的方差**：同一版本连跑 3 次若相差 4 个点，小于 4 点的"提升"根本不用讨论。

</details>

<details><summary>参考答案</summary>

**3. 为什么 `pairKey` 必须在导入时**重新计算**并强制比对，而不是直接信任输入文件里的值？**

因为 `pairKey` 决定**谁和谁配对**。直接信任输入值，外部文件就能通过改主键操纵统计：把两个本该配对的样本编成不同的键，让它们变成"孤立配对"被统计逻辑忽略——**这是剔除不理想数据最隐蔽的方式**（`pairs` 数量减少，但看不出少了谁）；反过来也能把本该独立的两条编成同一个键，被去重逻辑丢掉一条。

重新计算的成本极低（一次字符串拼接），收益是**配对关系不再是可被外部伪造的自由参数**：它完全由 `taskId`、`repeatId`、`seed` 决定，而这三个字段本身又受其他校验约束。这也是"幂等键"的深层含义：幂等键必须是**数据的函数**，而不是**数据的字段**。

</details>

<details><summary>参考答案</summary>

**4. 把评测接入 CI，Manifest 里哪些字段应该自动注入，哪些必须人工维护？**

**自动注入**的是"环境事实"，取值无歧义：`codeCommit`（`GITHUB_SHA`）、`createdAt`、`evaluatorVersion`（读 `package.json`）、`dataset.hash` 与 `promptHash`（对版本库里的文件实时计算）。好处是"不可能忘记更新"。

**人工维护**的是"意图声明"，机器猜不出来：`experimentId`、`taskIds`（**应该**覆盖哪些任务——防作弊的关键字段）、`seeds` 与 `repeatCount`（投入多少重复才够）、`model`（CI 不知道实际调用的是哪个快照）、`data.classification` 与 `containsPrivateData`（发布安全判断）。

判据是：**能自动算的必须自动算，因为手填的值会过期；表达"应该是什么"的必须手填，因为机器只看到"实际是什么"。** Manifest 的价值正是把这两类放在一起比对——`taskIds`（应跑）与实际运行（实跑）不一致时报错，而这个比对只有人工字段才能提供。

</details>

---

## 7. 延伸阅读

- Agent Eval Lab 仓库 —— https://github.com/coolwkx/agent-eval-lab （本项目；重点读 `docs/ARCHITECTURE.md` 与 `examples/public-evidence/README.md`）
- Agent Eval Lab 的公开证据示例 —— https://github.com/coolwkx/agent-eval-lab/tree/main/examples/public-evidence （`promptHash` 与 `dataset.hash` 的推导规则，可用 3.3 节代码逐位复算）
- Agent Eval Lab 架构说明 —— https://github.com/coolwkx/agent-eval-lab/blob/main/docs/ARCHITECTURE.md （可复现边界、配对实验设计、证据信任边界）
- JSON Schema Draft 2020-12 发布说明 —— https://json-schema.org/draft/2020-12/release-notes （`$schema`、`oneOf`、`const` 的用法）
- JSON Canonicalization Scheme (RFC 8785) —— https://www.rfc-editor.org/rfc/rfc8785 （跨语言稳定序列化的标准化方案，比手写 `sort_keys` 更严格）
- Unicode Normalization Forms (UAX #15) —— https://unicode.org/reports/tr15/ （NFC/NFD 对哈希稳定性的影响）
- reproducible-builds.org —— https://reproducible-builds.org/ （工业界对"可复现"的系统性讨论，含时间戳与环境信息的处理思路）
- McNemar's test —— https://en.wikipedia.org/wiki/McNemar%27s_test （配对二分类检验，见 [03 篇](03-失败归因与显著性检验实战.md)）
- lm-evaluation-harness —— https://github.com/EleutherAI/lm-evaluation-harness （版本化评测配置的工程对照，其 `--seed` 与模型版本记录方式值得对比）

---

[⬅️ 返回本章目录](README.md)
