> **一句话总结**：Agent 的 Demo 靠一次成功的调用，生产系统靠的是**把每一次可能失败的环节都准备好降级路径**——数据源要多级兜底并做有效性校验、配置要外置、状态要落盘、通知要限流、工具错误要变成可读的 Observation、凭证绝不能进源码。
> **前置知识**：[02-Function-Calling与工具调用](../02-工具与规划/02-Function-Calling与工具调用.md) 的工具协议与错误处理、[05-Agent的记忆与知识管理](../03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的状态持久化、[08-大宗商品价格监控Agent项目复盘](../07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md)。
> **学完能做到**：
> 1. 列出 Agent 生产化的六类风险，并为每一类给出至少一种的应对手段。
> 2. 写一个带「多源降级 + 有效性校验 + 退避重试 + 结构化日志」的外部调用封装。
> 3. 说清工具错误、解析错误、权限错误三类异常分别应该如何处理，以及为什么不能直接抛给用户。

---

## 1. 核心概念

### 1.1 从 Demo 到生产：六类风险

| 风险类别 | 具体表现 | 的应对 |
| --- | --- | --- |
| 数据源不可靠 | 目标接口改版、限流、返回空、单位变化 | 大宗商品项目三级数据源降级 + 价格合法性校验 |
| 模型不确定 | 输出格式不稳定、幻觉、策略选择失败 | LangChain `handle_parsing_errors=True`；策略选择器的默认值兜底 |
| 工具失败 | 网络超时、参数错误、返回异常结构 | Function Call 的 `try/except` + 把错误作为内容返回 |
| 状态丢失 | 进程重启后重复提醒、趋势数据断裂 | `gold_state.json` / `gold_history.json` 落盘 |
| 凭证与权限 | API Key 硬编码、SQL 越权 | 环境变量读取；只读账号 + `SELECT` 白名单 |
| 成本与延迟 | 重试风暴、上下文膨胀、多 Agent 轮数失控 | 步数上限、重排候选裁剪、通知限流 |

### 1.2 工程化的六个关注点

| 关注点 | 目标 | 典型手段 |
| --- | --- | --- |
| 可用性 | 单点失败不导致整体失败 | 多级降级、超时、重试、熔断 |
| 正确性 | 错误数据不进入决策链路 | 有效性校验、单位/量纲检查、白名单 |
| 可观测 | 出问题能定位 | 结构化日志、请求耗时、完整轨迹打印（`verbose`） |
| 可配置 | 不改代码即可调整行为 | 配置文件外置 + 代码内默认值 |
| 幂等与恢复 | 重启/重跑不产生副作用 | 状态落盘、`upsert` 覆盖、去重键 |
| 安全合规 | 最小权限、脱敏 | 环境变量、只读凭证、入盘前脱敏 |

### 1.3 大宗商品监控项目里的工程要素清单

这个只有 5 个文件、200 行有效代码的小项目，恰好把 Agent 工程化的主要骨架都演示了一遍：

| 文件 | 工程职责 | 对应上面的关注点 |
| --- | --- | --- |
| `config.json` | 阈值、检查间隔、通知间隔、推送 Key | 可配置 |
| `main_monitor.py` | 多源抓取 + 校验 + 状态判定 + 通知 | 可用性 / 正确性 / 幂等 |
| `gold_state.json` | 上次价格、状态、提醒时间 | 状态恢复 |
| `gold_history.json` | 时间序列 | 幂等与恢复 |
| `dashboard.py` | 可视化与状态展示 | 可观测 |
| `daily_report.py` | 汇总与推送 | 可观测 / 可配置 |
| `requirements.txt` | 依赖固定（`requests`、`flask`） | 环境可复现 |

---

## 2. 关键机制

### 2.1 数据源可靠性：多级降级

`get_gold_price()` 里定义了三组数据源，逐级尝试：

| 级别 | 变量 | 数据源 | 解析方式 |
| --- | --- | --- | --- |
| 一级 | `apis` | 工银积存金 API（`get_stats.php`、`get_latest_price.php`）、新浪财经 AU9999 / AU(T+D) / AU100g | JSON 解析 `current_price` / `price`；`hq.sinajs.cn` 按逗号切分取第 4 个字段 |
| 二级 | `alt_apis` | 和讯大宗商品、中金在线、上海大宗商品交易所、Wind 财经、腾讯财经 | 正则提取 `"price":"xx"` 或 JSON 路径 `data.goldprice` |
| 三级 | `more_apis` | 新浪财经大宗商品页面、金融界、同花顺 | 正则匹配「大宗商品现货」「AU9999…价格」附近的数字 |

每一级内部都是同一个模式：

```text
for api in <level>:
 try:
 response = session.get(api["url"])
 if response.status_code != 200: continue # 非 200 直接换下一个
 response.encoding = "utf-8"
 text = response.text.strip()
 if not text or text.endswith('=""'): continue # 空响应（新浪接口的典型形态）
 price = api["parser"](text) # 每个源自带解析器
 if price and price > 0:
 if price < 200: continue # 有效性阈值：剔除明显异常值
 return price
 except Exception as e:
 print("数据源 %s 获取失败: %s" % (api["name"], e))
 continue # 任何异常都不中断整体流程
```

三个设计点值得单独记住：

1. **「解析器」作为数据源的一部分**。每个数据源用 lambda 自带 `parser`，把「怎么取 URL」与「怎么从响应里取数」绑在一起，新增数据源只需往列表里加一项——这是很好的可扩展设计。
2. **有效性校验必须显式写**。`if price < 200: continue` 这一行是在防「解析器抓到了响应里的其它数字」（比如时间戳、成交量）。没有这道校验，一次解析偏差就会触发错误的买卖提醒。
3. **异常必须就地消化**。`except Exception` 里不 raise，只打印并 `continue`，保证「某一个源坏掉」不会让整个监控进程退出。

此外 `session.timeout = 15` 与统一的 `headers`（含 `User-Agent`、`Referer`）也是必要的：前者防挂死，后者是很多财经接口的最低要求。

### 2.2 配置外置与默认值兜底

`load_config()` 的双层设计：

```text
"""可靠的外部数据获取封装：多源降级 → 校验 → 退避重试 → 结构化日志。

依赖：仅标准库。
"""

import json
import logging
import random
import time
import urllib.error
import urllib.request

logging.basicConfig(
 level=logging.INFO,
 format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("price_fetcher")

MIN_VALID_PRICE = 200.0 # 低于该值视为解析异常
MAX_RETRY = 3
TIMEOUT = 15

def _parse_sina(text):
 parts = text.split(",")
 if len(parts) <= 3:
 raise ValueError("字段不足: %d" % len(parts))
 return float(parts[3])

def _parse_json_price(text):
 payload = json.loads(text)
 if not payload.get("success"):
 raise ValueError("接口返回 success=false")
 return float(payload["price"])

SOURCES = [
 {"name": "工银积存金-最新价", "url": "http://106.54.190.155:886/get_latest_price.php",
 "parser": _parse_json_price},
 {"name": "新浪财经-AU9999", "url": "http://hq.sinajs.cn/list=AU9999", "parser": _parse_sina},
]

def fetch_once(source):
 """抓取单个数据源，失败抛异常由上层处理"""
 request = urllib.request.Request(
 source["url"],
 headers={
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
 "Referer": "https://finance.sina.com.cn/",
 },
 )
 with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
 if response.status != 200:
 raise ValueError("HTTP 状态码 %d" % response.status)
 text = response.read().decode("utf-8", errors="ignore").strip()
 if not text or text.endswith('=""'):
 raise ValueError("响应为空")
 price = float(source["parser"](text))
 if price <= 0:
 raise ValueError("价格非正数: %s" % price)
 if price < MIN_VALID_PRICE:
 raise ValueError("价格低于有效阈值 %s: %s" % (MIN_VALID_PRICE, price))
 return price

def fetch_price_with_fallback(sources=None, max_retry=MAX_RETRY):
 """多源降级 + 每个源内部退避重试，全部失败返回 None"""
 sources = sources if sources is not None else SOURCES
 for source in sources:
 for attempt in range(1, max_retry + 1):
 try:
 price = fetch_once(source)
 logger.info("数据源 %s 成功，价格 %.2f", source["name"], price)
 return price
 except (urllib.error.URLError, ValueError, KeyError, json.JSONDecodeError) as exc:
 wait = min(2 ** attempt + random.random(), 10.0) # 指数退避 + 抖动
 logger.warning("数据源 %s 第 %d 次失败: %s（%.1fs 后重试）",
 source["name"], attempt, exc, wait)
 if attempt < max_retry:
 time.sleep(wait)
 logger.error("数据源 %s 重试耗尽，切换到下一个源", source["name"])
 logger.error("所有数据源均失败，本次抓取返回 None")
 return None

if __name__ == "__main__":
 print("最终获取到的价格:", fetch_price_with_fallback())
```

| 层次 | 作用 |
| --- | --- |
| 配置文件 | 运行期可调整（阈值、间隔、推送 Key），不必改代码 |
| 内置默认值 | 配置缺失/损坏时程序仍能启动，不会因一个 JSON 语法错误直接崩掉 |

配套的 `send_wechat_message()` 在 `sc_key` 为空时会打印「警告: 未配置 SCKEY，请在 config.json 中设置」并返回 `False`，而不是抛异常——**配置缺失属于预期内的运行态，不应作为崩溃处理**。

但这里也暴露了一个真实问题：`config.json` 里的 `sc_key` 是明文提交的（`"SCT<YOUR_SENDKEY>"`）。正确做法是把 `config.json` 加入 `.gitignore`，并提供一份 `config.example.json` 只含占位值。

### 2.3 状态持久化与幂等

`load_state()` / `save_state()` 保证「判断是否需要提醒」所需的全部上下文都在磁盘上：

```text
{"last_price": 888.71, "last_status": "normal", "last_notify_time": 0}
```

| 幂等来源 | 说明 |
| --- | --- |
| 状态文件 | 崩溃重启后仍知道上次的价格与状态，不会重复提醒 |
| 内容哈希主键 + `upsert` | RAG 的向量写入用 MD5 作主键，重复索引同一文档只覆盖不重复 |
| 按内容去重 | 检索结果与历史记录按内容去重，避免同一条信息被多次消费 |

### 2.4 通知限流与降噪

`monitor_gold()` 的双条件判定是「降噪」的标准范式：

```text
"""工具包装器：统一超时、重试、异常转结构化 Observation、调用统计。

依赖：仅标准库。
"""

import functools
import json
import logging
import time

logger = logging.getLogger("tool")

class ToolError(Exception):
 """工具级错误，会被包装成可读 Observation 返回给模型"""

def resilient_tool(max_retry=2, timeout_hint=10, retry_on=(ToolError,)):
 """装饰器：失败重试；最终失败时返回 {"error": ...} 而不是抛异常。"""

 def decorator(func):
 @functools.wraps(func)
 def wrapper(*args, **kwargs):
 last_error = None
 for attempt in range(1, max_retry + 1):
 started = time.time()
 try:
 result = func(*args, **kwargs)
 logger.info("tool=%s attempt=%d cost=%.3fs ok",
 func.__name__, attempt, time.time() - started)
 return result
 except retry_on as exc:
 last_error = exc
 logger.warning("tool=%s attempt=%d 可重试失败: %s",
 func.__name__, attempt, exc)
 time.sleep(0.5 * attempt)
 except Exception as exc: # 不可重试：立即收敛成 Observation
 last_error = exc
 logger.error("tool=%s 不可重试失败: %s", func.__name__, exc)
 break
 return json.dumps({"error": "%s 执行失败: %s" % (func.__name__, last_error)},
 ensure_ascii=False)

 wrapper.timeout_hint = timeout_hint
 return wrapper

 return decorator

@resilient_tool(max_retry=3)
def query_stock(sku):
 """查询库存（演示：SKU 以 '9' 开头时模拟瞬时故障）"""
 if sku.startswith("9"):
 raise ToolError("库存服务临时不可用")
 database = {"A1001": 12, "A1002": 0}
 if sku not in database:
 raise ValueError("未知 SKU: %s" % sku) # 业务错误，不重试
 return json.dumps({"sku": sku, "stock": database[sku]}, ensure_ascii=False)

if __name__ == "__main__":
 print(query_stock("A1001")) # 正常
 print(query_stock("A9999")) # 业务错误，一次失败即返回 error
 print(query_stock("90001")) # 重试 3 次后返回 error
```

| 条件 | 语义 | 防的是什么 |
| --- | --- | --- |
| A：`status != last_status` | 事件驱动，状态刚变化 | 漏报（该提醒的时候没提醒） |
| B：`now - last_notify_time > notify_interval` | 时间驱动，兜底周期提醒 | 长期停留在同一状态时的信息沉默 |
| 都不满足 | 静默 | 高频轮询下的重复轰炸 |

`config.json` 中 `check_interval_seconds` 为 5、`notify_interval_seconds` 为 3600，正好体现了「检查频率」与「打扰频率」解耦的设计：可以高频检查，但不能高频打扰。

### 2.5 工具错误的三种处理姿势

| 错误类型 | 例子 | 处理原则 | 的实现 |
| --- | --- | --- | --- |
| 工具执行失败 | 网络超时、文件不存在 | **转成结构化 Observation 回灌**，让模型决定下一步 | `send_message` 返回 `"错误：本地书信文件不存在，请先保存内容。"`；Function Call 的 `{"error": ...}` |
| 模型输出格式错误 | ReAct 格式不合法、参数不是 JSON | 捕获解析异常并提示模型重试 | LangChain `handle_parsing_errors=True` |
| 权限/安全错误 | 非 `SELECT` 语句、路径越界 | **直接拒绝**，不进入模型链路，并记录日志 | `ask_database` 里的 `SELECT` 白名单与单语句校验 |

关键区别：前两类错误要让**模型看到**（它是可恢复的，模型可能换参数重试）；第三类错误**不应该让模型绕过**（它是安全边界，必须硬失败）。

### 2.6 凭证、权限与最小暴露

| 风险 | /项目中的表现 | 正确做法 |
| --- | --- | --- |
| API Key 硬编码 | CrewAI 项目里 `to_addr` / `from_pwd` / `from_addr` 写在源码（部分打码） | 环境变量（`os.environ["OPENAI_API_KEY"]`）或密钥管理服务 |
| 配置中的推送 Key 明文入库 | `config.json` 里 `sc_key` 明文 | 加入 `.gitignore`，仓库只放 `config.example.json` |
| 让 LLM 生成的 SQL 直接执行 | `ask_database(query)` 直接 `cursor.execute(query)` | 只读账号 + `SELECT` 白名单 + 禁止多语句 + 超时 + 行数上限 |
| 用 `eval` 解析外部响应 | 天气示例的 `eval(response.text)` | 改用 `json.loads` 或 `ast.literal_eval` |
| 日志打印完整上下文 | debug 打印可能含用户隐私 | 日志分级；入盘前脱敏 |

### 2.7 可观测性

| 手段 | 的实例 | 作用 |
| --- | --- | --- |
| 分级日志 | `from base import logger, Config`，`logger.info/error` | 结构化输出，可按级别过滤 |
| 关键节点计时 | `processing_time = time.time() - start_time` | 发现慢查询与慢检索 |
| 完整轨迹打印 | LangChain `verbose=True`；CrewAI `verbose=2` | 定位「选错工具」「任务传递丢失」类问题 |
| 中间结果落盘 | GPT2 医疗机器人的 `samples.txt` 聊天记录 | 事后复盘生成质量 |
| 可视化看板 | `dashboard.py`（Chart.js + 120 秒自动刷新） | 让人一眼看到「当前状态是否正常」 |
| 依赖清单 | `requirements.txt` | 环境可复现 |

一个反例：大宗商品项目的日志全靠 `print`，且 `logs.txt` 是空文件——**打印到 stdout 在后台运行时等于没有日志**。生产环境应改为写入带时间戳的日志文件（或日志采集系统），并至少保留最近若干天。

### 2.8 模型侧的可靠性（训练与推理）

医疗问诊机器人的训练脚本（`train.py`）体现了模型侧的稳健性设计：

| 机制 | 实现 | 作用 |
| --- | --- | --- |
| 验证集评估 | 每个 epoch 后 `validate_epoch` 计算验证 loss | 及时发现过拟合 |
| 最优模型保存 | `if validate_loss < best_val_loss:` 保存 `min_ppl_model` | 最终用的是最好的检查点而非最后一个 |
| 梯度累积 | `if (batch_idx + 1) % gradient_accumulation_steps == 0` | 显存不足时模拟大 batch |
| 梯度裁剪 | `clip_grad_norm_(model.parameters(), args.max_grad_norm)` | 防梯度爆炸 |
| 学习率调度 | `get_linear_schedule_with_warmup` | 预热 + 线性衰减 |
| 损失忽略项 | `ignore_index=-100`，`labels.ne(ignore_index)` | padding 不参与损失与准确率计算 |

推理侧则用三个技巧控制生成质量：**屏蔽 `[UNK]`**（`next_token_logits[unk_id] = -float('Inf')`）、**重复惩罚**（对已生成 token 降权）、**`[SEP]` 作为停止符**（避免无限生成）。

### 2.9 成本与延迟控制

| 手段 | 的位置 | 效果 |
| --- | --- | --- |
| 意图分类后再决定是否检索 | RAG `QueryClassifier` | 通用知识跳过检索与重排 |
| 候选数量上限 | `context_docs[:conf.CANDIDATE_M]` | 控制 prompt 长度 |
| 少于 2 个文档时跳过重排 | `if len(parent_docs) < 2` | 省一次 CrossEncoder 推理 |
| 推理用 CPU/FP16 取舍 | `BGEM3EmbeddingFunction(use_fp16=False, device="cpu")` | 无 GPU 也能跑，代价是速度 |
| 检查间隔与通知间隔解耦 | `check_interval_seconds` / `notify_interval_seconds` | 高频感知、低频打扰 |
| 历史窗口截断 | `history[-max_history_len:]` / `[-500:]` | 防止数据与 token 无限增长 |

### 2.10 人机协同与降级出口

Agent 不可能永远答对，因此每个环节都要给出「人工接管」的出口：

| 场景 | 降级出口 | 的实现 |
| --- | --- | --- |
| 检索不到答案 | 明确回复并给人工联系方式 | RAG prompt 中的「信息不足，无法回答，请联系人工客服，电话：{phone}」 |
| LLM 调用失败 | 返回可读的失败文案，而不是 500 | `except Exception as e: answer = "抱歉，处理您的专业咨询问题时出错。请联系人工客服：{phone}"` |
| Agent 反复失败 | 步数上限后返回中间结果并提示人工 | `max_iterations` / `max_steps` |
| 高风险动作（发信、写库） | 关键节点人工确认 | CrewAI 中 `allow_delegation` 与 `human` 工具 |

---

## 3. 可运行示例

### 3.1 多源降级 + 校验 + 退避重试的价格抓取器

**依赖**：仅标准库（用 `urllib` 替代 `requests`，演示同样的降级结构）。

```text
"""Agent 运行骨架：配置外置 + 状态落盘 + 步数上限 + 轨迹记录。

依赖：仅标准库。
"""

import json
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "agent_config.json")
STATE_FILE = os.path.join(BASE_DIR, "agent_run_state.json")

DEFAULT_CONFIG = {
 "max_steps": 5,
 "tool_timeout_seconds": 10,
 "notify_interval_seconds": 3600,
 "enable_retrieval": True,
}

def load_config(path=CONFIG_FILE):
 try:
 with open(path, "r", encoding="utf-8") as file:
 config = json.load(file)
 except (OSError, ValueError) as exc:
 print("配置加载失败，使用默认配置: %s" % exc)
 config = {}
 merged = dict(DEFAULT_CONFIG)
 merged.update(config) # 缺哪项补哪项，多余项忽略
 return merged

def load_state(path=STATE_FILE):
 try:
 with open(path, "r", encoding="utf-8") as file:
 return json.load(file)
 except (OSError, ValueError):
 return {"runs": 0, "last_success_time": 0}

def save_state(state, path=STATE_FILE):
 with open(path, "w", encoding="utf-8") as file:
 json.dump(state, file, ensure_ascii=False, indent=2)

def run_agent(goal, planner, tools, config=None):
 """planner(goal, facts, step) -> {"tool": name, "args": {...}} 或 None"""
 config = config or load_config()
 state = load_state()
 facts, trace = {}, []
 started = time.time()

 for step in range(1, int(config["max_steps"]) + 1):
 action = planner(goal, facts, step)
 if action is None:
 break
 name = action["tool"]
 if name not in tools:
 trace.append({"step": step, "error": "未知工具: %s" % name})
 break
 try:
 result = tools[name](**action["args"])
 except Exception as exc: # 工具错误 → Observation
 result = {"error": str(exc)}
 trace.append({"step": step, "tool": name, "args": action["args"], "result": result})
 if isinstance(result, dict) and not result.get("error"):
 facts.update(result)
 else:
 break # 关键步骤失败则停止，交人工处理
 else:
 trace.append({"step": None, "error": "达到最大步数仍未完成"})

 state["runs"] = state.get("runs", 0) + 1
 state["last_success_time"] = int(time.time())
 state["last_trace"] = trace
 save_state(state)

 return {
 "facts": facts,
 "trace": trace,
 "elapsed": round(time.time() - started, 3),
 "runs_total": state["runs"],
 }

if __name__ == "__main__":
 def planner(goal, facts, step):
 if "number" not in facts:
 return {"tool": "get_plane_number",
 "args": {"date": "2024-04-02", "start": "郑州", "end": "北京"}}
 return None

 TOOLS = {"get_plane_number": lambda **kw: {"date": kw["date"], "number": "1123"}}
 print(json.dumps(run_agent("查询航班号", planner, TOOLS), ensure_ascii=False, indent=2))
```

这段代码与项目的差别只有三处：把 `print` 换成 `logging`、把「一层 for」改成「每个源内退避重试」、把「静默 continue」改成显式 `logger.warning`——但这三处正是「能跑」与「可运维」的分界线。

### 3.2 工具包装器：超时、重试、错误转 Observation

**依赖**：仅标准库。可直接用于 [02](../02-工具与规划/02-Function-Calling与工具调用.md) 的 `available_functions` 注册表。

要点：**区分可重试异常与业务异常**。瞬时故障（`ToolError`）重试有意义；「SKU 不存在」这种业务错误重试一百次也不会成功，应立即返回结构化错误让模型自己修正参数。

### 3.3 一个可配置、可观测的 Agent 运行骨架

**依赖**：仅标准库。

落盘的是 `last_trace`——一旦线上出问题，可以直接翻出最后一次运行的完整动作序列，这比任何日志都直接。

---

## 4. 常见坑

| 现象 | 原因 | 解决 |
| --- | --- | --- |
| 单个数据源挂掉导致整个任务失败 | 没有降级链，或异常直接向上抛 | 多源列表 + 每个源内部 `try/except` + 全部失败才返回 `None` |
| 提醒错误的价格 | 解析器抓到了响应中的其它数字，缺少有效性校验 | 加取值范围/单位校验（如 `price < MIN_VALID_PRICE` 直接丢弃） |
| 重启后重复推送通知 | 状态存内存，重启即丢 | 状态落盘（`last_status` / `last_notify_time`） |
| 每 5 秒推送一次，用户被轰炸 | 检查频率与通知频率没有解耦 | 双条件判定：状态变化立即推，否则按 `notify_interval` 限流 |
| 配置文件写错程序完全起不来 | 配置读取失败时直接抛异常 | `load_config` 内置默认值，损坏时降级到默认配置 |
| 工具抛异常导致 Agent 崩溃 | 工具内部异常直接冒泡 | 包装器捕获并返回 `{"error": ...}`，让模型据此改参数或换路 |
| 业务错误被无限重试 | 没区分可重试与不可重试异常 | 瞬时故障（超时、限流）重试；业务错误（参数非法）立即返回 |
| 由 LLM 生成的 SQL 删了数据 | 直接执行模型输出的语句 | 只读账号 + `SELECT` 白名单 + 单语句校验 + 超时 + 行数上限 |
| 密钥出现在 Git 历史里 | 明文写进源码或 `config.json` | 环境变量 + `.gitignore` + `config.example.json`；已泄露的必须轮换 |
| 后台跑起来后什么日志都没有 | 用 `print` 输出到 stdout，日志文件是空的 | 改用 `logging` 写入文件，配置轮转 |
| Agent 无限循环刷 token | 没有步数上限，工具一直返回无效信息 | `max_iterations` / `max_steps` + 连续重复动作检测 |
| 检索结果过多导致答案变差 | 没有裁剪候选数量，噪声压过信号 | 统一在链路末端裁剪（`CANDIDATE_M`） |
| 用户遇到错误看到堆栈 | 异常直接抛到 API 层 | 上层兜底文案 + 人工客服出口，异常只进日志 |

---

## 5. 面试问答

<details>
<summary><strong>Q1：一个 Agent 服务上线前，你会做哪些可靠性加固？</strong></summary>

按失败面逐项加固。①外部依赖：为每个数据源准备多级降级链，每个源内部做超时与退避重试，并对返回值做业务校验（取值范围、单位、必填字段），全部失败时返回明确的可重试状态而不是脏数据。②模型依赖：设置步数上限与整体超时，把解析错误配置成「回灌给模型重试」，为分类/策略选择这类规划器准备安全默认值和输出白名单。③状态：把决策所需上下文（上次状态、上次通知时间）落盘，保证重启后行为一致、不重复产生副作用。④安全：凭证全部走环境变量，外部输入一律校验，模型生成的 SQL/命令走白名单与最小权限账号。⑤可观测：结构化日志、关键节点耗时、每次运行的完整轨迹落盘。⑥降级出口：任何环节失败都要有用户可读的兜底文案和人工接管路径。

</details>

<details>
<summary><strong>Q2：工具执行失败时，应该把异常抛给模型还是返回错误字符串？</strong></summary>

取决于错误性质。**可恢复类**错误（网络抖动、参数类型不对、资源暂时不可用、参数值不存在）应当转成结构化 Observation 返回给模型，例如 `{"error": "未知 SKU: A9999"}`——模型据此可以改用别的参数、换用另一个工具，或向用户追问，这正是 Agent 比固定流程更有价值的地方。**不可恢复/越界类**错误（权限不足、SQL 非 `SELECT`、路径穿越、未授权的写操作）必须硬失败并记录审计日志，不能让模型看到「绕过提示」，否则一次提示注入就可能拿到越权能力。另外要注意区分：可重试的瞬时错误应先在工具层重试（指数退避 + 抖动），重试耗尽后才转成 Observation。

</details>

<details>
<summary><strong>Q3：为什么说「检查频率」和「通知频率」必须解耦？</strong></summary>

因为二者的目标不同。检查频率服务于「及时发现状态变化」——价格可能几分钟内就跨过阈值，检查间隔必须短（项目里配成 5 秒）；通知频率服务于「不打扰用户」——同一状态的反复提醒没有新信息量，只会让人屏蔽通知（项目里配成 3600 秒）。如果用一个参数同时控制两者，要么检查太慢导致漏报，要么通知太频繁导致骚扰。实现上就是双条件判定：状态变化时立即通知（事件驱动），状态未变但距上次通知超过间隔时通知（时间驱动），两者都不满足就静默。

</details>

---

## 6. 自测题

<details>
<summary>参考答案</summary>

**1. 大宗商品监控项目的数据源降级分了几级？每一级各是什么？**

三级。一级 `apis`：工银积存金 API 两个端点、新浪财经 AU9999 / AU(T+D) / AU100g；二级 `alt_apis`：和讯大宗商品、中金在线、上海大宗商品交易所、Wind 财经、腾讯财经；三级 `more_apis`：新浪财经大宗商品页面、金融界、同花顺。每级内部逐源尝试，任一源成功即返回，全部失败则返回 `None` 并打印错误。

</details>

<details>
<summary>参考答案</summary>

**2. `if price < 200: continue` 这一行的作用是什么？删掉会有什么后果？**

它是有效性校验：低于 200 元/克的「价格」几乎可以断定是解析错误（例如正则抓到了响应里的序号、时间戳或其它数值）。删掉之后，错误的数值会进入状态判定逻辑，可能被当成「价格暴跌」而触发买入提醒，向用户推送完全错误的投资信号，同时污染 `gold_history.json` 与趋势分析。

</details>

<details>
<summary>参考答案</summary>

**3. 为什么 `load_config()` 要在 `except` 分支里返回一份默认配置，而不是直接 raise？**

因为配置缺失或语法错误属于预期内的运行态问题。监控脚本通常后台常驻、无人值守，如果因为一个 JSON 逗号错误就崩溃退出，就会静默失去监控能力。返回内置默认值可以让程序以安全参数继续运行，同时打印错误提示运维修复。这是「可用性优先」的典型取舍，前提是默认值本身是安全的（例如默认不推送、用保守阈值）。

</details>

<details>
<summary>参考答案</summary>

**4. GRPO/R1 之外，模型训练侧的三个稳健性设计是什么？（以医疗问诊机器人训练脚本为例）**

①验证集评估与最优模型保存：每个 epoch 后在验证集上算 loss，只有 `validate_loss < best_val_loss` 时才保存检查点，避免最终用的是过拟合的最后一个 epoch；②梯度累积与梯度裁剪：`gradient_accumulation_steps` 在显存不足时模拟大 batch，`clip_grad_norm_` 防止梯度爆炸导致训练发散；③学习率调度与 loss 忽略项：`get_linear_schedule_with_warmup` 做预热加线性衰减，`ignore_index=-100` 让 padding 位置不参与 loss 与准确率计算。

</details>

<details>
<summary>参考答案</summary>

**5. 为什么「日志只打印到 stdout」在后台服务里等于没有日志？**

因为通过 `nohup`、计划任务或进程管理器启动时，stdout 往往被重定向丢弃或只保留有限缓冲，进程崩溃后内容也随之丢失。项目里 `logs.txt` 是空文件正好说明了这一点。正确做法是用 `logging` 写出带时间戳与级别的文件日志，配置轮转（按大小或日期），关键节点（数据获取、判定、通知、异常）都留痕，并保证日志中不包含明文凭证与用户隐私。

</details>

---

## 7. 延伸阅读

- Anthropic, Building Effective Agents（工程取舍与常见模式） —— https://www.anthropic.com/engineering/building-effective-agents
- OpenAI, Production best practices —— https://platform.openai.com/docs/guides/production-best-practices
- LangChain, Error handling 与 `handle_parsing_errors` —— https://python.langchain.com/docs/how_to/tools_error/
- Google SRE Book（超时、重试、退避与熔断的经典论述） —— https://sre.google/sre-book/table-of-contents/
- Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection —— https://arxiv.org/abs/2302.12173
- OWASP Top 10 for LLM Applications —— https://owasp.org/www-project-top-10-for-large-language-model-applications/
- ：《第九章：大模型 Function Call 工具应用》；项目源码：大宗商品价格监控 Agent、GPT2 医疗问诊机器人

---

[⬅️ 返回本目录索引](README.md)
