---
article_id: kp-ae4f0bda230b1e8b
learning_kind: article
learning_category: 02-data
learning_direction: practice
learning_topic: topic-71094c625b7f
learning_sourceId: 71094c625b7f
learning_order: 2
learning_objective: 理解并验证：辅助功能 API 速查
---

# 辅助功能 API 速查

> **学习目标**：能够解释「辅助功能 API 速查」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-NumPy数值计算](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)（`linspace`、`random`）；[07-Pandas分组聚合与透视](../../../../../02-data/02-NumPy与Pandas/07-Pandas分组聚合与透视.md)（`Series`/`DataFrame` 的 `.plot`）。
>
> **所属主题**：-数据可视化-matplotlib与seaborn · 核心概念

## 本次只学这一点

| 功能 | API | 关键点 |
| --- | --- | --- |
| 自定义 x 轴刻度与标签 | `plt.xticks(x, labels)` | 标签数量必须与刻度数量一致，常用 `x[::5]` 抽稀 |
| 自定义 y 轴刻度 | `plt.yticks(y)` | 同上 |
| 网格 | `plt.grid(True, linestyle='--', alpha=0.5)` | `alpha` 是**透明度** 0~1，越小越淡 |
| 轴名称 | `plt.xlabel('时间')` / `plt.ylabel('温度')` | — |
| 标题 | `plt.title('...', fontsize=20)` | `fontsize` 控制字号 |
| 图例 | `plt.plot(..., label='上海')` + `plt.legend(loc='best')` | **只写 `label` 不会显示图例**，必须调 `legend` |
| 保存图片 | `plt.savefig('./test.png')` | 必须在 `show` **之前** |
| 多子图 | `fig, axes = plt.subplots(nrows, ncols, figsize=, dpi=)` | 返回画布与坐标系数组，用 `axes[i].set_xxx` |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/03-可视化与统计/08-数据可视化-matplotlib与seaborn.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「辅助功能 API 速查」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/03-可视化与统计/08-数据可视化-matplotlib与seaborn.md)
