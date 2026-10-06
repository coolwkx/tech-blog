---
article_id: kp-8b498e1253c2276d
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-21a1347a1b81
learning_sourceId: 21a1347a1b81
learning_order: 0
learning_objective: 理解并验证：需求
---

# 需求

> **学习目标**：能够解释「需求」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python `requests` 会话与超时、Web API 返回格式的解析技巧、简单的状态机与去重通知思想、Flask 路由与模板、`json` 文件持久化。
>
> **所属主题**：项目实战笔记 04：大宗商品价格监控 Agent · 项目目标与业务背景

## 本次只学这一点

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

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/04-Agent系统/04-项目-大宗商品价格监控Agent.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「需求」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/04-Agent系统/04-项目-大宗商品价格监控Agent.md)
