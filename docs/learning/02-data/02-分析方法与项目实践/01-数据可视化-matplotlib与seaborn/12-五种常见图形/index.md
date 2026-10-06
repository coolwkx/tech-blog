---
article_id: kp-4543a3d260769fd8
learning_kind: article
learning_category: 02-data
learning_direction: practice
learning_topic: topic-71094c625b7f
learning_sourceId: 71094c625b7f
learning_order: 11
learning_objective: 理解并验证：五种常见图形
---

# 五种常见图形

> **学习目标**：能够解释「五种常见图形」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-NumPy数值计算](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)（`linspace`、`random`）；[07-Pandas分组聚合与透视](../../../../../02-data/02-NumPy与Pandas/07-Pandas分组聚合与透视.md)（`Series`/`DataFrame` 的 `.plot`）。
>
> **所属主题**：-数据可视化-matplotlib与seaborn · 可运行示例

## 本次只学这一点

```python
import numpy as np, matplotlib.pyplot as plt
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei']; mpl.rcParams['axes.unicode_minus'] = False

# 1. 柱状图：离散类别对比
plt.figure(figsize=(8, 5))
plt.bar(['A', 'B', 'C', 'D'], [3, 7, 5, 4], color='blue', width=0.6)
plt.title('各分类数值对比'); plt.xlabel('分类'); plt.ylabel('数值'); plt.show

# 2. 直方图：连续数据分布（bins 区间个数；alpha 透明度；rwidth 条形宽度占比）
plt.figure(figsize=(10, 6))
plt.hist(np.random.randn(500), bins=30, color='blue', alpha=0.7, rwidth=0.85)
plt.title('正态分布数据直方图'); plt.xlabel('取值'); plt.ylabel('频数')
plt.grid(True); plt.show

# 3. 饼图：占比结构（autopct 中的 %% 是"百分号字符"的转义）
plt.figure(figsize=(7, 7))
plt.pie([25, 35, 25, 15], labels=['分类A', '分类B', '分类C', '分类D'],
autopct='%1.1f%%', startangle=90, counterclock=False)
plt.title('各分类占比'); plt.show

# 4. 散点图：两变量关系
plt.figure(figsize=(8, 6))
plt.scatter([1, 2, 3, 4, 5], [2, 3, 5, 7, 11], color='red')
plt.title('两变量关系'); plt.xlabel('X'); plt.ylabel('Y'); plt.show

# 5. 折线图：趋势
days = range(1, 8)
plt.figure(figsize=(10, 5))
plt.plot(days, [1200, 1350, 1100, 1500, 1800, 1650, 2000], marker='o', label='日活')
plt.xticks(list(days), ['周一', '周二', '周三', '周四', '周五', '周六', '周日'])
plt.xlabel('星期'); plt.ylabel('活跃用户数'); plt.title('一周日活趋势')
plt.grid(True, linestyle='--', alpha=0.5); plt.legend; plt.show
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/03-可视化与统计/08-数据可视化-matplotlib与seaborn.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「五种常见图形」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/03-可视化与统计/08-数据可视化-matplotlib与seaborn.md)
