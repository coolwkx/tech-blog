---
article_id: kp-9d45e78ec0c3fa74
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-fb8e5382c0c0
learning_sourceId: fb8e5382c0c0
learning_order: 13
learning_objective: 理解并验证：特征工程：把时序展开成宽表（可独立运行、含自检）
---

# 特征工程：把时序展开成宽表（可独立运行、含自检）

> **学习目标**：能够解释「特征工程：把时序展开成宽表（可独立运行、含自检）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：pandas 时间序列操作（`str` 切片、`shift`、`to_timedelta`）、特征工程五大组成（见 [09-特征工程](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)）、XGBoost 与网格搜索（见 [06-集成学习](../../../../../03-ml/04-集成与无监督/06-集成学习.md)、[08-模型评估与调优](../../../../../03-ml/03-评估与调优/08-模型评估与调优.md)）。
>
> **所属主题**：数据挖掘案例：电力负荷预测 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""特征工程：时间 one-hot + 滑窗负荷 + 昨日同时刻负荷
并附一个自检：手动验算某一行特征是否正确对齐
"""
import numpy as np
import pandas as pd

def feature_engineering(data, logger=None, window_size=3):
 result = data.copy(deep=True)

 # ---- 1. 时间特征 ----
 result["hour"] = result["time"].str[11:13]
 result["month"] = result["time"].str[5:7]

 hour_encoding = pd.get_dummies(result["hour"])
 hour_encoding.columns = ["hour_" + str(c) for c in hour_encoding.columns]
 month_encoding = pd.get_dummies(result["month"])
 month_encoding.columns = ["month_" + str(c) for c in month_encoding.columns]
 result = pd.concat([result, hour_encoding, month_encoding], axis=1)

 # ---- 2. 滑窗历史负荷 ----
 shift_list = [result["power_load"].shift(i) for i in range(1, window_size + 1)]
 shift_data = pd.concat(shift_list, axis=1)
 shift_data.columns = ["前%d小时" % i for i in range(1, window_size + 1)]
 result = pd.concat([result, shift_data], axis=1)

 # ---- 3. 昨日同时刻负荷 ----
 time_load_dict = result.set_index("time")["power_load"].to_dict
 result["yesterday_time"] = result["time"].apply(
 lambda x: (pd.to_datetime(x) - pd.to_timedelta("1d")).strftime("%Y-%m-%d %H:%M:%S"))
 result["yesterday_load"] = result["yesterday_time"].apply(lambda x: time_load_dict.get(x))

 # ---- 4. 剔除空值 ----
 result.dropna(axis=0, inplace=True)

 # ---- 5. 特征列清单 ----
 feature_names = (list(hour_encoding.columns) + list(month_encoding.columns)
 + list(shift_data.columns) + ["yesterday_load"])
 return result, feature_names

if __name__ == "__main__":
 # 造 3 天的小时级数据
 times = pd.date_range("2015-07-30 00:00:00", periods=72, freq="h")
 rng = np.random.default_rng(0)
 df = pd.DataFrame({
 "time": times.strftime("%Y-%m-%d %H:%M:%S"),
 "power_load": 600 + 120 * np.sin(np.arange(72) / 24 * 2 * np.pi) + rng.normal(0, 5, 72),
 })

 processed, feats = feature_engineering(df)
 print("原始形状:", df.shape, " 处理后形状:", processed.shape)
 print("特征列数:", len(feats))

 # ---- 自检 1：某一行的"前1小时"应等于上一行的 power_load ----
 row = processed.iloc[5]
 prev = processed.iloc[4]
 print("\n自检 1（滑窗对齐）：")
 print(" 第 5 行 time =", row["time"], " 前1小时 =", round(row["前1小时"], 4))
 print(" 第 4 行 power_load =", round(prev["power_load"], 4), " -> 应相等 ✓")

 # ---- 自检 2：昨日同时刻 = 该时刻减 24 小时的负荷 ----
 t = processed.iloc[30]["time"]
 y_time = (pd.to_datetime(t) - pd.to_timedelta("1d")).strftime("%Y-%m-%d %H:%M:%S")
 print("\n自检 2（昨日同时刻）：")
 print(" 当前 time =", t, " 昨日同时刻 =", y_time)
 print(" yesterday_load =", round(processed.iloc[30]["yesterday_load"], 4),
 " 原始值 =", round(df[df["time"] == y_time]["power_load"].iloc[0], 4), " -> 应相等 ✓")

 # ---- 自检 3：one-hot 每行只有 1 个 hour 为 1、1 个 month 为 1 ----
 h_cols = [c for c in feats if c.startswith("hour_")]
 m_cols = [c for c in feats if c.startswith("month_")]
 print("\n自检 3（one-hot 正确性）：")
 print(" hour 列和为 1 的行数:", int((processed[h_cols].sum(axis=1) == 1).all) == 1)
 print(" month 列和为 1 的行数:", int((processed[m_cols].sum(axis=1) == 1).all) == 1)
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/06-案例与面试/10-数据挖掘案例-电力负荷预测.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「特征工程：把时序展开成宽表（可独立运行、含自检）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/06-案例与面试/10-数据挖掘案例-电力负荷预测.md)
