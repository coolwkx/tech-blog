---
article_id: kp-224a1a875de974af
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-7b8856bc8b6a
learning_sourceId: 7b8856bc8b6a
learning_order: 6
learning_objective: 理解并验证：完整案例的业务逻辑：股票涨跌与星期几的关系
---

# 完整案例的业务逻辑：股票涨跌与星期几的关系

> **学习目标**：能够解释「完整案例的业务逻辑：股票涨跌与星期几的关系」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[06-Pandas数据清洗](../../../../../02-data/02-NumPy与Pandas/06-Pandas数据清洗.md)（索引、`loc/iloc`、缺失值、`merge`）；[05-NumPy数值计算](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md) 的聚合函数与 `np.where`。
>
> **所属主题**：-Pandas分组聚合与透视 · 核心概念

## 本次只学这一点

| 步骤 | 做法 |
| --- | --- |
| ① 提取分类维度 | `pd.to_datetime(df.index).weekday` → 0=周一 … 6=周日 |
| ② 目标变量二值化 | `np.where(df['p_change'] > 0, 1, 0)` → 1 表示涨、0 表示跌 |
| ③ 交叉计数 | `pd.crosstab(df['week'], df['posi_neg'])` 得每个星期几的涨/跌天数 |
| ④ 转成比例 | 按行求和后用 `div(..., axis=0)` 相除，得到"上涨占比" |
| ⑤ 可视化 | `pro.plot(kind='bar', stacked=True)` 堆叠柱状图 |
| ⑥ 一行替代 ③④ | `df.pivot_table(['posi_neg'], index='week')` 直接得均值（即上涨占比） |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/02-NumPy与Pandas/07-Pandas分组聚合与透视.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「完整案例的业务逻辑：股票涨跌与星期几的关系」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/02-NumPy与Pandas/07-Pandas分组聚合与透视.md)
