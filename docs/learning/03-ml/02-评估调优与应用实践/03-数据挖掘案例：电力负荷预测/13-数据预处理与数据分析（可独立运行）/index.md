---
article_id: kp-104b0f5207df4f8d
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-fb8e5382c0c0
learning_sourceId: fb8e5382c0c0
learning_order: 12
learning_objective: 理解并验证：数据预处理与数据分析（可独立运行）
---

# 数据预处理与数据分析（可独立运行）

> **学习目标**：能够解释「数据预处理与数据分析（可独立运行）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：pandas 时间序列操作（`str` 切片、`shift`、`to_timedelta`）、特征工程五大组成（见 [09-特征工程](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)）、XGBoost 与网格搜索（见 [06-集成学习](../../../../../03-ml/04-集成与无监督/06-集成学习.md)、[08-模型评估与调优](../../../../../03-ml/03-评估与调优/08-模型评估与调优.md)）。
>
> **所属主题**：数据挖掘案例：电力负荷预测 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""utils/common.py + ana_data 的精简版：预处理 + 4 张分析图"""
import os

import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.family"] = "SimHei" # 中文显示
plt.rcParams["font.size"] = 15

def data_preprocessing(path):
 """加载 -> 时间格式化 -> 升序 -> 去重"""
 data = pd.read_csv(path)
 data["time"] = pd.to_datetime(data["time"]).dt.strftime("%Y-%m-%d %H:%M:%S")
 data.sort_values(by="time", inplace=True)
 data.drop_duplicates(inplace=True)
 return data

def ana_data(data):
 data = data.copy(deep=True)
 print(data.info)
 print(data.head)

 fig = plt.figure(figsize=(20, 32))

 # 1. 负荷整体分布
 ax1 = fig.add_subplot(411)
 ax1.hist(data["power_load"], bins=100)
 ax1.set_title("负荷分布直方图")

 # 2. 各小时的平均负荷（日内周期）
 ax2 = fig.add_subplot(412)
 data["hour"] = data["time"].str[11:13]
 hour_avg = data.groupby(by="hour", as_index=False)["power_load"].mean
 ax2.plot(hour_avg["hour"], hour_avg["power_load"], color="b", linewidth=2)
 ax2.set_title("各小时的平均负荷趋势图")
 ax2.set_xlabel("小时"); ax2.set_ylabel("负荷")

 # 3. 各月份的平均负荷（季节周期）
 ax3 = fig.add_subplot(413)
 data["month"] = data["time"].str[5:7]
 month_avg = data.groupby("month", as_index=False)["power_load"].mean
 ax3.plot(month_avg["month"], month_avg["power_load"], color="r", linewidth=2)
 ax3.set_title("各月份平均负荷")
 ax3.set_xlabel("月份"); ax3.set_ylabel("平均负荷")

 # 4. 工作日 vs 周末
 ax4 = fig.add_subplot(414)
 data["week_day"] = data["time"].apply(lambda x: pd.to_datetime(x).weekday)
 data["is_workday"] = data["week_day"].apply(lambda x: 1 if x <= 4 else 0)
 workday_avg = data[data["is_workday"] == 1]["power_load"].mean
 weekend_avg = data[data["is_workday"] == 0]["power_load"].mean
 ax4.bar(x=["工作日平均负荷", "周末平均负荷"], height=[workday_avg, weekend_avg])
 ax4.set_ylabel("平均负荷")
 ax4.set_title("工作日与周末的平均负荷对比")

 os.makedirs("../data/fig", exist_ok=True)
 plt.savefig("../data/fig/负荷分析图.png")
 print("工作日平均负荷 = %.2f, 周末平均负荷 = %.2f" % (workday_avg, weekend_avg))
 print("季节/日内周期是否明显？决定 hour、month 特征是否值得加入。")
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/06-案例与面试/10-数据挖掘案例-电力负荷预测.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「数据预处理与数据分析（可独立运行）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/06-案例与面试/10-数据挖掘案例-电力负荷预测.md)
