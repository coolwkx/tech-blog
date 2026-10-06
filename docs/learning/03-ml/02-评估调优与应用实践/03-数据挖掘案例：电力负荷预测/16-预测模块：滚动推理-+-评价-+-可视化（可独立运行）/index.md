---
article_id: kp-969c2ca3bbbb36ba
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-fb8e5382c0c0
learning_sourceId: fb8e5382c0c0
learning_order: 15
learning_objective: 理解并验证：预测模块：滚动推理 + 评价 + 可视化（可独立运行）
---

# 预测模块：滚动推理 + 评价 + 可视化（可独立运行）

> **学习目标**：能够解释「预测模块：滚动推理 + 评价 + 可视化（可独立运行）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：pandas 时间序列操作（`str` 切片、`shift`、`to_timedelta`）、特征工程五大组成（见 [09-特征工程](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)）、XGBoost 与网格搜索（见 [06-集成学习](../../../../../03-ml/04-集成与无监督/06-集成学习.md)、[08-模型评估与调优](../../../../../03-ml/03-评估与调优/08-模型评估与调优.md)）。
>
> **所属主题**：数据挖掘案例：电力负荷预测 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""预测模块核心逻辑：解析特征 -> 滚动推理 -> 评价 -> 可视化"""
import joblib
import matplotlib.pyplot as plt
import matplotlib.ticker as mick
import pandas as pd
from sklearn.metrics import mean_absolute_error

plt.rcParams["font.family"] = "SimHei"

# 与训练端完全一致的 40 列特征清单
# 注意：训练端用 pd.get_dummies 生成的小时/月份列名是「无前导零」的（hour_0..hour_9、month_1..month_9），
# 所以这里必须与训练端保持完全相同的命名，否则预测时列名对不上、模型会报 feature_names mismatch。
HOUR_COLS = ["hour_" + str(i) for i in range(24)]
MONTH_COLS = ["month_" + str(i) for i in range(1, 13)]
FEATURE_NAMES = HOUR_COLS + MONTH_COLS + ["前1小时", "前2小时", "前3小时", "yesterday_load"]


def pred_feature_extract(data_dict, time, default_load=600):
    """预测时刻 -> 特征 DataFrame（列名与列序必须与训练一致）"""
    # 1. 小时 one-hot：用 split 取后缀，避免切片下标写死导致长度不一致
    pred_hour = time[11:13].lstrip("0") or "0" # "09" -> "9"，"00" -> "0"
    hour_part = [1 if pred_hour == c.split("_")[1] else 0 for c in HOUR_COLS]
    # 2. 月份 one-hot
    pred_month = time[5:7].lstrip("0") or "0"
    month_part = [1 if pred_month == c.split("_")[1] else 0 for c in MONTH_COLS]
    # 3. 历史负荷：前 1/2/3 小时 + 昨日同时刻
    def get_load(delta):
        t = (pd.to_datetime(time) - pd.to_timedelta(delta)).strftime("%Y-%m-%d %H:%M:%S")
        return data_dict.get(t, default_load)

    his_part = [get_load("1h"), get_load("2h"), get_load("3h"), get_load("1d")]
    return pd.DataFrame([hour_part + month_part + his_part], columns=FEATURE_NAMES)

def rolling_predict(data_source, model, start_time, default_load=600):
    """从 start_time 起逐小时滚动预测，返回 [时间, 真实值, 预测值] 表"""
    data_dict = data_source.set_index("time")["power_load"].to_dict
    pred_times = data_source[data_source["time"] >= start_time]["time"]
    evaluate_list = []
    for pred_time in pred_times:
        # 模拟真实场景：只保留预测时刻之前的数据
        data_his_dict = {k: v for k, v in data_dict.items() if k < pred_time}
        feats = pred_feature_extract(data_his_dict, pred_time, default_load)
        pred_value = model.predict(feats)[0]
        evaluate_list.append([pred_time, data_dict.get(pred_time), pred_value])
        return pd.DataFrame(evaluate_list, columns=["时间", "真实值", "预测值"])

    def prediction_plot(evaluate_df, save_path="预测效果.png"):
        fig = plt.figure(figsize=(40, 20))
        ax = fig.add_subplot()
        ax.plot(evaluate_df["时间"], evaluate_df["真实值"], label="真实值")
        ax.plot(evaluate_df["时间"], evaluate_df["预测值"], label="预测值")
        ax.set_ylabel("负荷")
        ax.set_title("预测负荷以及真实负荷的折线图")
        ax.xaxis.set_major_locator(mick.MultipleLocator(50)) # 时间太密，调间隔
        plt.xticks(rotation=45)
        plt.legend()
        plt.savefig(save_path)
        plt.show()


        if __name__ == "__main__":
            # 依赖：先跑完 3.2、3.3 并保存 xgb.pkl 与 test.csv
            from importlib import import_module
            cp = import_module("common_demo")

            test_data = cp.data_preprocessing("../data/test.csv")
            model = joblib.load("xgb.pkl")

            evaluate_df = rolling_predict(test_data, model, "2015-08-01 00:00:00")
            print("滚动预测样本数:", len(evaluate_df))

            mae = mean_absolute_error(evaluate_df["真实值"], evaluate_df["预测值"])
            print("模型对新数据进行预测的平均绝对误差(MAE): %.4f" % mae)
            print("相对误差(MAE/真实均值): %.4f%%"
            % (100 * mae / evaluate_df["真实值"].mean()))

            prediction_plot(evaluate_df)
            # 结论：预测负荷曲线应紧密贴合真实负荷曲线，并复现出明显的日周期峰谷。
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/06-案例与面试/10-数据挖掘案例-电力负荷预测.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「预测模块：滚动推理 + 评价 + 可视化（可独立运行）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/06-案例与面试/10-数据挖掘案例-电力负荷预测.md)
