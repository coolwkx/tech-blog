---
article_id: kp-31de3f36fb081f9e
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-fb8e5382c0c0
learning_sourceId: fb8e5382c0c0
learning_order: 7
learning_objective: 理解并验证：数据分析（src/train.py → ana_data）
---

# 数据分析（src/train.py → ana_data）

> **学习目标**：能够解释「数据分析（src/train.py → ana_data）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：pandas 时间序列操作（`str` 切片、`shift`、`to_timedelta`）、特征工程五大组成（见 [09-特征工程](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)）、XGBoost 与网格搜索（见 [06-集成学习](../../../../../03-ml/04-集成与无监督/06-集成学习.md)、[08-模型评估与调优](../../../../../03-ml/03-评估与调优/08-模型评估与调优.md)）。
>
> **所属主题**：数据挖掘案例：电力负荷预测 · 算法细节

## 本次只学这一点

**5 项分析**（对应 4 张子图）：

| 序号 | 分析内容 | 代码手段 | 观察目的 |
| --- | --- | --- | --- |
| 1 | 查看数据整体情况 | `data.info`、`data.head` | 行列数、缺失、类型 |
| 2 | 负荷整体的分布情况 | `ax1.hist(data['power_load'], bins=100)` | 是否有偏态、双峰、异常区间 |
| 3 | 各小时的平均负荷趋势 | `data['hour'] = time.str[11:13]`；`groupby('hour')['power_load'].mean` | 看负荷在**一天**中的变化（日内周期） |
| 4 | 各月份的平均负荷趋势 | `data['month'] = time.str[5:7]`；`groupby('month').mean` | 看负荷在**一年**中的变化（季节性） |
| 5 | 工作日 vs 周末的平均负荷 | `weekday`；`is_workday = 1 if weekday<=4 else 0`；对比两组均值 | 看工作日与周末是否有明显区别 |

```python
# 关键片段：把字符串时间拆成年/月/日/星期，是时序分析的起点
data['hour'] = data['time'].str[11:13]
data_hour_avg = data.groupby(by='hour', as_index=False)['power_load'].mean

data['month'] = data['time'].str[5:7]
data_month_avg = data.groupby('month', as_index=False)['power_load'].mean

data['week_day'] = data['time'].apply(lambda x: pd.to_datetime(x).weekday) # 0=周一, 6=周日
data['is_workday'] = data['week_day'].apply(lambda x: 1 if x <= 4 else 0) # 周一~周五
```

> **分析的结论要落到特征设计上**：如果"各小时平均负荷"呈现明显的峰谷（早高峰、晚高峰），就说明**小时是有判别力的特征**，必须加入；如果"月份均值"差异明显，就说明**月份特征有效**。这正是下一步特征工程的依据。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/06-案例与面试/10-数据挖掘案例-电力负荷预测.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「数据分析（src/train.py → ana_data）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/06-案例与面试/10-数据挖掘案例-电力负荷预测.md)
