---
article_id: kp-e784d146dea6d6cb
learning_kind: article
learning_category: 02-data
learning_direction: practice
learning_topic: topic-71094c625b7f
learning_sourceId: 71094c625b7f
learning_order: 12
learning_objective: 理解并验证：Pandas 集成绘图
---

# Pandas 集成绘图

> **学习目标**：能够解释「Pandas 集成绘图」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-NumPy数值计算](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)（`linspace`、`random`）；[07-Pandas分组聚合与透视](../../../../../02-data/02-NumPy与Pandas/07-Pandas分组聚合与透视.md)（`Series`/`DataFrame` 的 `.plot`）。
>
> **所属主题**：-数据可视化-matplotlib与seaborn · 可运行示例

## 本次只学这一点

```python
import pandas as pd, matplotlib.pyplot as plt
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei']; mpl.rcParams['axes.unicode_minus'] = False

gdp = pd.DataFrame({'中国': [100, 200, 350, 500], '美国': [400, 420, 450, 480],
'日本': [300, 280, 260, 240]}, index=[2016, 2017, 2018, 2019])
gdp.plot(legend=True, title='三国 GDP 趋势') # 多条折线并自动出图例
plt.xlabel('年份'); plt.ylabel('GDP'); plt.show

s = pd.Series([2.62, 1.44, 1.57, 2.02, 8.51, -1.23],
index=pd.date_range('2024-01-01', periods=6))
s.cumsum.plot(title='累计涨跌幅'); plt.show # 累计走势

pd.Series({'高价值': 355, '中价值': 1200, '低价值': 2400}) \
.plot(kind='pie', autopct='%1.1f%%', startangle=90)
plt.ylabel(''); plt.title('客户价值分层占比'); plt.show # 隐藏多余的 y 轴标签
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/03-可视化与统计/08-数据可视化-matplotlib与seaborn.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Pandas 集成绘图」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/03-可视化与统计/08-数据可视化-matplotlib与seaborn.md)
