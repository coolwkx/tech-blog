---
article_id: kp-f3762ca686a3ffd2
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-fb8e5382c0c0
learning_sourceId: fb8e5382c0c0
learning_order: 14
learning_objective: 理解并验证：训练模块（精简可运行版）
---

# 训练模块（精简可运行版）

> **学习目标**：能够解释「训练模块（精简可运行版）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：pandas 时间序列操作（`str` 切片、`shift`、`to_timedelta`）、特征工程五大组成（见 [09-特征工程](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)）、XGBoost 与网格搜索（见 [06-集成学习](../../../../../03-ml/04-集成与无监督/06-集成学习.md)、[08-模型评估与调优](../../../../../03-ml/03-评估与调优/08-模型评估与调优.md)）。
>
> **所属主题**：数据挖掘案例：电力负荷预测 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""训练模块：切分 -> 网格搜索 -> 训练 -> 评价 -> 保存"""
import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit, train_test_split
from xgboost import XGBRegressor

from importlib import import_module
# 假设 feature_engineering / data_preprocessing 来自上面的示例模块
fe = import_module("feature_engineering_demo") # 换成你的模块名
cp = import_module("common_demo")

def model_train(data, features, use_time_split=True):
    x_data, y_data = data[features], data["power_load"]

    # ---- 1. 数据集切分 ----
    if use_time_split:
        # 推荐：时序场景按时间切分，且 CV 用 TimeSeriesSplit
        n = len(data)
        cut = int(n * 0.7)
        x_train, x_test = x_data.iloc[:cut], x_data.iloc[cut:]
        y_train, y_test = y_data.iloc[:cut], y_data.iloc[cut:]
        cv = TimeSeriesSplit(n_splits=5)
    else:
        # 原做法：随机切分（评估会偏乐观）
        x_train, x_test, y_train, y_test = train_test_split(
        x_data, y_data, test_size=0.3, random_state=22)
        cv = 5

        # ---- 2. 网格化搜索 + 交叉验证 ----
        param_dict = {
        "n_estimators": [50, 100, 150, 200],
        "max_depth": [3, 6, 9],
        "learning_rate": [0.1, 0.01],
        }
        grid_cv = GridSearchCV(estimator=XGBRegressor(random_state=22),
        param_grid=param_dict, cv=cv, n_jobs=-1,
        scoring="neg_mean_absolute_error")
        grid_cv.fit(x_train, y_train)
        print("最优超参数:", grid_cv.best_params_) # 期望 {'learning_rate':0.1,'max_depth':6,'n_estimators':150}
        print("CV 最优 MAE:", round(-grid_cv.best_score_, 4))

        # ---- 3. 用最优参数训练（也可直接用 grid_cv.best_estimator_）----
        xgb = XGBRegressor(n_estimators=150, max_depth=6, learning_rate=0.1, random_state=22)
        xgb.fit(x_train, y_train)

        # ---- 4. 评价：训练集与测试集对照 ----
        y_pred_train = xgb.predict(x_train)
        y_pred_test = xgb.predict(x_test)
        for name, yt, yp in [("训练集", y_train, y_pred_train), ("测试集", y_test, y_pred_test)]:
            print(f"{name}: MSE={mean_squared_error(yt, yp):.4f} MAE={mean_absolute_error(yt, yp):.4f}")

            # ---- 5. 保存 ----
            joblib.dump(xgb, "xgb.pkl")
            return xgb

        if __name__ == "__main__":
            data = cp.data_preprocessing("../data/train.csv")
            processed, feats = fe.feature_engineering(data)
            model_train(processed, feats)
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/06-案例与面试/10-数据挖掘案例-电力负荷预测.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「训练模块（精简可运行版）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/06-案例与面试/10-数据挖掘案例-电力负荷预测.md)
