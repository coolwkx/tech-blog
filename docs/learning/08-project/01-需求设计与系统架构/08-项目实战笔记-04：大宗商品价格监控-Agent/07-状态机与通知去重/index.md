---
article_id: kp-9c098264d036ffe9
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-21a1347a1b81
learning_sourceId: 21a1347a1b81
learning_order: 6
learning_objective: 理解并验证：状态机与通知去重
---

# 状态机与通知去重

> **学习目标**：能够解释「状态机与通知去重」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python `requests` 会话与超时、Web API 返回格式的解析技巧、简单的状态机与去重通知思想、Flask 路由与模板、`json` 文件持久化。
>
> **所属主题**：项目实战笔记 04：大宗商品价格监控 Agent · 核心实现

## 本次只学这一点

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

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/04-Agent系统/04-项目-大宗商品价格监控Agent.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「状态机与通知去重」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/04-Agent系统/04-项目-大宗商品价格监控Agent.md)
