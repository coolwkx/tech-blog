---
article_id: kp-fcf09b921a9eb1ac
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-21a1347a1b81
learning_sourceId: 21a1347a1b81
learning_order: 10
learning_objective: 理解并验证：入口设计：一个脚本两种模式
---

# 入口设计：一个脚本两种模式

> **学习目标**：能够解释「入口设计：一个脚本两种模式」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python `requests` 会话与超时、Web API 返回格式的解析技巧、简单的状态机与去重通知思想、Flask 路由与模板、`json` 文件持久化。
>
> **所属主题**：项目实战笔记 04：大宗商品价格监控 Agent · 核心实现

## 本次只学这一点

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

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/04-Agent系统/04-项目-大宗商品价格监控Agent.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「入口设计：一个脚本两种模式」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/04-Agent系统/04-项目-大宗商品价格监控Agent.md)
