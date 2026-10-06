---
article_id: kp-67fc4cb4e6fc179a
learning_kind: article
learning_category: 02-data
learning_direction: practice
learning_topic: topic-fe8ec5a80b7e
learning_sourceId: fe8ec5a80b7e
learning_order: 7
learning_objective: 理解并验证：简化版：五分位法（ 04-扩展 的写法）
---

# 简化版：五分位法（ 04-扩展 的写法）

> **学习目标**：能够解释「简化版：五分位法（ 04-扩展 的写法）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[06-Pandas数据清洗](../../../../../02-data/02-NumPy与Pandas/06-Pandas数据清洗.md)（`dropna`、`concat`、`dt` 时间属性）；[07-Pandas分组聚合与透视](../../../../../02-data/02-NumPy与Pandas/07-Pandas分组聚合与透视.md)（`groupby + agg`）；[09-统计分析基础](../../../../../02-data/03-可视化与统计/09-统计分析基础.md)（`describe` 与分位数）。
>
> **所属主题**：-RFM用户价值分析实战 · 可运行示例

## 本次只学这一点

只需要一个快速分群结论时，可用固定 5 档的写法，代码更短：

```python
import numpy as np, pandas as pd
df_raw = raw.set_index('会员ID') # 真实场景：pd.read_excel(..., index_col='USERID')

sales_data = df_raw.dropna # 缺失值处理
sales_data = sales_data[sales_data['订单金额'] > 1] # 去异常

recency_value = sales_data['提交日期'].groupby(sales_data.index).max # 最近一次订单时间
frequency_value = sales_data['提交日期'].groupby(sales_data.index).count # 订单频率
monetary_value = sales_data['订单金额'].groupby(sales_data.index).sum # 订单总金额

deadline_date = pd.to_datetime('2020-05-01') # 指定时间节点
r_interval = (deadline_date - recency_value).dt.days
r_score = pd.cut(r_interval, 5, labels=[5, 4, 3, 2, 1]) # R 五分位，倒序
f_score = pd.cut(frequency_value, 5, labels=[1, 2, 3, 4, 5]) # F 五分位
m_score = pd.cut(monetary_value, 5, labels=[1, 2, 3, 4, 5]) # M 五分位

rfm_list = [r_score, f_score, m_score]
rfm_cols = ['r_score', 'f_score', 'm_score']
rfm_pd = pd.DataFrame(np.array(rfm_list).transpose, dtype=np.int32,
columns=rfm_cols, index=frequency_value.index) # 3 x N 转置成 N x 3

rfm_pd['rfm_wscore'] = (rfm_pd['r_score'] * 0.2 + rfm_pd['f_score'] * 0.2
+ rfm_pd['m_score'] * 0.6) # 加权得分
tmp = rfm_pd[rfm_cols].astype(str)
rfm_pd['rfm_comb'] = tmp['r_score'].str.cat(tmp['f_score']).str.cat(tmp['m_score'])
rfm_pd.to_csv('rfm_result.csv')
print(rfm_pd.head)
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/04-分析实战/10-RFM用户价值分析实战.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「简化版：五分位法（ 04-扩展 的写法）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/04-分析实战/10-RFM用户价值分析实战.md)
