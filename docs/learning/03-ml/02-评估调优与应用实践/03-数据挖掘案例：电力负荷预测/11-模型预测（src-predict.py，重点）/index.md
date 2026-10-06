---
article_id: kp-34ffa37014df5d0d
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-fb8e5382c0c0
learning_sourceId: fb8e5382c0c0
learning_order: 10
learning_objective: 理解并验证：模型预测（src/predict.py，重点）
---

# 模型预测（src/predict.py，重点）

> **学习目标**：能够解释「模型预测（src/predict.py，重点）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：pandas 时间序列操作（`str` 切片、`shift`、`to_timedelta`）、特征工程五大组成（见 [09-特征工程](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)）、XGBoost 与网格搜索（见 [06-集成学习](../../../../../03-ml/04-集成与无监督/06-集成学习.md)、[08-模型评估与调优](../../../../../03-ml/03-评估与调优/08-模型评估与调优.md)）。
>
> **所属主题**：数据挖掘案例：电力负荷预测 · 算法细节

## 本次只学这一点

**核心思想**：为了**模拟实际场景**，预测某个时刻时，把它以及它之后的所有负荷都"掩盖掉"，只用**该时刻之前**的历史数据构造特征并预测。这是一个**滚动推理（rolling forecast）**过程。

**完整流程 5 步**：

| 步骤 | 内容 | 关键点 |
| --- | --- | --- |
| 1 | 导包、配置绘图字体 | `plt.rcParams['font.family'] = 'SimHei'`，否则中文乱码 |
| 2 | 定义 `PowerLoadPredict` 类 | 配置日志、获取数据源、**历史数据转字典** |
| 3 | 加载模型 | `joblib.load('../model/xgb.pkl')` |
| 4 | **滚动预测** | 确定预测时间段 → 掩盖未来 → 解析特征 → 预测 → 保存真实值与预测值 |
| 5 | 预测结果评价 | 计算 MAE + 绘制真实/预测折线图 |

**为什么把历史数据转成字典**：

```python
self.data_dict = self.data_source.set_index('time')['power_load'].to_dict
```

- 预测时需要对每个时刻反复查询"某一具体时间点的负荷"，如果每次都在 DataFrame 上做条件筛选，开销极大；
- 转成 `dict`（`key: 时间字符串 → value: 负荷`）后查询是 $O(1)$；
- 注释也指出：**实际开发场景中可以使用 Redis 进行缓存**。

**特征解析函数（`pred_feature_extract`）**——预测端必须**手工组装出与训练时列名、列序完全一致的 40 列特征**：

```python
feature_names = ['hour_00', ..., 'hour_23', # 24 列
'month_01', ..., 'month_12', # 12 列
'前1小时', '前2小时', '前3小时', # 3 列
'yesterday_load'] # 1 列

# 1. 小时 one-hot：把预测时间的小时与 hour_00..hour_23 逐一比对
pred_hour = time[11:13]
for i in range(24):
    hour_part.append(1 if pred_hour == feature_names[i][5:7] else 0)

    # 2. 月份 one-hot：注意下标从 24 开始，且切片起点是 [6:8]（"month_01" 的长度差异）
    pred_month = time[5:7]
    for i in range(24, 36):
        month_part.append(1 if pred_month == feature_names[i][6:8] else 0)

        # 3. 历史负荷：前 1/2/3 小时、昨日同时刻；查不到时给默认值 600
        last_1h_load = data_dict.get((pd.to_datetime(time) - pd.to_timedelta('1h')).strftime('%Y-%m-%d %H:%M:%S'), 600)
        last_2h_load = data_dict.get((pd.to_datetime(time) - pd.to_timedelta('2h')).strftime('%Y-%m-%d %H:%M:%S'), 600)
        last_3h_load = data_dict.get((pd.to_datetime(time) - pd.to_timedelta('3h')).strftime('%Y-%m-%d %H:%M:%S'), 600)
        last_day_load = data_dict.get((pd.to_datetime(time) - pd.to_timedelta('1d')).strftime('%Y-%m-%d %H:%M:%S'), 600)
```

**滚动预测主循环**：

```python
# 4.1 确定要预测的时间段：2015-08-01 00:00:00 及以后
pred_times = pred_obj.data_source[pred_obj.data_source['time'] >= '2015-08-01 00:00:00']['time']

evaluate_list = []
for pred_time in pred_times:
 # 4.2 模拟真实场景：只保留预测时间之前的数据（把未来"掩盖"掉）
 data_his_dict = {k: v for k, v in pred_obj.data_dict.items() if k < pred_time}

 # 4.3 解析特征并预测
 processed_data, feature_cols = pred_feature_extract(data_his_dict, pred_time, pred_obj.logfile)
 pred_value = model.predict(processed_data[feature_cols])

 # 4.4 取该时刻的真实负荷
 true_value = pred_obj.data_dict.get(pred_time)

 # 4.5 记录【预测时间, 真实值, 预测值】
 evaluate_list.append([pred_time, true_value, pred_value[0]])

 # 4.6 转成 DataFrame
 evaluate_df = pd.DataFrame(evaluate_list, columns=['时间', '真实值', '预测值'])

 # 5.1 计算 MAE
 mae_score = mean_absolute_error(evaluate_df['真实值'], evaluate_df['预测值'])

 # 5.2 画折线图（真实值 vs 预测值），横轴时间太密，用 MultipleLocator(50) 调间隔
```

**为什么这个设计是"最关键的工程点"**：

| 设计 | 意义 |
| --- | --- |
| 每个时刻都重新过滤 `data_his_dict = {k: v for k, v in ... if k < pred_time}` | **严格禁止未来信息泄漏**。注意：这里预测用的是**真实的历史值**（不是把预测值当作下一步的输入），所以预测是"单步预测"而不是"多步自回归滚动" |
| 预测端的 `feature_names` 与训练端完全一致 | 特征列名/列序不一致是时序项目最常见的线上事故 |
| `data_dict.get(key, 600)` 的默认值 | 处理边界情况（如数据缺失），避免 `None` 导致预测崩溃。**注意 600 是硬编码的经验值，稳健做法应改用该小时的历史均值** |
| 逐时刻循环 + 字典查询 | 模拟真实场景（每个小时到来时才有真实数据） |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/06-案例与面试/10-数据挖掘案例-电力负荷预测.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「模型预测（src/predict.py，重点）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/06-案例与面试/10-数据挖掘案例-电力负荷预测.md)
