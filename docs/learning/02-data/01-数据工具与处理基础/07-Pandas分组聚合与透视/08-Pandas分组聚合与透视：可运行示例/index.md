---
article_id: kp-3fdffc9ecf395370
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-7b8856bc8b6a
learning_sourceId: 7b8856bc8b6a
learning_order: 7
learning_objective: 理解并验证：-Pandas分组聚合与透视：可运行示例
---

# -Pandas分组聚合与透视：可运行示例

> **学习目标**：能够解释「-Pandas分组聚合与透视：可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[06-Pandas数据清洗](../../../../../02-data/02-NumPy与Pandas/06-Pandas数据清洗.md)（索引、`loc/iloc`、缺失值、`merge`）；[05-NumPy数值计算](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md) 的聚合函数与 `np.where`。
>
> **所属主题**：-Pandas分组聚合与透视 · 可运行示例

## 本次只学这一点

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei']; mpl.rcParams['axes.unicode_minus'] = False

# ================= 0. 模拟优衣库门店销售明细 =================
df = pd.DataFrame({
'store_id': [1, 2, 3, 4, 5, 6, 7, 8],
'city': ['上海', '上海', '北京', '北京', '深圳', '深圳', '广州', '广州'],
'channel': ['线上', '线下', '线上', '线下', '线上', '线下', '线上', '线下'],
'gender_group': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
'customer': [120, 150, 90, 130, 200, 180, 160, 140],
'revenue': [24000.0, 31500.0, 16200.0, 26000.0, 44000.0, 37800.0, 33600.0, 29400.0],
'unit_cost': [12000.0, 18000.0, 8000.0, 14000.0, 22000.0, 19000.0, 17000.0, 15000.0],
})

# ================= 1. 分组对象与组内取值 =================
gb = df.groupby('gender_group') # DataFrameGroupBy（惰性）
print(type(gb)); print(gb['city']) # SeriesGroupBy
print(gb.get_group('Female')) # 取指定组的数据
gb2 = df.groupby(['gender_group', 'city'])
print(gb2.first, gb2.last) # 每组第一条 / 最后一条

# ================= 2. 分组聚合：三种等价写法 =================
print(df.groupby('city').customer.sum) # ① 链式
print(df.groupby('city').customer.agg('sum')) # ② agg + 函数名
print(df.groupby('city').agg({'customer': 'sum'})) # ③ agg + 字典

# 按城市、渠道分组，分别算销售额均值与成本总和（不同列不同函数）
print(df.groupby(['city', 'channel']).agg({'revenue': 'mean', 'unit_cost': 'sum'}))

# 同一列多种聚合
print(df.groupby('city').agg({'revenue': ['sum', 'mean', 'max'],
'customer': ['sum', 'count']}))

# 命名聚合：直接指定结果列名，避免 MultiIndex 列
print(df.groupby('city', as_index=False).agg(
总销售额=('revenue', 'sum'), 平均销售额=('revenue', 'mean'), 门店数=('store_id', 'nunique')))

# size 与 count 的差异
print(df.groupby('city').size) # 每组行数
print(df.groupby('city')['revenue'].count) # 每组 revenue 的非空个数

# ================= 3. 分组过滤 filter 与分组转换 transform =================
# 保留"该城市平均销售额 > 30000"的所有明细行
print(df.groupby('city').filter(lambda s: s['revenue'].mean > 30000))
# 换 SQL 思路：select * from df where city in
# (select city from df group by city having avg(revenue) > 30000);

# transform：返回与原表等长的结果，常用于"组内均值填充"
df2 = df.copy
df2['city_avg'] = df2.groupby('city')['revenue'].transform('mean')
df2['revenue_ratio'] = df2['revenue'] / df2['city_avg'] # 相对本城市均值的倍数
print(df2)

# apply：最灵活（可返回任意形状）但性能最差；能用 agg/transform 就不要用 apply
print(df.groupby('city').apply(lambda g: g.nlargest(1, 'revenue'), include_groups=False))

# ================= 4. value_counts =================
print(df['city'].value_counts)
print(df['city'].value_counts(normalize=True)) # 占比
df['city'].value_counts.plot(kind='bar'); plt.show

# ================= 5. 交叉表 crosstab =================
print(pd.crosstab(df['gender_group'], df['channel'])) # 频数
print(pd.crosstab(df['gender_group'], df['channel'], margins=True)) # 加总计
print(pd.crosstab(df['city'], df['channel'], normalize='index')) # 每行占比
print(pd.crosstab(df['city'], df['channel'], normalize='columns')) # 每列占比
print(pd.crosstab(df['city'], df['channel'], normalize='all')) # 占总体比例
print(df.groupby(['gender_group', 'channel']).size.unstack(fill_value=0)) # 等价写法

# ================= 6. 透视表 pivot_table =================
print(df.pivot_table(index='city', values='customer', aggfunc='sum')) # 基础
print(df.pivot_table(index='city', columns='channel', # 行列转置
values='customer', aggfunc='sum'))
print(df.pivot_table(index=['city', 'channel'], values=['revenue', 'unit_cost'],
aggfunc={'revenue': 'mean', 'unit_cost': 'sum'})) # 不同列不同函数
print(df.pivot_table(index='city', values=['revenue', 'unit_cost'],
aggfunc=['mean', 'sum'])) # 全部函数
print(df.pivot_table(index='city', columns='channel', values='revenue',
aggfunc='sum', fill_value=0, margins=True)) # 填 0 + 总计

# ================= 7. 完整案例：股票涨跌与星期几的关系 =================
dates = pd.date_range('2024-01-01', periods=20, freq='D')
stock = pd.DataFrame({'p_change': [2.62, 1.44, 1.57, 2.02, 8.51, -1.23, 0.85, 3.11,
-0.66, 1.98, -2.10, 0.45, 4.20, -1.85, 0.92, 2.33,
-0.57, 1.11, 3.05, -1.40]}, index=dates)

stock['week'] = pd.to_datetime(stock.index).weekday # 0=周一 … 6=周日
stock['posi_neg'] = np.where(stock['p_change'] > 0, 1, 0) # 涨为 1，跌为 0

count = pd.crosstab(stock['week'], stock['posi_neg']) # 每个星期几的涨/跌天数
row_sum = count.sum(axis=1).astype(np.float32) # 每个星期几的总天数
pro = count.div(row_sum, axis=0) # 逐行相除得比例
print(count); print(pro)

pro.plot(kind='bar', stacked=True)
plt.title('各星期几的涨跌比例'); plt.xlabel('星期（0=周一，6=周日）'); plt.ylabel('比例')
plt.show

# 用透视表一行完成：posi_neg 是 0/1，其"均值"恰好等于"1 的占比"= 上涨占比
print(stock.pivot_table(values='posi_neg', index='week', aggfunc='mean'))
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/02-NumPy与Pandas/07-Pandas分组聚合与透视.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「-Pandas分组聚合与透视：可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/02-NumPy与Pandas/07-Pandas分组聚合与透视.md)
