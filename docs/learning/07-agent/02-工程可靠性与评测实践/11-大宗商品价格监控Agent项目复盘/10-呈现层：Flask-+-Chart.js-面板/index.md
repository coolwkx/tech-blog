---
article_id: kp-7258e1f0a526d6ed
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-4cd0a37cb105
learning_sourceId: 4cd0a37cb105
learning_order: 9
learning_objective: 理解并验证：呈现层：Flask + Chart.js 面板
---

# 呈现层：Flask + Chart.js 面板

> **学习目标**：能够解释「呈现层：Flask + Chart.js 面板」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的五要素、[05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的状态与历史分离、[07-Agent工程化与可靠性设计](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md) 的降级与限流。
>
> **所属主题**：-大宗商品价格监控Agent项目复盘 · 关键机制

## 本次只学这一点

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

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「呈现层：Flask + Chart.js 面板」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md)
