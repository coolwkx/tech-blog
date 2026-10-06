---
article_id: kp-d48ec7a1299a5275
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-21a1347a1b81
learning_sourceId: 21a1347a1b81
learning_order: 8
learning_objective: 理解并验证：历史留痕与每日日报
---

# 历史留痕与每日日报

> **学习目标**：能够解释「历史留痕与每日日报」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python `requests` 会话与超时、Web API 返回格式的解析技巧、简单的状态机与去重通知思想、Flask 路由与模板、`json` 文件持久化。
>
> **所属主题**：项目实战笔记 04：大宗商品价格监控 Agent · 核心实现

## 本次只学这一点

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

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/04-Agent系统/04-项目-大宗商品价格监控Agent.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「历史留痕与每日日报」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/04-Agent系统/04-项目-大宗商品价格监控Agent.md)
