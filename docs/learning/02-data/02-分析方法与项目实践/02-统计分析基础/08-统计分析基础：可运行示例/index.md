---
article_id: kp-abcefe2f7e38d027
learning_kind: article
learning_category: 02-data
learning_direction: practice
learning_topic: topic-0cc0dae06e45
learning_sourceId: 0cc0dae06e45
learning_order: 7
learning_objective: 理解并验证：-统计分析基础：可运行示例
---

# -统计分析基础：可运行示例

> **学习目标**：能够解释「-统计分析基础：可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-NumPy数值计算](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)（`axis`、`np.nan`、聚合函数）；[06-Pandas数据清洗](../../../../../02-data/02-NumPy与Pandas/06-Pandas数据清洗.md)（`DataFrame`/`Series`、缺失值）；[08-数据可视化- matplotlib与seaborn](../../../../../02-data/03-可视化与统计/08-数据可视化-matplotlib与seaborn.md)（直方图看分布）。
>
> **所属主题**：-统计分析基础 · 可运行示例

## 本次只学这一点

```python
import numpy as np
import pandas as pd

# ============================================================
# 1. NumPy：统计函数的 axis 语义
# ============================================================
score = np.array([[80, 89, 86, 67, 79],
[78, 97, 89, 67, 81],
[90, 94, 78, 67, 74],
[91, 91, 90, 67, 69],
[76, 87, 75, 67, 86],
[70, 79, 84, 67, 84],
[94, 92, 93, 67, 64],
[86, 85, 83, 67, 80]]) # 8 名学生 × 5 门课

print('维度 / 轴数 / 元素数:', score.shape, score.ndim, score.size)

temp = score[:4, :] # 取前 4 名学生
print('各科最高分 (axis=0):', np.max(temp, axis=0)) # 长度 = 列数 = 5
print('各科最低分 (axis=0):', np.min(temp, axis=0))
print('各科平均分 (axis=0):', np.mean(temp, axis=0))
print('各科中位数 (axis=0):', np.median(temp, axis=0))
print('各科标准差 (axis=0):', np.std(temp, axis=0))
print('各科方差 (axis=0):', np.var(temp, axis=0))
print('各科最高分是谁 (下标):', np.argmax(temp, axis=0))

print('每人总分 (axis=1):', np.sum(temp, axis=1)) # 长度 = 行数 = 4
print('全班最高分 (无 axis):', np.max(temp))

# 极差
print('各科极差:', np.ptp(temp, axis=0))

# 总体 vs 样本标准差
flat = temp.ravel
print('np.std(ddof=0):', round(np.std(flat), 4)) # 总体
print('np.std(ddof=1):', round(np.std(flat, ddof=1), 4))# 样本
print('pandas std :', round(pd.Series(flat).std, 4))# 默认 ddof=1，与上面一致

# ============================================================
# 2. Pandas：describe 与统计函数
# ============================================================
df = pd.DataFrame(score, columns=['语文', '数学', '英语', '政治', '体育'],
index=['学生' + str(i) for i in range(8)])

print(df.describe) # count / mean / std / min / 25% / 50% / 75% / max
print(df.info) # 每列非空数 + dtype + 内存

# 单个统计函数（默认按列 axis=0）
print(df.max)
print(df.max(0)) # 等价于上一行
print(df.max(1)) # 每行的最大值
print(df.mean)
print(df.median)
print(df.var)
print(df.std)
print(df.count) # 每列非空个数
print(df.count(axis=1)) # 每行非空个数

# 位置：Pandas 返回索引标签，NumPy 返回下标
print(df.idxmax(axis=0)) # 每列最大值所在的学生
print(df.idxmax(axis=1)) # 每行最大值所在的科目

# ============================================================
# 3. 判断分布形态：均值 vs 中位数
# ============================================================
order = pd.Series([59, 60, 62, 65, 68, 70, 72, 75, 80, 120, 5000], name='订单金额')
print(order.describe)
# mean 远大于 50%，说明右偏、存在极端大值
print('均值 :', round(order.mean, 2)) # 被 5000 拉高
print('中位数 :', round(order.median, 2)) # 更接近"典型订单"
print('偏度近似对比: mean > median ->', order.mean > order.median)

# ============================================================
# 4. 分位数与 IQR：制定分箱边界
# ============================================================
s = pd.Series([1.5, 69, 189, 1199, 206251.8] * 20) # 模拟"订单金额"
q1, q2, q3 = s.quantile([0.25, 0.5, 0.75])
print('25% / 50% / 75%:', q1, q2, q3)
iqr = q3 - q1
print('IQR:', iqr)
lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
print('离群点判定区间:', (lo, hi))
print('离群点个数:', ((s < lo) | (s > hi)).sum)

# 用 25%/75% 作为分箱边界（RFM 案例的实际做法）
r_bins = [-1, q1, q3, s.max + 1]
print('自定义分箱边界:', r_bins)
print(pd.cut(s, bins=r_bins, labels=[3, 2, 1]).value_counts)

# ============================================================
# 5. 累计统计
# ============================================================
dates = pd.date_range('2024-01-01', periods=8)
rise = pd.Series([2.62, 1.44, 1.57, 2.02, 8.51, -1.23, 0.85, -2.10], index=dates)
print(rise.sort_index.cumsum) # 累计涨跌
print(rise.cummax) # 历史新高
print(rise.cummin) # 历史新低
print((1 + rise / 100).cumprod) # 复利式累计净值

# ============================================================
# 6. apply：自定义统计量（极差）
# ============================================================
print(df.apply(lambda col: col.max - col.min, axis=0)) # 每列极差
print(df.apply(lambda row: row.max - row.min, axis=1)) # 每行极差
print(df[['语文', '数学']].apply(lambda col: col.std / col.mean, axis=0)) # 变异系数
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/03-可视化与统计/09-统计分析基础.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「-统计分析基础：可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/03-可视化与统计/09-统计分析基础.md)
