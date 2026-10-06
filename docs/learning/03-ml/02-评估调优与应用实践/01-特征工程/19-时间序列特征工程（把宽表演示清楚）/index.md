---
article_id: kp-afb802d8690067a5
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-0d24db15ec32
learning_sourceId: 0d24db15ec32
learning_order: 18
learning_objective: 理解并验证：时间序列特征工程（把宽表演示清楚）
---

# 时间序列特征工程（把宽表演示清楚）

> **学习目标**：能够解释「时间序列特征工程（把宽表演示清楚）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：pandas 的 `groupby`/`get_dummies`/缺失值处理、numpy 的数组拼接（`hstack`）、距离与量纲的影响（见 [02-KNN算法](../../../../../03-ml/02-经典算法/02-KNN算法.md)）。
>
> **所属主题**：特征工程 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""时序 -> 二维宽表：时间 one-hot + 滑窗负荷 + 昨日同时刻负荷"""
import numpy as np
import pandas as pd

# 造一份小时级数据
times = pd.date_range("2015-07-25 00:00:00", periods=200, freq="h")
df = pd.DataFrame({
"time": times.strftime("%Y-%m-%d %H:%M:%S"),
"power_load": 600 + 100 * np.sin(np.arange(200) / 24 * 2 * np.pi) + np.random.normal(0, 5, 200),
})

def feature_engineering(data, window_size=3):
 result = data.copy(deep=True)

 # ---- 1. 时间特征 ----
 result["hour"] = result["time"].str[11:13] # 短期：小时
 result["month"] = result["time"].str[5:7] # 长期：月份
 hour_encoding = pd.get_dummies(result["hour"])
 hour_encoding.columns = ["hour_" + str(c) for c in hour_encoding.columns]
 month_encoding = pd.get_dummies(result["month"])
 month_encoding.columns = ["month_" + str(c) for c in month_encoding.columns]
 result = pd.concat([result, hour_encoding, month_encoding], axis=1)

 # ---- 2. 滑窗历史负荷（只能用过去！）----
 shift_data = pd.concat([result["power_load"].shift(i) for i in range(1, window_size + 1)], axis=1)
 shift_data.columns = ["前%d小时" % i for i in range(1, window_size + 1)]
 result = pd.concat([result, shift_data], axis=1)

 # ---- 3. 昨日同时刻负荷 ----
 time_load_dict = result.set_index("time")["power_load"].to_dict()
 result["yesterday_time"] = result["time"].apply(
 lambda x: (pd.to_datetime(x) - pd.to_timedelta("1d")).strftime("%Y-%m-%d %H:%M:%S"))
 result["yesterday_load"] = result["yesterday_time"].apply(lambda x: time_load_dict.get(x))

 # ---- 4. 剔除因滑窗/昨日产生的空值 ----
 result.dropna(axis=0, inplace=True)

 # ---- 5. 整理特征列名 ----
 feature_names = (list(hour_encoding.columns) + list(month_encoding.columns)
 + list(shift_data.columns) + ["yesterday_load"])
 return result, feature_names

if __name__ == "__main__":
 processed, feats = feature_engineering(df)
 print("原始形状:", df.shape)
 print("处理后形状:", processed.shape)
 print("特征个数:", len(feats))
 print("前 5 个特征:", feats[:5])
 print(processed[["time", "power_load", "前1小时", "前2小时", "前3小时", "yesterday_load"]].head())
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「时间序列特征工程（把宽表演示清楚）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)
