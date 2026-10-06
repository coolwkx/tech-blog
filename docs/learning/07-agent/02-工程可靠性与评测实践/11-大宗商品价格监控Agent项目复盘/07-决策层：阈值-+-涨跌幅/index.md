---
article_id: kp-24f4ba593229e5a3
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-4cd0a37cb105
learning_sourceId: 4cd0a37cb105
learning_order: 6
learning_objective: 理解并验证：决策层：阈值 + 涨跌幅
---

# 决策层：阈值 + 涨跌幅

> **学习目标**：能够解释「决策层：阈值 + 涨跌幅」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的五要素、[05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的状态与历史分离、[07-Agent工程化与可靠性设计](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md) 的降级与限流。
>
> **所属主题**：-大宗商品价格监控Agent项目复盘 · 关键机制

## 本次只学这一点

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

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「决策层：阈值 + 涨跌幅」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md)
