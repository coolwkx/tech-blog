---
article_id: kp-46499f0901aa4e5f
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-fb8e5382c0c0
learning_sourceId: fb8e5382c0c0
learning_order: 8
learning_objective: 理解并验证：特征工程（重点）
---

# 特征工程（重点）

> **学习目标**：能够解释「特征工程（重点）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：pandas 时间序列操作（`str` 切片、`shift`、`to_timedelta`）、特征工程五大组成（见 [09-特征工程](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)）、XGBoost 与网格搜索（见 [06-集成学习](../../../../../03-ml/04-集成与无监督/06-集成学习.md)、[08-模型评估与调优](../../../../../03-ml/03-评估与调优/08-模型评估与调优.md)）。
>
> **所属主题**：数据挖掘案例：电力负荷预测 · 算法细节

## 本次只学这一点

**目标**：把 `[time, power_load]` 两列展开成机器学习可用的二维宽表。

**三类特征（共 40 列）**：

| 特征类别 | 列名 | 列数 | 构造方法 |
| --- | --- | --- | --- |
| 短期时间特征 | `hour_00` … `hour_23` | 24 | `time.str[11:13]` + `pd.get_dummies` |
| 长期时间特征 | `month_01` … `month_12` | 12 | `time.str[5:7]` + `pd.get_dummies` |
| 相近时间窗口负荷 | `前1小时`、`前2小时`、`前3小时` | 3 | `power_load.shift(i)`（`window_size=3`） |
| 昨日同时刻负荷 | `yesterday_load` | 1 | 时间→负荷字典 + `to_timedelta('1d')` |
| **合计** | —— | **40** | —— |

> **以 `predict.py` 中的 `feature_names` 为准**：24（hour）+ 12（month）+ 3（前 N 小时）+ 1（yesterday_load）= **40 列**。训练端 `feature_engineering` 返回的 `time_feature_names` 与此必须完全一致。

> **原始代码中的一个真实 Bug（必须修正）**： `pred_feature_extract` 用**写死的切片下标**从列名反查取值：
> ```python
> pred_hour = time[11:13] # 两位，如 '00'、'09'、'19'
> for i in range(24):
> if pred_hour == feature_names[i][5:7]: # 'hour_9'[5:7] == '9'；'hour_19'[5:7] == '19'
> ```
> `pd.get_dummies` 生成的列名是 `hour_0`、`hour_9`、`hour_10` 这种**无前导零**的格式，长度在 6~7 之间浮动，于是：
> - **小时 0（`'hour_0'[5:7] == '0'`）** 与预测值 `'00'` **永不相等** → 凌晨 0 点的 `hour` one-hot **恒为全 0**；
> - **月份 1~9（`'month_9'[6:8] == '9'`）** 与预测值 `'09'` **永不相等** → 这些月份的 `month` one-hot **恒为全 0**。
>
> 结果是预测时特征与训练时**分布不一致**（每月前 9 天、每天 0 点的样本都拿不到正确的时间特征），会静默拉低精度且极难排查。**正确做法**：不要用固定下标切片，统一用 `split('_')[1]` 取后缀，并把预测时间的两位数字去掉前导零（见下面示例代码）。

**实现（完整代码）**：

```python
def feature_engineering(data, logger):
 """
 1.提取出时间特征：月份、小时
 2.提取出相近时间窗口中的负荷特征：step 大小窗口的负荷
 3.提取昨日同时刻负荷特征
 4.剔除出现空值的样本
 5.整理时间特征，并返回
 """
 result = data.copy(deep=True)

 # ---- 1. 时间特征 ----
 result['hour'] = result['time'].str[11:13] # 短期时间特征
 result['month'] = result['time'].str[5:7] # 长期时间特征

 # 1.3 对时间特征做 one-hot 编码
 hour_encoding = pd.get_dummies(result['hour'])
 hour_encoding.columns = ['hour_' + str(i) for i in hour_encoding.columns]
 month_encoding = pd.get_dummies(result['month'])
 month_encoding.columns = ['month_' + str(i) for i in month_encoding.columns]
 result = pd.concat([result, hour_encoding, month_encoding], axis=1)

 # ---- 2. 相近时间窗口中的负荷特征 ----
 window_size = 3
 shift_list = [result['power_load'].shift(i) for i in range(1, window_size + 1)]
 shift_data = pd.concat(shift_list, axis=1)
 shift_data.columns = ['前' + str(i) + '小时' for i in range(1, window_size + 1)]
 result = pd.concat([result, shift_data], axis=1)

 # ---- 3. 昨日同时刻负荷特征 ----
 time_load_dict = result.set_index('time')['power_load'].to_dict
 result['yesterday_time'] = result['time'].apply(
 lambda x: (pd.to_datetime(x) - pd.to_timedelta('1d')).strftime('%Y-%m-%d %H:%M:%S'))
 result['yesterday_load'] = result['yesterday_time'].apply(lambda x: time_load_dict.get(x))

 # ---- 4. 剔除出现空值的样本 ----
 result.dropna(axis=0, inplace=True)

 # ---- 5. 整理特征列，并返回 ----
 time_feature_names = (list(hour_encoding.columns) + list(month_encoding.columns)
 + list(shift_data.columns) + ['yesterday_load'])
 return result, time_feature_names
```

**为什么这样设计特征（每个决策的理由）**：

| 设计决策 | 理由 |
| --- | --- |
| 小时/月份用 **one-hot** 而不是直接用 0~23 的数值 | 数值编码下"23 点"与"0 点"相差 23，但实际相邻；one-hot 消除了虚假的距离/大小关系。对树模型而言 one-hot 也让"某些小时"成为独立的可分裂条件 |
| 同时保留 **hour 与 month** | 分别刻画**日内周期**（短期）与**季节周期**（长期） |
| 用 **`shift`** 构造滑窗 | 直接的"上一时刻负荷"是最强的预测因子（负荷具有很强的惯性/自相关） |
| `window_size = 3` | 覆盖最近 3 小时的趋势；窗口越大信息越多但也越容易过拟合、且会删掉更多行 |
| 加 **昨日同时刻** | 捕捉**日周期**；比"前 24 小时"更直接地表达"同一时刻前一天是多少" |
| 最后 **`dropna`** | `shift(1..3)` 会在头部产生 3 行 NaN，"昨日同时刻"在首日产生一整天的 NaN；必须剔除，否则模型训练报错。代价是**损失了前 3 行 + 首日的数据** |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/06-案例与面试/10-数据挖掘案例-电力负荷预测.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「特征工程（重点）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/06-案例与面试/10-数据挖掘案例-电力负荷预测.md)
