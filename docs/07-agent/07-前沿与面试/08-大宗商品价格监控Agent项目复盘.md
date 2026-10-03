> **一句话总结**：`gold-monitor-v1.0` 是一个**规则驱动的监控 Agent**——它完整具备「感知（多源抓价格）→ 决策（阈值 + 状态机）→ 行动（推送 + 落盘）→ 记忆（状态与历史文件）」四段闭环，但决策规则是写死的 if/else，没有 LLM 参与；把它升级成真正的 LLM Agent，只需要把决策层换成模型调用，其余三层可以原样保留。
> **前置知识**：[01-Agent基础范式与ReAct循环](../01-基础范式/01-Agent基础范式与ReAct循环.md) 的五要素、[05-Agent的记忆与知识管理](../03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的状态与历史分离、[07-Agent工程化与可靠性设计](../04-评估与工程化/07-Agent工程化与可靠性设计.md) 的降级与限流。
> **学完能做到**：
> 1. 画出该项目的四层架构与数据流，逐文件说明职责。
> 2. 复现主循环的「阈值 + 状态变化 + 通知限流」决策逻辑，并解释每一个状态字段的必要性。
> 3. 指出代码中真实存在的 6 处工程缺陷（超时未生效、双份截断、路径不一致、明文密钥等）并给出修法。

---

## 1. 核心概念

### 1.1 项目概览

| 项目 | 内容 |
| --- | --- |
| 名称 | 大宗商品智能监控系统 v1.0 |
| 定位 | 定时抓取黄商品价格格 → 判断是否触发阈值 → 推送微信提醒 / 生成日报 / 提供走势图 |
| 运行方式 | `python main_monitor.py monitor`（常驻监控）、`python main_monitor.py`（单次查询）、`python dashboard.py`（Web 面板）、`python daily_report.py`（日报推送） |
| 依赖 | `requirements.txt`：`requests`、`flask` |
| 数据文件 | `config.json`（配置）、`commodity_state.json`（状态）、`commodity_history.json`（历史，运行后生成） |

README 中列出的七项功能，与代码的对应关系：

| 功能 | 实现位置 | 关键函数 |
| --- | --- | --- |
| 黄商品价格格自动监控 | `main_monitor.py` | `get_commodity_price()`、`monitor_commodity()` |
| Server酱微信提醒 | `main_monitor.py` / `daily_report.py` | `send_wechat_message()` / `send_wechat()` |
| 防重复提醒状态保存 | `main_monitor.py` | `load_state()` / `save_state()` |
| 历史价格记录 | `main_monitor.py` | `check_price_once()`、`save_commodity_history()` |
| 大宗商品 AI 趋势分析 | `ai_analysis.py` | `analyze_gold()` |
| 每日微信大宗商品日报 | `daily_report.py` | `create_daily_report()` |
| Web 走势图面板 | `dashboard.py` | `index()` + `render_template_string` |

### 1.2 文件职责

| 文件 | 行数（约） | 职责 | 依赖 |
| --- | --- | --- | --- |
| `main_monitor.py` | 447 | 抓价、状态判定、推送、历史记录、日报生成函数 | `requests`、`json`、`time`、`re` |
| `ai_analysis.py` | 88 | 读取历史做趋势/风险/操作参考分析 | `json`、`time` |
| `daily_report.py` | 170 | 生成日报文本并推送 | `requests`、`json` |
| `dashboard.py` | 178 | Flask + Chart.js 走势图面板 | `flask` |
| `config.json` | 8 | 阈值、间隔、推送 Key | — |
| `commodity_state.json` | 5 | 上次价格、状态、提醒时间 | — |
| `commodity_history.json` | — | 时间序列 | — |

### 1.3 它算不算 Agent？

用 [01](../01-基础范式/01-Agent基础范式与ReAct循环.md) 的五要素逐个对照：

| 要素 | 项目中的对应物 | 是否具备 |
| --- | --- | --- |
| Prompt | 无（没有自然语言指令） | ❌ |
| LLM | 无（`ai_analysis.py` 是纯规则计算，名字里的「AI」是营销用语） | ❌ |
| Memory | `commodity_state.json` + `commodity_history.json` | ✅（外部状态/历史记忆） |
| Planning | 固定的阈值规则 `price < buy_threshold` / `price > sell_threshold` | ⚠️ 有决策，但规则由人写死 |
| Action | `requests.post` 推送微信、写 JSON 文件 | ✅ |

结论：它是一个**规则驱动的感知—决策—行动循环**，属于 [01](../01-基础范式/01-Agent基础范式与ReAct循环.md) 1.2 节里的「反应型 Agent」——根据当前环境状态做出直接反应（温度调节器那一类），而不是目标导向型 Agent。这个判断很重要：**它已经具备 Agent 的骨架，缺的只是「规划由模型生成」这一层**。也正因如此，它非常适合作为「手写循环 → LLM 驱动循环」的改造起点。

### 1.4 状态机的三个状态

| 状态 | 触发条件 | 通知标题 | 颜色隐喻 |
| --- | --- | --- | --- |
| `normal` | `buy_threshold <= price <= sell_threshold` | 无 | — |
| `buy` | `price < buy_threshold`（默认 800） | 🟡 大宗商品买入提醒 | 黄色（机会） |
| `sell` | `price > sell_threshold`（默认 900） | 🔴 大宗商品卖出提醒 | 红色（风险） |

注意 `> sell` 与 `< buy` 都是**严格不等号**，等于阈值时归为 `normal`——这类边界值必须在文档里写清楚，否则「价格正好 800」时系统沉默会让人以为坏了。

---

## 2. 关键机制

### 2.1 主循环 `monitor_commodity()`

```text
读取 config → 取 buy/sell 阈值、check_interval、notify_interval
读取 state → last_price / last_status / last_notify_time
while True:
 price = get_commodity_price() # 感知（多源降级）
 if price is not None:
 change = (price - last_price) / last_price * 100
 status, title, content = 阈值判定(price)
 if status != last_status: # 条件 A：状态变化 → 立即提醒
 推送(title, content) → 更新 last_notify_time
 elif title and now - last_notify_time > notify_interval: # 条件 B：超时提醒
 推送(title, content) → 更新 last_notify_time
 else:
 打印「状态未变化，无需重复提醒」
 last_price, last_status = price, status
 保存 state
 打印「下次检查将在 X 分钟后进行」
 sleep(check_interval)
```

这个循环里有三个非常值得学习的工程细节：

1. **`get_commodity_price()` 返回 `None` 时不做任何状态修改**——异常情况不污染状态，下一轮重新尝试；
2. **`last_notify_time` 只在推送成功后更新**（`if title and send_wechat_message(...)`）——失败会自动触发下一轮重试；
3. **`save_state` 在每次循环结束时调用**，保证进程被 kill 时状态基本一致。

### 2.2 感知层：三级数据源降级

`get_commodity_price()` 的三级结构（详见 [07](../04-评估与工程化/07-Agent工程化与可靠性设计.md) 2.1）：

| 级别 | 变量 | 数据源与解析方式 |
| --- | --- | --- |
| 1 | `apis` | 工银积存金 `get_stats.php`（取 `current_price`）、`get_latest_price.php`（取 `price`）、新浪财经 `hq.sinajs.cn/list=AU9999 / AUTD / AU100G`（逗号切分取第 4 个字段） |
| 2 | `alt_apis` | 和讯大宗商品（正则 `"price"`）、中金在线（`data.goldprice`）、上海期货交易所（`AU9999` 后数字）、Wind 财经（`gold` 后数字）、腾讯财经 `qt.gtimg.cn/q=sh600019`（`~` 切分） |
| 3 | `more_apis` | 新浪财经大宗商品页面、金融界、同花顺（均为正则匹配中文关键词附近的数字） |

统一校验：`status_code == 200`、响应非空且不以 `=""` 结尾、解析结果为正数且 `>= 200`。任何一步不满足就换下一个源，异常被 `except` 捕获后 `continue`。

### 2.3 决策层：阈值 + 涨跌幅

```python
"""大宗商品监控 Agent 的离线复刻：感知 → 决策 → 行动 → 记忆。

依赖：仅标准库。
"""

import json
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "commodity_state.json")
HISTORY_FILE = os.path.join(BASE_DIR, "commodity_history.json")

DEFAULT_CONFIG = {
"buy_threshold": 800,
"sell_threshold": 900,
"check_interval_seconds": 5,
"notify_interval_seconds": 3600,
}
MAX_HISTORY = 500

# ---------------- 记忆层 ----------------
def _load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, ValueError):
        return default

    def load_state():
        return _load_json(STATE_FILE, {"last_price": None, "last_status": "normal",
    "last_notify_time": 0})

    def save_state(state):
        with open(STATE_FILE, "w", encoding="utf-8") as file:
            json.dump(state, file, ensure_ascii=False, indent=2)

            def append_history(price):
                history = _load_json(HISTORY_FILE, [])
                history.append({"time": time.strftime("%Y-%m-%d %H:%M:%S"), "price": price})
                history = history[-MAX_HISTORY:] # 统一截断阈值，避免两套阈值打架
                with open(HISTORY_FILE, "w", encoding="utf-8") as file:
                    json.dump(history, file, ensure_ascii=False, indent=2)
                    return history

                # ---------------- 感知层 ----------------
                def get_commodity_price(price_source):
                    """price_source 是一个可迭代的价格序列，模拟多源降级后的结果"""
                    for price in price_source:
                        if price is None or price <= 0:
                            continue
                        if price < 200: # 有效性校验
                            continue
                        return float(price)
                    return None

                # ---------------- 决策层 ----------------
                def get_price_change(current, last):
                    if not last:
                        return 0.0
                    return (current - last) / last * 100

                def decide(price, config):
                    if price < config["buy_threshold"]:
                        return "buy", "🟡 大宗商品买入提醒", "当前黄商品价格格：%.2f 元/吨\n价格低于买入参考价：%d 元/吨" % (
                    price, config["buy_threshold"])
                    if price > config["sell_threshold"]:
                        return "sell", "🔴 大宗商品卖出提醒", "当前黄商品价格格：%.2f 元/吨\n价格高于卖出参考价：%d 元/吨" % (
                    price, config["sell_threshold"])
                    return "normal", None, None

                # ---------------- 行动层 ----------------
                def send_wechat_message(title, content):
                    """真实实现为 requests.post(Server酱)；此处只打印，保证示例可离线运行"""
                    line = "[推送] %s\n%s" % (title, content)
                    try:
                        print(line)
                    except UnicodeEncodeError: # Windows GBK 控制台无法输出 emoji，退化为纯 ASCII
                        print(line.encode("ascii", "replace").decode("ascii"))
                        return True

                    # ---------------- 主循环 ----------------
                    def run_once(price, config=None, now=None):
                        config = config or DEFAULT_CONFIG
                        now = now if now is not None else time.time()
                        state = load_state()
                        change = get_price_change(price, state.get("last_price"))
                        status, title, content = decide(price, config)

                        notified = False
                        if status != state.get("last_status"):
                            if title and send_wechat_message(title, content):
                                state["last_notify_time"] = now
                                notified = True
                            elif title and now - state.get("last_notify_time", 0) > config["notify_interval_seconds"]:
                                if send_wechat_message(title, content):
                                    state["last_notify_time"] = now
                                    notified = True
                                else:
                                    print("状态未变化，无需重复提醒")

                                    state["last_price"] = price
                                    state["last_status"] = status
                                    save_state(state)
                                    append_history(price)
                                    return {"price": price, "status": status, "change": round(change, 2), "notified": notified}

                                def monitor(prices, config=None):
                                    """模拟常驻监控：把价格序列逐个喂给 run_once"""
                                    results = []
                                    for price in prices:
                                        print("\n=== 价格 %.2f ===" % price)
                                        results.append(run_once(price, config))
                                        return results

                                    if __name__ == "__main__":
                                        # 模拟一段行情：正常 → 跌破买入线 → 继续低位（不应重复提醒）→ 突破卖出线
                                        outcomes = monitor([880.0, 795.0, 790.0, 912.0])
                                        print("\n--- 决策轨迹 ---")
                                        for item in outcomes:
                                            print(item)
                                            print("\n历史记录条数:", len(_load_json(HISTORY_FILE, [])))
```

涨跌幅出现在两处：

| 位置 | 比较基准 | 语义 |
| --- | --- | --- |
| 通知内容「相比上次变化」 | `state["last_price"]`（上一轮检查） | 相邻两次检查（默认 5 秒）的变化率 |
| `ai_analysis.py`「近期涨跌」 | `recent[0]`（最近 12 条中最早一条） | 约 1 分钟的区间涨跌 |

前者的语义偏弱：在 `check_interval_seconds=5` 的配置下，它反映的是 5 秒内的价格抖动，对用户几乎没有参考价值。**更好的做法是引入「基准价」概念**——例如记录 24 小时前或当日开盘价，让「相比上次」变成「相比昨日」，同时把 `last_price` 与 `baseline_price` 分开存储。

### 2.4 行动层：推送与落盘

| 动作 | 实现 | 返回判定 |
| --- | --- | --- |
| 微信推送 | `POST https://sctapi.ftqq.com/{sc_key}.send`，`data={"title": ..., "desp": ...}` | `result.get("code") == 0` 视为成功 |
| 写状态 | `json.dump(state, f, ensure_ascii=False, indent=2)` | 覆盖写 |
| 写历史 | 追加一条 `{"time": ..., "price": ...}` 后截断再覆盖写 | 覆盖写 |
| 保存聊天风格文本 | 无 | — |

`send_wechat_message()` 的三个防御：`sc_key` 为空时打印警告并返回 `False`；`requests.post(..., timeout=10)` 显式设置超时；整个调用包在 `try/except` 中，返回布尔值供调用方决定是否更新 `last_notify_time`。**这是项目里写得最规范的一个函数**。

### 2.5 记忆层：状态与历史分离

```json
// commodity_state.json —— 只关心最新值
{"last_price": 888.71, "last_status": "normal", "last_notify_time": 0}

// commodity_history.json —— 时间序列
[{"time": "2026-07-08 23:40:48", "price": 888.71},
 {"time": "2026-07-08 23:44:11", "price": 888.71}]
```

两者的读取方式完全不同：

| 文件 | 读取者 | 读取方式 |
| --- | --- | --- |
| `commodity_state.json` | `monitor_commodity` | `state.get("last_price")` 等，单值查询 |
| `commodity_history.json` | `ai_analysis`、`daily_report`、`dashboard` | 全量载入后切片（`prices[-12:]`、`history[-50:]`、按日期前缀过滤） |

这种划分是通用的：**「决策所需的最新事实」与「分析所需的历史序列」应当分文件存放**，因为前者的读写频率高、体积恒定，后者体积持续增长且需要截断策略。

### 2.6 呈现层：Flask + Chart.js 面板

`dashboard.py` 用 `render_template_string(HTML, ...)` 把内联模板渲染出来，要点：

| 设计 | 实现 | 效果 |
| --- | --- | --- |
| 自动刷新 | `<meta http-equiv="refresh" content="120">` | 每 2 分钟整页刷新，无需前端轮询代码 |
| 折线图 | Chart.js，`labels = [x["time"][11:16] for x in recent]` | 横轴只显示 `HH:MM` |
| 参考线 | `Array(count).fill(buy)` / `.fill(sell)`，`borderDash: [5,5]` | 虚线标出买卖阈值 |
| 状态文案 | `current > sell` → 🔴；`current < buy` → 🟢；否则 ➡️ | 一眼可读 |
| 数据裁剪 | `recent = history[-50:]`，列表只显示最近 10 条 | 控制渲染量 |
| 容错 | `load_json` 失败返回 `{}`，`if history:` 分支兜底 | 数据文件缺失时页面仍可打开 |

面板的三条曲线正好对应 Agent 的三类信息：**实际状态（价格）**、**决策边界（阈值线）**、**决策历史（状态文案）**——这是任何监控类 Agent 都应具备的可视化最小集。

### 2.7 日报层

`daily_report.py` 与 `ai_analysis.py` 的关系是「复用 + 组合」：

```text
create_daily_report():
 history = load_history()
 today = time.strftime("%Y-%m-%d")
 prices = [x["price"] for x in history if x["time"].startswith(today)]
 if not prices: # 当天无数据 → 退回最近 20 条
 prices = [x["price"] for x in history[-20:]]
 report = 今日价格 + 最高 + 最低 + 涨跌
 report += analyze_gold(history) # 拼接趋势/风险/操作参考
 report += "⚠️ 以上内容仅为行情分析，不构成投资建议"
 send_wechat("📊 大宗商品智能日报", report)
```

三个值得肯定的细节：**当天无数据时退回最近 20 条**（避免日报变空）、**固定追加免责声明**（金融场景的必要合规动作）、**日报与实时提醒共用同一套阈值语义**（用户不会看到冲突的结论）。

### 2.8 数据流全景

```text
 config.json（阈值/间隔/Key）
 │
 ▼
 [感知] 三级数据源 ──▶ get_commodity_price() ──▶ price
 │
 ▼
 [决策] 阈值 + 状态机 ──▶ status ∈ {normal, buy, sell} ──▶ 是否需要通知
 │ │
 ▼ ▼
 [记忆] commodity_state.json ◀── save_state() [行动] Server酱推送
 commodity_history.json ◀── 追加 + 截断
 │
 ┌────────────────────┼────────────────────┐
 ▼ ▼ ▼
 ai_analysis.py daily_report.py dashboard.py
 （趋势/风险/参考） （日报 + 推送） （Flask + Chart.js）
```

---

## 3. 可运行示例

### 3.1 离线复刻：注入假价格源跑通全部四层

**依赖**：仅标准库（把网络抓取替换为可注入的价格序列，便于本地验证决策逻辑）。

```text
"""把大宗商品监控的决策层升级为 LLM Agent（保留原有感知/记忆/行动）。

依赖：pip install zhipuai python-dotenv
环境变量：ZHIPU_API_KEY
"""

import json
import os
from zhipuai import ZhipuAI

# 复用 3.1 中的记忆层与行动层：load_state / save_state / append_history / send_wechat_message

SYSTEM_PROMPT = """你是一名大宗商品行情监控助手。
你会收到当前价格、近期价格序列、用户的买入/卖出参考阈值，以及上一轮的判断状态。
请判断本轮应该处于哪种状态（normal / buy / sell），并给出不超过 80 字的分析。
必须基于给定的数据，不得编造未提供的行情信息。
只输出 JSON，格式为：
{"status": "normal|buy|sell", "reason": "简短分析", "suggest_notify": true|false}
"""

def build_user_prompt(price, history, config, last_status):
 recent = [item["price"] for item in history[-12:]]
 return json.dumps({
 "current_price": price,
 "recent_prices": recent,
 "buy_threshold": config["buy_threshold"],
 "sell_threshold": config["sell_threshold"],
 "last_status": last_status,
 "note": "阈值仅为参考线，若价格只是轻微越过阈值且近期无趋势，可建议不通知。",
 }, ensure_ascii=False)

def llm_decide(price, history, config, last_status, model="glm-4"):
 client = ZhipuAI(api_key=os.environ["ZHIPU_API_KEY"])
 messages = [
 {"role": "system", "content": SYSTEM_PROMPT},
 {"role": "user", "content": build_user_prompt(price, history, config, last_status)},
 ]
 try:
 response = client.chat.completions.create(
 model=model, messages=messages, temperature=0.1,
 response_format={"type": "json_object"},
 )
 payload = json.loads(response.choices[0].message.content)
 status = payload.get("status")
 if status not in ("normal", "buy", "sell"):
 raise ValueError("非法状态: %s" % status)
 return status, payload.get("reason", ""), bool(payload.get("suggest_notify", False))
 except Exception as exc: # 模型侧失败 → 回退到规则决策，保证系统可用
 print("LLM 决策失败，回退到规则决策: %s" % exc)
 return rule_fallback(price, config)

def rule_fallback(price, config):
 if price < config["buy_threshold"]:
 return "buy", "价格低于买入参考价（规则兜底）", True
 if price > config["sell_threshold"]:
 return "sell", "价格高于卖出参考价（规则兜底）", True
 return "normal", "价格处于正常区间（规则兜底）", False
```

预期输出（要点）：

```text
=== 价格 880.00 ===
状态未变化，无需重复提醒
=== 价格 795.00 ===
[推送] 🟡 大宗商品买入提醒
=== 价格 790.00 ===
状态未变化，无需重复提醒 # 状态仍是 buy，未到 notify_interval，不重复推送
=== 价格 912.00 ===
[推送] 🔴 大宗商品卖出提醒 # 状态变化，立即推送
```

第三轮不推送正是「防重复提醒」生效的证据。

### 3.2 升级为 LLM Agent：把决策层换成模型

保留感知/记忆/行动三层，只替换决策层——这是本项目最有价值的改造路径。**依赖**：`pip install zhipuai python-dotenv`；环境变量 `ZHIPU_API_KEY`。

改造的关键三点：

| 改造点 | 做法 | 收益 |
| --- | --- | --- |
| 决策由规则改为模型 | 把 `decide()` 换成 `llm_decide()` | 能结合近期序列做判断，而不只是单点比大小 |
| 输出结构化 | `response_format={"type": "json_object"}` + 白名单校验 | 保证下游可直接消费 |
| 保留规则兜底 | `except` 分支调用 `rule_fallback` | 模型不可用时监控不中断 |

后续还可以继续升级：把「抓价格」包装成 tool 让模型自主调用（见 [02](../02-工具与规划/02-Function-Calling与工具调用.md)），把「历史查询」做成 RAG 检索（见 [06](../03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md)），把「是否推送」变成需要人工确认的高风险动作（见 [07](../04-评估与工程化/07-Agent工程化与可靠性设计.md) 2.10）。

---

## 4. 常见坑

以下每一条都是本项目代码里**真实存在**的问题，适合作为代码评审练习。

| 现象 | 原因 | 解决 |
| --- | --- | --- |
| 外部请求可能永久挂起 | `session.timeout = 15` 只是给 Session 对象加了一个**普通属性**，`requests` 并不会读取它 | 在每次请求上显式传参：`session.get(url, timeout=15)` |
| 历史文件出现两份、数据对不上 | 同一份数据有两条写入路径：`check_price_once()` 用相对路径 `"commodity_history.json"`，`save_commodity_history()` 用绝对路径 `HISTORY_FILE` | 统一为单一常量（`os.path.join(os.path.dirname(__file__), "commodity_history.json")`），所有写入走同一个函数 |
| 历史长度在两个上限之间反复跳变 | 两处截断阈值不一致：`history[-500:]` 与 `history[-20000:]` | 抽成 `MAX_HISTORY` 常量，只保留一处截断逻辑 |
| 同一段分析逻辑维护两份 | `ai_analysis.analyze_gold()` 与 `daily_report.analyze_gold()` 实现几乎相同（近 12 条、±1% 趋势、0.98/1.02 风险线、±2% 建议） | 抽成公共模块，两个入口都 import 它 |
| 「相比上次变化」几乎没有意义 | `check_interval_seconds = 5`，涨跌幅基于上一轮 5 秒前的价格 | 引入基准价（昨日收盘 / 当日开盘 / 24 小时前），单独存储 `baseline_price` |
| 默认阈值不一致 | `load_config()` 默认 800/900，`check_price_once()` 默认 700/800 | 默认值只在配置模块定义一次，其它地方不重复 | 
| 面板上有计算了却不用的变量 | `dashboard.index()` 里的 `high` / `low` 计算后未传入模板 | 删除死代码，或把它展示到页面上 |
| 走势图横轴标签重复、点挤在一起 | `labels = x["time"][11:16]` 只到分钟，5 秒一条数据时同一分钟出现多个同标签点 | 标签用 `HH:MM:SS`，或在前端做降采样/按分钟聚合 |
| 后台运行没有任何日志 | 全部用 `print` 输出，`logs.txt` 是 0 字节空文件 | 改用 `logging` 写文件并轮转（见 [07](../04-评估与工程化/07-Agent工程化与可靠性设计.md) 2.7） |
| 推送 Key 明文提交到仓库 | `config.json` 里 `sc_key` 明文 | 加入 `.gitignore`，提供 `config.example.json`；已泄露的 Key 立即轮换 |
| 高频轮询触发风控 | `check_interval_seconds = 5`，一天约 1.7 万次请求 | 按数据源实际更新频率调整（如 30–60 秒），并加请求头与随机抖动 |
| 微信推送失败被静默忽略 | `send_wechat_message` 返回 `False` 时只更新状态，没有告警链路 | 连续 N 次推送失败时记录错误并（可选）改用备用通道 |
| 日报里混用「当天数据」与「全量历史」 | `create_daily_report` 用当天价格算涨跌，但 `analyze_gold(history)` 内部用的是全量历史最近 12 条 | 明确文档化各统计口径，或让 `analyze_gold` 接收明确的子序列 |
| 抓取失败时状态不更新，历史也不记 | `if price is not None:` 之外没有 else 分支 | 增加连续失败计数器，达到阈值后推送「数据源异常」告警 |

---

## 5. 面试问答

<details><summary>参考答案</summary>

**Q1：这个项目算 AI Agent 吗？请给出判断依据。**

按对 Agent 的定义（能够感知环境、进行决策和执行动作的智能实体）以及五要素（Prompt / LLM / Memory / Planning / Action）来看，它只具备三个半要素：Memory（`commodity_state.json` 与 `commodity_history.json` 提供状态与历史）、Action（推送微信、写文件）、以及由人写死的 Planning（阈值比较），缺少 Prompt 与 LLM。因此它是一个**规则驱动的反应型 Agent**（与温度调节器同类），`ai_analysis.py` 里的「AI」只是规则计算加文案，没有任何模型调用。不过它的价值在于骨架完整：感知—决策—行动—记忆四层清晰分离，只要把决策层从 `decide()` 换成一次 LLM 调用，就能平滑升级为真正的 LLM Agent，其余三层可以原样复用。

</details>

<details><summary>参考答案</summary>

**Q2：为什么需要同时保存 `last_price`、`last_status`、`last_notify_time` 三个字段？各去掉一个会怎样？**

三者分别支撑三类判断。`last_price` 用于计算相比上次的涨跌幅，去掉后通知里就没有变化率信息，用户无法判断是急涨还是缓涨。`last_status` 用于判定「状态是否刚变化」，去掉后无法区分「刚刚跌破买入线」和「已经在买入区待了一整天」，会退化成每轮都推送或永远不推送。`last_notify_time` 用于对同一状态做周期提醒限流，去掉后要么在状态持续期间彻底沉默（漏报），要么按检查频率疯狂打扰（`check_interval_seconds=5` 意味着每 5 秒一条）。本质上，状态文件必须承载「一次决策所需的全部上下文」，才能让提醒行为与进程生命周期解耦、重启后保持一致。

</details>

<details><summary>参考答案</summary>

**Q3：如果让你把这个项目重构成生产可用版本，你会做哪五件事？**

①**统一配置与常量**：阈值、间隔、文件路径、截断上限全部收敛到一处，消除 700/800 与 800/900、相对/绝对路径、500/20000 三类不一致。②**修复外部调用的可靠性**：`session.get(url, timeout=15)` 显式超时，加指数退避重试与失败计数告警，把请求频率降到与数据源更新频率匹配。③**日志与可观测**：用 `logging` 写带时间戳的文件日志并轮转，给关键节点加耗时统计，连续失败时推送运维告警。④**安全与配置管理**：密钥迁移到环境变量，`config.json` 进 `.gitignore`，轮换已泄露的 Key。⑤**消除重复实现并补齐测试**：把重复的 `analyze_gold` 抽成公共模块，为「阈值判定 + 状态机 + 通知限流」这三段纯函数逻辑写单元测试（它们是整个系统唯一有决策风险的地方）。如果还要更进一步，则把决策层替换为可回退的 LLM 调用。

</details>

---

## 6. 自测题

<details><summary>参考答案</summary>

**1. 项目用哪几个文件承载「记忆」？各自的读取者是谁？**

`commodity_state.json`（`last_price` / `last_status` / `last_notify_time`，由 `monitor_commodity()` 通过 `load_state` / `save_state` 读写，决定是否提醒）与 `commodity_history.json`（时间序列，由 `ai_analysis.analyze_gold`、`daily_report.create_daily_report`、`dashboard.index` 读取，用于趋势分析、日报和走势图）。前者的读写频率高、体积恒定；后者持续增长、需要截断。

</details>

<details><summary>参考答案</summary>

**2. `session.timeout = 15` 为什么不能起到超时作用？**

`requests.Session` 的工作方式是在 `request()` / `send()` 时从调用参数中读取超时值；它会读取 `headers`、`auth`、`proxies`、`hooks` 等已知属性，但没有名为 `timeout` 的属性会被用于实际请求。给 Session 赋 `timeout` 只是新增了一个普通实例属性，请求时被完全忽略，因此网络挂起时仍会无限等待。正确写法是每次请求传参：`session.get(url, timeout=15)`。

</details>

<details><summary>参考答案</summary>

**3. 主循环里「条件 A / 条件 B」分别防的是什么问题？**

条件 A（`status != last_status`）是事件驱动，防止**漏报**——状态刚发生变化时必须立刻通知，不能等到下一个周期。条件 B（`now - last_notify_time > notify_interval`）是时间驱动，防止**长期沉默**——如果价格长期停留在买入区，只靠条件 A 就再也不会提醒，用户可能错过持续的建仓窗口。两者都不满足时静默，防止的是**重复轰炸**。这三条合起来实现「检查频率高、打扰频率低」的解耦。

</details>

<details><summary>参考答案</summary>

**4. 为什么「当天没有数据时退回最近 20 条」是一个好设计？**

因为日报的触发时间与数据产生时间不保证对齐（例如刚过零点、或当天尚未抓取到数据、或服务中途重启）。如果严格按当天日期过滤，日报会退化成一句「今日暂无数据」，用户拿不到任何信息，而这恰恰是他最需要确认系统是否正常的时刻。退回最近 20 条可以在数据缺失时仍然给出「最近一段时间的行情」，同时保留日期字段让用户自行判断数据新鲜度。

</details>

<details><summary>参考答案</summary>

**5. 把决策层换成 LLM 后，必须同时保留哪些东西？为什么？**

至少保留三样：①**规则兜底**——LLM 调用可能因网络、额度、限流失败，`except` 分支应回退到阈值规则，保证监控不中断；②**输出校验**——要求模型输出 JSON 并白名单校验 `status` 只能取 `normal` / `buy` / `sell`，非法值一律回退，因为下游状态机只认识这三个值；③**状态持久化与通知限流结构**——无论决策由谁产生，`last_status` / `last_notify_time` 的判定逻辑都不应改变，否则升级决策层会连带改变提醒行为，回归测试无从下手。这也是本项目作为改造起点的优势：决策层是唯一需要替换的部分。

</details>

---

## 7. 延伸阅读

- Server 酱（ServerChan）推送文档 —— https://sct.ftqq.com/
- Flask 快速入门（`render_template_string` 用法） —— https://flask.palletsprojects.com/en/stable/quickstart/
- Chart.js 折线图文档 —— https://www.chartjs.org/docs/latest/charts/line.html
- requests 高级用法（Session、超时与重试） —— https://requests.readthedocs.io/en/latest/user/advanced/
- 新浪财经行情接口 `hq.sinajs.cn` 说明（第三方整理） —— https://blog.csdn.net/weixin_43665996/article/details/108610467
- 本目录：[01-Agent基础范式与ReAct循环](../01-基础范式/01-Agent基础范式与ReAct循环.md)、[05-Agent的记忆与知识管理](../03-记忆与多智能体/05-Agent的记忆与知识管理.md)、[07-Agent工程化与可靠性设计](../04-评估与工程化/07-Agent工程化与可靠性设计.md)

---

[⬅️ 返回本目录索引](README.md)
