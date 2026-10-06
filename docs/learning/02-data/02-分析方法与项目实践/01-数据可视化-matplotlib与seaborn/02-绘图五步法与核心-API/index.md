---
article_id: kp-40486f6ec82dfaea
learning_kind: article
learning_category: 02-data
learning_direction: practice
learning_topic: topic-71094c625b7f
learning_sourceId: 71094c625b7f
learning_order: 1
learning_objective: 理解并验证：绘图五步法与核心 API
---

# 绘图五步法与核心 API

> **学习目标**：能够解释「绘图五步法与核心 API」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-NumPy数值计算](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)（`linspace`、`random`）；[07-Pandas分组聚合与透视](../../../../../02-data/02-NumPy与Pandas/07-Pandas分组聚合与透视.md)（`Series`/`DataFrame` 的 `.plot`）。
>
> **所属主题**：-数据可视化-matplotlib与seaborn · 核心概念

## 本次只学这一点

| 步骤 | API | 说明 |
| --- | --- | --- |
| ① 准备数据 | `x`、`y` | 列表、`range`、`ndarray` 均可 |
| ② 创建画布 | `plt.figure(figsize=(w,h), dpi=)` | `figsize` 单位英寸，决定长宽比；`dpi` 决定清晰度；返回 `Figure` 对象 |
| ③ 绘制图形 | `plt.plot/bar/hist/pie/scatter(...)` | 面向过程风格 |
| ④ 添加辅助元素 | `plt.xticks/yticks/grid/xlabel/ylabel/title/legend` | 见 1.3 |
| ⑤ 保存与显示 | `plt.savefig(path)` → `plt.show` | **顺序不能反** |

图像结构（自外向内）：`Figure`（整张画布）→ `Axes`（坐标系/绘图区，可多个）→ `Axis`（坐标轴）→ 刻度与刻度标签 → 数据图形 → 图例与标题。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/03-可视化与统计/08-数据可视化-matplotlib与seaborn.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「绘图五步法与核心 API」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/03-可视化与统计/08-数据可视化-matplotlib与seaborn.md)
