# 项目实战笔记 04：大宗商品价格监控 Agent

> **一句话总结**：一个只有几百行的轻量自动化 Agent —— 多数据源容灾抓价 → 状态机判断"该买/该卖" → Server酱推到微信 → JSON 落盘存历史 → Flask 出看板与日报，跑在无人值守的定时循环里。
> **前置知识**：Python `requests` 会话与超时、Web API 返回格式的解析技巧、简单的状态机与去重通知思想、Flask 路由与模板、`json` 文件持久化。

> 1. 设计一个"多数据源依次降级"的抓取器，让单点故障不致命；
> 2. 用状态文件实现"只在状态变化或冷却期满时通知"，避免消息轰炸；
> 3. 把脚本从"跑一次就完"升级成"可无人值守 + 可观测 + 有日报"的小系统。

## 1. 项目目标与业务背景

### 1.1 需求

大宗商品价格每天波动，钢材、铜等品种的报价直接关系到贸易与加工企业的成本。人工盯盘的问题很实在：

- 一天要看很多次，价格到了又想不起来看；
- 看到价格了还要自己算"比昨天涨了多少""离我的心理价位还差多少"；
- 想留个记录回头看走势，但懒得手工记。

所以需求可以拆成四件事：**盯价、判势、提醒、留痕**。

| 需求 | 本项目对应功能 | 实现文件 |
| --- | --- | --- |
| 盯价 | 定时循环抓取多源报价，容灾降级 | `main_monitor.py` |
| 判势 | 阈值状态机 + 近 12 期趋势判断 | `main_monitor.py` / `ai_analysis.py` |
| 提醒 | Server酱推送微信，状态变化或冷却期满才发 | `main_monitor.py` |
| 留痕 | `commodity_history.json` 追加历史、`commodity_state.json` 存状态 | 全部模块 |
| 展示 | Flask 看板画价格曲线 + 阈值参考线 | `dashboard.py` |
| 汇报 | 每日行情日报推微信 | `daily_report.py` |

### 1.2 为什么叫它 "Agent"

它具备 Agent 的最小闭环，虽然不含 LLM：

```text
感知（Perception） → 从 5+N 个数据源抓取当前报价
决策（Reasoning） → 与买入/卖出阈值比较，判断状态（buy/sell/normal）
记忆（Memory） → commodity_state.json 记上次价格与上次通知时间；commodity_history.json 记历史
行动（Action） → 通过 Server酱推送微信
```

把"Agent"理解成"感知-决策-记忆-行动"的循环，就能看清这类脚本和纯 CRUD 应用的区别，也更容易在面试里讲清楚它为什么值得写。

### 1.3 阈值语义

```json
{ "buy_threshold": 800, "sell_threshold": 900,
 "sc_key": "...", "check_interval_seconds": 300, "notify_interval_seconds": 3600 }
```

- `price < buy_threshold(800)` → 状态 `buy`，"价格低于买入参考价，可关注"；
- `price > sell_threshold(900)` → 状态 `sell`，"价格高于卖出参考价，注意风险"；
- 其余 → 状态 `normal`。

**注意措辞是"参考价"而不是"建议买入"**，`ai_analysis.py` 的输出末尾也固定带上"仅为行情分析，不构成投资建议"。做行情类的工具，这条免责声明不是形式主义——它明确了产品是"信息提示工具"而非"投资顾问"。

## 2. 技术架构

### 2.1 整体数据流

```text
 ┌───────────────────────────────────────────┐
 │ main_monitor.py │
 │ │
 定时循环 │ while True: │
 (check_interval) │ price = get_commodity_price ────────┐ │
 │ change = (price-last)/last*100 │ │
 │ 与 buy/sell 阈值比较 → status │ │
 │ ┌──────────────────────────────┐ │ │
 │ │ 状态变化? → 立即通知 │ │ │
 │ │ 状态未变但冷却期满? → 再通知 │ │ │
 │ │ 否则 → 跳过（不打扰用户） │ │ │
 │ └──────────────┬───────────────┘ │ │
 │ │ │ │
 │ save_state(commodity_state.json) │ │
 │ time.sleep(check_interval) │ │
 └───────────────────────────────────────┘ │
 │
 ┌───────────────────────────────────────────────────────┘
 │ get_commodity_price：三级数据源依次降级
 ▼
 ┌────────────────────────┐
 │ 一级：工银积存金 API×2 │ 106.54.190.155:886
 │ 新浪财经 AU9999/ │ hq.sinajs.cn
 │ AUTD/AU100G │
 ├────────────────────────┤ ← 任一成功即 return
 │ 二级：和讯/中金在线/ │ quote.hexun.com、data.cnfol.com
 │ 上金所/Wind/腾讯 │ sge.com.cn、qt.gtimg.cn
 ├────────────────────────┤
 │ 三级：新浪期货页/我的钢铁网/│ 页面正则抓取（最不稳定）
 │ 同花顺 │
 └───────────┬────────────┘
 │ 全部失败
 ▼
 return None → 本轮跳过，不写状态、不发通知
 │
 ┌──────┴──────────────────────────────┐
 ▼ ▼
 Server酱推送 commodity_history.json 追加
 sctapi.ftqq.com/<key>.send {time, price}，保留最近 N 条
 │ │
 ▼ ▼
 微信消息 dashboard.py (Flask)
 折线图 + 买入/卖出参考虚线
 meta refresh 120s 自动刷新
 │
 daily_report.py
 取当日数据 → 日报 + 趋势分析 → 推微信
```

### 2.2 状态机

```text
 price < buy_threshold
 ┌───────────────────────────────────────────┐
 │ ▼
 ┌─────────┐ buy_threshold ≤ price ≤ sell_threshold ┌────────┐
 │ buy │◀────────────────────────────────────────│ normal │
 └─────────┘ └────────┘
 ▲ ▲
 │ price > sell_threshold │
 └────────────────────────────────────────────────────┘
 （normal ↔ sell 同理）
```

通知规则（这是全项目最核心的一段业务逻辑）：

```text
if status != state["last_status"]: # 状态跃迁 → 立刻通知
 通知
elif now - state["last_notify_time"] > notify_interval:
 通知（冷却期满，提醒"还在低位/高位"）
else:
 不通知（避免刷屏）
```

### 2.3 多数据源分层

```text
apis (一级, 5 个) ：结构化的 JSON 接口 / 新浪行情字符串，最稳
alt_apis (二级, 5 个) ：财经站点接口，通常还能用
more_apis (三级, 3 个) ：直接正则抓 HTML 页面，最脆弱
```

## 3. 关键技术选型与理由

| 方案 | 优点 | 代价 | 本项目为何选它 |
| --- | --- | --- | --- |
| 多源依次降级（而不是单源） | 任一源挂掉系统仍可用 | 代码量翻几倍，各源响应格式都要写 parser | 免费行情接口极不稳定，单源必然三天两头断；这是本项目的**核心设计** |
| `requests.Session` 复用连接 | 复用 TCP 连接、统一超时与 headers | 需要注意线程安全（本项目单线程无妨） | 每轮要打多个源，复用 session 明显更快 |
| 自定义 `User-Agent` / `Referer` | 绕过部分站点的爬虫拦截 | 属于"弱对抗"，对方改策略就失效 | 财经接口对无 UA 的请求常直接返回空 |
| `parser` 写成 lambda 放在数据源字典里 | 新增一个源只需加一个 dict 项 | lambda 内异常难调试（但外层有 try） | 把"数据源 URL + 解析逻辑"聚成一处，扩展成本降到最低 |
| JSON 文件持久化（而非 SQLite/DB） | 零依赖、可直接用编辑器看、极易备份 | 并发写得加锁；数据量大后全量读写变慢 | 单机单进程、每次一条记录、量级在万条内，JSON 足够 |
| Server酱推微信 | 接入成本极低（一个 key + 一个 POST） | 依赖第三方服务，免费版有频次限制 | 比自建公众号/企业微信机器人快太多，适合个人项目 |
| 状态变化 + 冷却期双条件通知 | 既不漏关键变化，也不无限刷屏 | 需要维护状态文件，重启后要靠它恢复语义 | 通知类系统最容易犯的错就是"每 5 分钟发一条一样的消息" |
| Flask + `render_template_string` + Chart.js CDN | 不用前端工程链，单文件出图 | HTML 内嵌在 Python 字符串里，可维护性差；CDN 断网就没图 | 个人看板，一次成型即可；真要做产品再拆模板与前端 |
| `meta refresh 120s` 自动刷新 | 零 JS 实现自动更新 | 整页刷新、体验略糙 | 与"每 5 分钟抓一次价"的刷新频率匹配，够用 |
| 行情判断用规则而非 LLM | 确定、可解释、零成本、零延迟 | 无法理解新闻面、宏观因素 | 价格数字上的趋势判断本就是规则问题，没必要上模型 |

> **一个诚实的说明**：`ai_analysis.py` 名叫 "AI 分析"，但实现是**纯规则**（近 12 期最大/最小/涨跌幅 + 三档阈值判断），不含任何模型。这个命名要提前想清楚怎么解释——在面试里主动说"这是规则引擎，我把它叫 AI 是营销叫法；如果真要用 AI，应该接入 LLM 做新闻情绪分析"，比被面试官发现后解释要好得多。

### 3.1 为什么不干脆用交易软件的价格提醒？

因为要的是**多源容灾 + 可编程 + 可扩展**：交易软件的提醒只能用它自己的报价、只能设一个阈值、不能自定义"状态变化才提醒"的逻辑、也不能把历史留成自己的 JSON 做后续分析（比如接 LLM 做日报）。自己写 300 行的收益是**可控性和可组合性**。

## 4. 核心实现

### 4.1 多数据源降级抓取

```text
# main_monitor.py（精简）
def get_commodity_price:
 headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ... Chrome/120.0.0.0 Safari/537.36",
 "Referer": "https://finance.sina.com.cn/",
 "Accept": "*/*", "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
 "Accept-Encoding": "gzip, deflate", "Connection": "keep-alive",
 }
 session = requests.Session
 session.timeout = 15 # 统一超时，防止某个源把循环卡死
 session.headers.update(headers)

 apis = [
 {"name": "工银积存金 API",
 "url": "http://106.54.190.155:886/api/get_stats.php",
 "parser": lambda t: float(json.loads(t)["current_price"])
 if json.loads(t).get("success") else None},
 {"name": "新浪财经 AU9999",
 "url": "http://hq.sinajs.cn/list=AU9999",
 "parser": lambda t: float(t.split(',')[3]) if len(t.split(',')) > 3 else None},
 # ... AUTD / AU100G / get_latest_price.php ...
 ]

 # 三级数据源，结构完全一致，逐级降级
 for source_group in (apis, alt_apis, more_apis):
 for api in source_group:
 try:
 print("尝试数据源: %s" % api["name"])
 response = session.get(api["url"])
 if response.status_code != 200:
 continue

 response.encoding = "utf-8" # 中文站点必须显式指定编码
 text = response.text.strip
 if not text or text.endswith('=""'): # 新浪接口无数据时返回空串
 print("响应为空")
 continue

 price = api["parser"](text)
 if price and price > 0:
 # 关键：合理性校验，挡住"抓到了别的数字"
 if price < 200:
 continue
 return price
 else:
 print("解析失败")
 except Exception as e:
 print("数据源 %s 获取失败: %s" % (api["name"], e))
 continue

 print("错误: 所有数据源均失败，无法获取大宗商品价格")
 return None
```

**这段代码里有四个值得单独拿出来讲的设计**：

1. **`session.timeout = 15` 而不是依赖默认值**：`requests` 默认**没有超时**，一个卡住的源会让整个循环永久挂起。定时任务里这是致命问题。
2. **每个源独立 `try/except` 并 `continue`**：一个源的解析异常绝不能中断整轮降级。
3. **`if price < 200: continue`** 这条"魔法数字"校验：不同数据源返回的可能是"元/吨"，也可能是"元/千克"或股票价格（比如 `qt.gtimg.cn/q=sh600019` 返回的是宝钢股份的**股价**，不是钢价！）。用一个数量级下限把明显不合理的值挡掉，是**最便宜的防错手段**。更好的做法是按数据源分别设合理区间，而不是一个全局数字。
4. **`text.endswith('=""')`**：新浪 `hq.sinajs.cn` 在标的无数据时会返回 `var hq_str_AU9999="";`。不判断这一点，`t.split(',')[3]` 会抛 `IndexError`——虽然被 try 接住了，但会白白消耗一次请求。

### 4.2 状态机与通知去重

```text
# main_monitor.py: monitor_commodity（精简）
def monitor_commodity:
 config = load_config
 buy_threshold = config.get("buy_threshold", 800)
 sell_threshold = config.get("sell_threshold", 900)
 check_interval = config.get("check_interval_seconds", 300)
 notify_interval = config.get("notify_interval_seconds", 3600)

 state = load_state # 从 commodity_state.json 恢复：last_price / last_status / last_notify_time

 while True:
 price = get_commodity_price
 now = time.time

 if price is not None:
 change = get_price_change(price, state.get("last_price"))

 status, title, content = "normal", None, None
 if price < buy_threshold:
 status = "buy"
 title = "🟡 大宗商品买入提醒"
 content = ("当前大宗商品价格：%.2f 元/吨\n\n""价格低于买入参考价：%d 元/吨\n""相比上次变化：%.2f%%\n\n""请关注大宗商品行情变化。") % (price, buy_threshold, change)
 elif price > sell_threshold:
 status = "sell"
 title = "🔴 大宗商品卖出提醒"
 content = ("当前大宗商品价格：%.2f 元/吨\n\n""价格高于卖出参考价：%d 元/吨\n""相比上次变化：%.2f%%\n\n""请关注大宗商品行情变化。") % (price, sell_threshold, change)

 # ① 状态跃迁 → 立即通知
 if status != state.get("last_status"):
 if title and send_wechat_message(title, content):
 print("状态变化，已发送提醒")
 state["last_notify_time"] = now
 # ② 状态未变，但冷却期满 → 再提醒一次
 elif title and now - state.get("last_notify_time", 0) > notify_interval:
 if send_wechat_message(title, content):
 state["last_notify_time"] = now
 else:
 print("状态未变化，无需重复提醒")

 state["last_price"] = price
 state["last_status"] = status
 save_state(state) # 每轮落盘，重启后语义连续

 print("\n下次检查将在%d分钟后进行..." % (check_interval / 60))
 time.sleep(check_interval)
```

**注意 `status != last_status` 这个判断的语义**：它比较的是**离散状态**（buy/sell/normal），不是价格。这意味着价格从 799 涨到 801（buy → normal）会触发一次通知，但从 799 跌到 750 不会（还是 buy，得等冷却期）。这个设计是对的：用户关心"是否越过了参考线"，而不是"价格又动了多少"。

**`last_notify_time` 只在发送成功后才更新**：如果 Server酱挂了导致发送失败，下一轮还会重试，不会因为"记了时间"而永久丢失这条提醒。这是通知系统的常见正确姿势。

### 4.3 状态持久化

```text
STATE_FILE = os.path.join(os.path.dirname(__file__), "commodity_state.json")

def load_state:
 try:
 with open(STATE_FILE, "r", encoding="utf-8") as f:
 return json.load(f)
 except: # 文件不存在 / 内容损坏 → 用默认值
 return {"last_price": None, "last_status": "normal", "last_notify_time": 0}

def save_state(state):
 with open(STATE_FILE, "w", encoding="utf-8") as f:
 json.dump(state, f, ensure_ascii=False, indent=2)
```

```json
{ "last_price": 888.71, "last_status": "normal", "last_notify_time": 0 }
```

**为什么 `last_notify_time` 初始为 0**：`now - 0 > notify_interval` 恒成立，所以首次进入 buy/sell 状态时一定会触发通知（走的是"状态变化"分支，其实不影响）。这个默认值的选择让逻辑在任何状态下都不会"卡住不发"。

**为什么用 `except:` 宽异常**：状态文件是"可重建的派生数据"，读不到就从零开始，不应该因此让监控进程起不来。**但要区分清楚**：这是"缓存可丢"的场景；如果是用户的购买记录，就绝不能用裸 `except` 静默吞掉。

### 4.4 历史留痕与每日日报

```python
# main_monitor.py 尾部扩展
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "commodity_history.json")

def save_commodity_history(price):
 history = json.load(open(HISTORY_FILE, encoding="utf-8")) if os.path.exists(HISTORY_FILE) else []
 history.append({"time": time.strftime("%Y-%m-%d %H:%M:%S"), "price": price})
 history = history[-20000:] # 滚动窗口，防止文件无限增长
 json.dump(history, open(HISTORY_FILE, "w", encoding="utf-8"),
 ensure_ascii=False, indent=2)
```

```text
# daily_report.py（精简）
def create_daily_report:
 history = load_history
 today = time.strftime("%Y-%m-%d")
 prices = [x["price"] for x in history if x["time"].startswith(today)]

 if not prices: # 当日无数据（如凌晨执行）→ 退化为最近 20 条
 prices = [x["price"] for x in history[-20:]]

 current, high, low = prices[-1], max(prices), min(prices)
 change = (current - prices[0]) / prices[0] * 100

 report = f"📊 大宗商品每日行情\n\n日期：\n{today}\n\n当前价格：\n{current:.2f} 元/吨\n..."
 report += analyze_commodity(history) # 追加规则化的趋势/风险/操作参考
 report += "\n⚠️ 以上内容仅为行情分析，不构成投资建议\n"
 return report
```

趋势判断（`ai_analysis.py`）：

```text
def analyze_commodity:
 history = load_history
 if len(history) < 2:
 return "暂无足够数据进行趋势分析"

 prices = [x["price"] for x in history]
 current = prices[-1]
 recent = prices[-12:] if len(prices) >= 12 else prices # 近 12 期窗口
 high, low = max(recent), min(recent)
 change = (current - recent[0]) / recent[0] * 100

 trend = "📈 短线上涨趋势" if change >= 1 else \
 "📉 短线下跌趋势" if change <= -1 else "➡️ 短线震荡"

 risk = ("接近近期高位，注意追高风险" if current >= high * 0.98 else
 "接近近期低位，关注支撑" if current <= low * 1.02 else
 "价格处于正常波动区间")

 advice = ("涨幅较大，可关注回调机会" if change > 2 else
 "价格走弱，等待企稳" if change < -2 else
 "保持观察，等待趋势确认")
 ...
```

**`high * 0.98` 与 `low * 1.02` 是相对阈值而不是绝对阈值**：大宗商品价格在 400 和 900 时，"接近高位"的绝对差距完全不同。用百分比表达"接近"，才能让同一套代码在不同价格水平下都说得通。这是写规则引擎时很容易忽略的一点。

### 4.5 Flask 看板：把历史画成图

```text
# dashboard.py（精简）
@app.route("/")
def index:
 history = load_json(HISTORY_FILE)
 config = load_json(CONFIG_FILE)

 if history:
 recent = history[-50:] # 只看最近 50 个点
 prices = [x["price"] for x in recent]
 current = prices[-1]

 status = ("🔴 高于卖出参考区域" if current > config.get("sell_threshold", 900) else
 "🟢 接近买入参考区域" if current < config.get("buy_threshold", 800) else
 "➡️ 正常波动区间")

 labels = [x["time"][11:16] for x in recent] # 只取 "HH:MM" 做横轴
 values = prices
 else:
 current, status, labels, values, recent = 0, "暂无数据", [], [], []

 return render_template_string(
 HTML,
 price=f"{current:.2f}",
 update=time.strftime("%Y-%m-%d %H:%M:%S"),
 status=status,
 history=reversed(recent[-10:]), # 最近 10 条倒序展示
 labels=json.dumps(labels), # 直接注入 JS 数组
 values=json.dumps(values),
 count=len(values),
 buy=config.get("buy_threshold", 800),
 sell=config.get("sell_threshold", 900),
 )
```

前端用 Chart.js 画三条线：真实价格折线 + 买入参考虚线 + 卖出参考虚线。

```javascript
new Chart(ctx, {
 type:'line',
 data:{
 labels: {{labels|safe}}, // Jinja2 的 safe：不过 HTML 转义
 datasets:[
 { label:'大宗商品价格', data:{{values|safe}}, tension:0.3 },
 { label:'买入参考', data:Array({{count}}).fill({{buy}}), borderDash:[5,5] },
 { label:'卖出参考', data:Array({{count}}).fill({{sell}}), borderDash:[5,5] }
 ]
 }
});
```

**`{{labels|safe}}` 是必需的**：`json.dumps([...])` 产出的是 `["09:30", "09:35"]` 这样的 JS 数组字面量。如果用 Jinja2 默认的转义，引号会变成 `&quot;`，JS 语法直接报错。这也是"把 JSON 注入模板"时的标准坑——**要么用 `|safe`，要么改用 `tojson` 过滤器**（后者更安全，会额外处理 `</script>` 注入）。

**用 `Array(count).fill(buy)` 画参考线**：Chart.js 要求每条 dataset 的数据长度与 labels 一致，无法直接给一个标量。用 `fill` 生成一个常数序列是最简做法。

### 4.6 入口设计：一个脚本两种模式

```python
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        monitor_commodity # python main_monitor.py monitor → 常驻监控
    else:
        check_price_once # python main_monitor.py → 查一次就退出
```

**为什么保留"查一次"模式**：定时任务（Windows 计划任务 / Linux cron / GitHub Actions）通常是"执行一次就退出"的模型，不需要常驻进程。提供单次模式，脚本就能被任意外部调度器调用，灵活性远高于内置 `while True`。这是写自动化脚本时很实用的一个模式：

- 想常驻 → `python main_monitor.py monitor &`
- 想交给系统调度 → `python main_monitor.py`，让 cron 每 5 分钟调一次

## 5. 踩坑与解决

| 现象 | 根因 | 解决 | 如何预防 |
| --- | --- | --- | --- |
| 监控进程某天起完全不工作了 | `requests.get` 没有超时，某个数据源不响应把循环卡死 | 显式设 `session.timeout = 15` | **所有网络请求必须显式设超时**，默认值不是"安全值"而是"无限等待" |
| 抓到的"报价"只有 6 块钱 | 备用源 `qt.gtimg.cn/q=sh600019` 返回的是宝钢股份的**股票价格**，字段位置恰好也是 `split('~')[3]` | 加合理性下限校验 `if price < 200: continue` | 多源容灾时，各源的"数值语义"可能不同（元/吨 vs 元/千克 vs 股价）；校验要按源分别设，别用一个全局阈值 |
| 每 5 分钟收到一条一模一样的微信 | 没有状态记忆与冷却期判断，每轮都发 | 状态变化才发；状态未变则等 `notify_interval` | 通知系统的第一原则：**只在信息增量出现时打扰用户** |
| 重启后马上又发了一条重复通知 | 状态只存在内存变量里，重启即丢 | 状态落到 `commodity_state.json`，启动时 `load_state` 恢复 | 任何"去重/限流"逻辑依赖的状态都必须持久化 |
| 抓到的价格是 `None` 但程序继续往下跑，把 `None` 写进了历史 | 未对 `price is not None` 做分支保护 | 把整个判断+落盘逻辑放进 `if price is not None:` 块内 | 外部数据必须"先校验后使用"，`None` 要当成一个独立的失败态处理 |
| 新浪接口返回 `var hq_str_AU9999="";`，解析报 IndexError | 接口无数据时返回空串，字段数不足 | `if not text or text.endswith('=""'): continue` | 对接第三方接口时，**先摸清它的"空数据长什么样"**，再写 parser |
| 看板图表不显示，浏览器控制台报语法错误 | Jinja2 把 `json.dumps` 产出的双引号转义成了 `&quot;` | 模板里写 `{{labels|safe}}`（或改用 `tojson`） | 把 JSON 注入 `<script>` 时，转义问题一定要单独验证 |
| 中文站点抓到乱码 | 未设 `response.encoding`，`requests` 猜错编码 | 显式 `response.encoding = "utf-8"` | 中文页面/接口一律显式指定编码 |
| `commodity_history.json` 越跑越大，读写越来越慢 | 无上限追加 | `history = history[-20000:]` 滚动窗口 | 用文件做时序存储时，**必须设容量上限或做归档** |
| `sc_key` 这类密钥被提交到了 Git | 直接写进 `config.json` 并入库 | 把 `config.json` 加进 `.gitignore`，提供 `config.example.json` | 密钥与代码分离；仓库里只放示例值 |
| 价格明明越过了阈值却没提醒 | 阈值改动后忘记重启进程；或通知在异常中被跳过 | 每次发送失败时**不更新** `last_notify_time`，下轮自动重试 | 通知发出与"标记已发"必须在同一个成功判定内完成 |
| 数据源全部失败时静默无输出 | 只 `return None`，外层也没告警 | 打印明确错误 + 日志；重要场景可加"连续 N 次失败则告警" | **静默失败比报错更危险**，尤其是无人值守的定时任务 |

## 6. 可复用经验

1. **多数据源降级（fallback chain）是抓取类项目的标准骨架。** 把每个源写成 `{name, url, parser}` 三件套放进列表，外层统一处理"请求 → 校验 → 解析 → 成功即返回"，新增源只是加一行。这个模式可以直接复用到任何行情、天气、汇率、运价的抓取上。
2. **外部数据必须过"合理性校验"才能进业务逻辑。** 状态码 200 不代表内容可用；字段能解析出 float 不代表数值有意义。下限/上限校验、量纲检查、时间新鲜度检查，成本极低但能挡住大部分脏数据事故。
3. **通知类系统 = 触发条件 × 去重策略 × 持久化状态。** 三者缺一不可：没触发条件就没价值，没去重就变骚扰，没持久化就重启即失效。更成熟的做法还可以加"静默时段"（夜间不推送）和"分级通知"（越界一级 / 极端行情二级）。
4. **状态机和阈值参数要分离。** 状态定义（normal/buy/sell）写在代码里，阈值写在配置里。这样改参考价不需要改代码，也便于未来做"每人一套阈值"的个性化。
5. **规则引擎里"接近"要用相对量表达。** `current >= high * 0.98` 比 `current >= high - 5` 更能适应不同价格水平；同理，涨跌判断用百分比而不是绝对值。
6. **脚本要同时支持"常驻"和"跑一次"两种模式。** 一旦支持"跑一次"，就能被 cron、计划任务、GitHub Actions、Airflow 任意编排，比自己实现调度器灵活得多。
7. **把 JSON 文件当数据库是有边界的。** 单进程、低写入频率、单表、总量万级以内，JSON 完全够用且极其方便（能直接打开看、能直接进 Git 做 diff）。一旦出现并发写入、需要按时间范围查询、或数据超过几十万条，就该换 SQLite——迁移成本很低，收益明确。
8. **别把"AI"标签当装饰。** 这个项目的分析模块是纯规则。诚实地标注"规则引擎"，然后在有真实需求时（比如要分析新闻面、宏观数据）再接 LLM，比让名不副实的功能成为面试上的减分项要好。

## 7. 面试问答

<details>
<summary><b>Q1：你的多数据源容灾是怎么设计的？为什么不用数据库或消息队列？</b></summary>

**容灾设计**是三级降级链：

```text
一级（5 个）：结构化接口 —— 工银积存金 JSON API ×2、新浪财经行情串 AU9999 / AUTD / AU100G
二级（5 个）：财经站点接口 —— 和讯、中金在线、上海期货交易所、Wind、腾讯
三级（3 个）：HTML 页面正则抓取 —— 新浪期货页、我的钢铁网、同花顺
```

每一级内部按顺序尝试，任一个成功就立即 `return`，不再往下试。每个源独立 `try/except` + `continue`，单个源的网络异常或解析失败都不影响后续降级。全部失败则 `return None`，外层跳过本轮（既不写历史也不发通知），避免用脏数据污染状态。

为了让"新增一个源"的成本降到最低，每个源被抽象成 `{name, url, parser}`：

```python
{"name": "新浪财经 AU9999",
"url": "http://hq.sinajs.cn/list=AU9999",
"parser": lambda t: float(t.split(',')[3]) if len(t.split(',')) > 3 else None}
```

再加两道校验：响应非空（新浪无数据时返回 `=""`）、数值在合理量级（`price > 200`）。

**为什么不用数据库或消息队列**：

- 数据规模：每 5 分钟一条，一年约 10 万条，单机 JSON 滚动保留 2 万条完全够；
- 访问模式：只有"追加 + 全量读最近 N 条"，没有复杂查询、没有并发写；
- 部署成本：个人项目的核心诉求是"随便扔到哪台机器都能跑"。引入 DB 意味着要装、要备份、要迁移，收益为零；
- 可调试性：`commodity_history.json` 能直接用记事本打开、能进 Git 做 diff，这是 DB 给不了的。

**边界在哪**：一旦出现多个进程并发写（比如同时跑监控和日报生成）、需要按时间范围或价格区间查询、或数据量突破几十万条，就该换 SQLite。JSON 读写是 O(文件大小) 的全量操作，而 SQLite 是 O(log n) 索引查询。迁移成本很低（`json.load` 换成 `sqlite3` 三行），所以"先用 JSON 后换 DB"是合理的演进路径，不是技术债。

</details>

<details>
<summary><b>Q2：怎么保证用户不被重复消息轰炸？</b></summary>

用一个**状态机 + 双条件触发 + 持久化状态**的组合。

**状态定义**：把价格映射成三个离散状态 `normal / buy / sell`，而不是直接看价格数值。

**双条件触发**：

```python
if status != state["last_status"]: # 条件一：状态跃迁
 通知
elif now - state["last_notify_time"] > notify_interval: # 条件二：冷却期满
 通知
else:
 跳过
```

- 条件一保证**不漏**：只要越过参考线就立刻告知；
- 条件二保证**不过量**：如果价格长期在低位徘徊，最多每小时（`notify_interval=3600`）提醒一次，而不是每 5 分钟一次。

**持久化**：`last_status` 和 `last_notify_time` 存在 `commodity_state.json`，进程重启后语义连续。这一点很关键——如果用内存变量，每次重启都会"忘记上次已经提醒过"，立刻再发一条。

**两个细节决定成败**：

1. **`last_notify_time` 只在发送成功后才更新。** 如果 Server酱临时挂了，`send_wechat_message` 返回 `False`，就不更新时间戳，下一轮自动重试。反过来写（先更新时间再发）会导致消息永久丢失。
2. **比较的是状态而不是价格。** 价格从 799 涨到 801（buy→normal）触发一次通知，从 799 跌到 750（仍是 buy）不触发。这符合用户心智："我关心的是有没有越过我的参考线"。

**还能怎么加强**：

- **静默时段**：23:00–07:00 不推送，攒到早上发汇总；
- **分级通知**：轻微越界用普通消息，极端行情（如单日跌 5%）用加急通道；
- **多通道降级**：微信失败后转邮件或短信，避免单通道故障导致提醒全丢；
- **通知日志**：记录每次发送的时间与结果，用户投诉"没收到"时能查证。

</details>

<details>
<summary><b>Q3：这个项目叫"大宗商品价格监控 Agent"，它算 Agent 吗？如果让你升级成真正的 AI Agent 会怎么做？</b></summary>

**先说结论：按"感知-决策-记忆-行动"的最小闭环定义，它算一个（非常朴素的）Agent；但它不含任何 LLM，所以不是当下语境里通常说的"智能体"。**

对照四个能力：

| 能力 | 本项目实现 | 局限 |
| --- | --- | --- |
| 感知 | `get_commodity_price` 从 13 个源降级抓价 | 只感知价格这一个标量信号 |
| 决策 | 阈值状态机 + 近 12 期规则判断 | 规则固定，不理解任何"为什么" |
| 记忆 | `commodity_state.json`（短期状态）+ `commodity_history.json`（长期历史） | 只存数值，没有语义记忆 |
| 行动 | Server酱推送 + 每天生成日报 | 行动空间只有"发消息"一种 |

**升级成真正的 AI Agent 的路径**，我会分三层来加：

**第一层：让"感知"更丰富。** 现在只看价格，但钢价受铁矿石价格、宏观需求、库存、地产开工等影响。接入新闻标题（财经 RSS / 财联社）、汇率、美债收益率，让 Agent 的输入从一维标量变成多模态信号。

**第二层：让"决策"从规则变成推理。** 把"价格 + 近期走势 + 今日相关新闻标题"拼成 prompt 交给 LLM，让它输出结构化的判断（趋势方向、置信度、主要驱动因素）。这里要用 **Function Calling / 结构化输出**把结论约束成 JSON schema，而不是让它自由发挥——因为下游要消费这个结论。同时保留规则引擎作为**基线**和**兜底**：LLM 不可用时退回阈值判断，这也让"加 LLM 到底有没有用"变得可对比。

**第三层：让"行动"和"记忆"闭环。** 用向量库存历史"判断 + 实际结果"的配对，让 Agent 能回溯"上次我判断会上涨，实际涨了吗"，从而在 prompt 里带上 few-shot 的历史战绩。这一步才真正把"自动化脚本"变成"能自我校准的系统"。

**但我会很谨慎地评估必要性。** 这个项目的核心价值是"及时、准确、不打扰"——三件事规则引擎都做得比 LLM 更好：更确定、更便宜、更快、零幻觉。LLM 的增量价值只在"解释为什么"和"综合非数值信号"上。所以正确的做法不是"为了叫 Agent 而加 LLM"，而是**先明确哪一环规则做不好，再在那儿引入模型**。

面试里我倾向于这样表述："它是一个自动化监控 Agent；AI 部分目前是规则引擎。我认为在这个规模上规则比 LLM 更合适，如果要加 LLM，我会加在新闻面理解和日报自然语言生成这两个环节，并保留规则作为基线和降级路径。"

</details>

## 8. 延伸阅读

- `requests` 官方文档：Session、Timeouts、`response.encoding` 的行为
- Server酱（ServerChan）推送 API 文档
- Chart.js 折线图配置：`borderDash`、`fill`、时间轴处理
- Flask 官方文档：`render_template_string`、Jinja2 的 `tojson` 过滤器与自动转义
- 本仓库同目录：[01-项目-法律咨询RAG问答系统](../01-问答与RAG系统/01-项目-法律咨询RAG问答系统.md)（对比"有 LLM 的系统"架构差异）
- 配套代码：`commodity-monitor-v1.0/main_monitor.py`、`ai_analysis.py`、`dashboard.py`、`daily_report.py`、`config.json`

---
[⬅️ 返回本目录索引](README.md)
