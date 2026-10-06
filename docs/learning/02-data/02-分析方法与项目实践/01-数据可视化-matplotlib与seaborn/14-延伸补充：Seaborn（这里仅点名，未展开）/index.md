---
article_id: kp-33343eb72b8a59c0
learning_kind: article
learning_category: 02-data
learning_direction: practice
learning_topic: topic-71094c625b7f
learning_sourceId: 71094c625b7f
learning_order: 13
learning_objective: 理解并验证：延伸补充：Seaborn（这里仅点名，未展开）
---

# 延伸补充：Seaborn（这里仅点名，未展开）

> **学习目标**：能够解释「延伸补充：Seaborn（这里仅点名，未展开）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-NumPy数值计算](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)（`linspace`、`random`）；[07-Pandas分组聚合与透视](../../../../../02-data/02-NumPy与Pandas/07-Pandas分组聚合与透视.md)（`Series`/`DataFrame` 的 `.plot`）。
>
> **所属主题**：-数据可视化-matplotlib与seaborn · 可运行示例

## 本次只学这一点

> 以下 API **未在讲解**，属进阶延伸，考试/作业以 Matplotlib 为准。Seaborn 建立在 Matplotlib 之上并直接接受 DataFrame，在"按分类字段拆分绘图"场景下代码更短。

```python
import seaborn as sns, matplotlib.pyplot as plt
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei']; mpl.rcParams['axes.unicode_minus'] = False

sns.set_theme(style='whitegrid') # 相当于 seaborn 版的 rcParams
df = sns.load_dataset('tips') # 内置示例数据集

sns.scatterplot(data=df, x='total_bill', y='tip', hue='sex') # 散点 + 分类着色
sns.barplot(data=df, x='day', y='total_bill', hue='sex') # 自动分组的柱状图
sns.histplot(data=df, x='total_bill', bins=20, kde=True) # 直方图 + 核密度
sns.boxplot(data=df, x='day', y='total_bill') # 箱线图：分布与离群点
sns.heatmap(df.select_dtypes('number').corr, annot=True, cmap='coolwarm') # 相关性热力图
plt.show
```

分工：Seaborn 负责**统计图形的语义层**（自动分组、自动算置信区间、直接吃 DataFrame），Matplotlib 负责**底层渲染与精细控制**，两者可混用。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/03-可视化与统计/08-数据可视化-matplotlib与seaborn.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「延伸补充：Seaborn（这里仅点名，未展开）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/03-可视化与统计/08-数据可视化-matplotlib与seaborn.md)
