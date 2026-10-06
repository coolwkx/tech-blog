---
article_id: kp-0516b4d895507118
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-4cd0a37cb105
learning_sourceId: 4cd0a37cb105
learning_order: 4
learning_objective: 理解并验证：主循环 monitor_commodity()
---

# 主循环 monitor_commodity()

> **学习目标**：能够解释「主循环 monitor_commodity()」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的五要素、[05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的状态与历史分离、[07-Agent工程化与可靠性设计](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md) 的降级与限流。
>
> **所属主题**：-大宗商品价格监控Agent项目复盘 · 关键机制

## 本次只学这一点

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

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「主循环 monitor_commodity()」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md)
