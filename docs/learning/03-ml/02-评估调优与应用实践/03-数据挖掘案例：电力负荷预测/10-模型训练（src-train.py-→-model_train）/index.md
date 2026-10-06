---
article_id: kp-373fb4de89f06171
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-fb8e5382c0c0
learning_sourceId: fb8e5382c0c0
learning_order: 9
learning_objective: 理解并验证：模型训练（src/train.py → model_train）
---

# 模型训练（src/train.py → model_train）

> **学习目标**：能够解释「模型训练（src/train.py → model_train）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：pandas 时间序列操作（`str` 切片、`shift`、`to_timedelta`）、特征工程五大组成（见 [09-特征工程](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)）、XGBoost 与网格搜索（见 [06-集成学习](../../../../../03-ml/04-集成与无监督/06-集成学习.md)、[08-模型评估与调优](../../../../../03-ml/03-评估与调优/08-模型评估与调优.md)）。
>
> **所属主题**：数据挖掘案例：电力负荷预测 · 算法细节

## 本次只学这一点

**流程 6 步**：数据集切分 → 网格化搜索与交叉验证 → 模型实例化 → 模型训练 → 模型评价 → 模型保存。

```python
def model_train(data, features, logger):
 # 1. 数据集切分
 x_data = data[features]
 y_data = data['power_load']
 x_train, x_test, y_train, y_test = train_test_split(
 x_data, y_data, test_size=0.3, random_state=22)

 # 2. 网格化搜索与交叉验证（完整代码中已执行，结果被注释保留）
 param_dict = {
 'n_estimators': [50, 100, 150, 200],
 'max_depth': [3, 6, 9],
 'learning_rate': [0.1, 0.01]
 }
 grid_cv = GridSearchCV(estimator=XGBRegressor, param_grid=param_dict, cv=5)
 grid_cv.fit(x_train, y_train)
 # 最优结果：{'learning_rate': 0.1, 'max_depth': 6, 'n_estimators': 150}

 # 3. 用最优超参数正式训练
 xgb = XGBRegressor(n_estimators=150, max_depth=6, learning_rate=0.1)
 xgb.fit(x_train, y_train)

 # 4. 模型评价：训练集与测试集各算 MSE、MAE
 y_pred_train = xgb.predict(x_train)
 y_pred_test = xgb.predict(x_test)
 mse_train = mean_squared_error(y_train, y_pred_train)
 mae_train = mean_absolute_error(y_train, y_pred_train)
 mse_test = mean_squared_error(y_test, y_pred_test)
 mae_test = mean_absolute_error(y_test, y_pred_test)

 # 5. 模型保存
 joblib.dump(xgb, '../model/xgb.pkl')
```

**网格搜索结果**：

| 超参数 | 候选 | 最优值 |
| --- | --- | --- |
| `n_estimators` | 50 / 100 / **150** / 200 | **150** |
| `max_depth` | 3 / **6** / 9 | **6** |
| `learning_rate` | **0.1** / 0.01 | **0.1** |

**网格搜索耗时参考（日志）**：`2024-11-26 15:38:26` 开始、`15:39:07` 结束，约 **41 秒**（$4\times3\times2\times5 = 120$ 次训练）。

**评价指标的选择**：

| 指标 | 公式 | 为什么用它 |
| --- | --- | --- |
| MSE | $\frac1n\sum(y_i-\hat y_i)^2$ | 放大大误差，敏感于极端偏差 |
| MAE | $\frac1n\sum\lvert y_i-\hat y_i\rvert$ | **量纲与负荷相同**，业务上最直观（"平均错多少 kW"） |

同时输出训练集与测试集的 MSE/MAE，便于对照诊断过拟合（详见 [08-模型评估与调优](../../../../../03-ml/03-评估与调优/08-模型评估与调优.md)）。

> **关于切分方式的重要提示**：完整代码用的是 `train_test_split(test_size=0.3, random_state=22)`，即**随机划分**。对时序数据而言，严格的工程做法应该是**按时间切分**（前 70% 训练、后 30% 测试）。随机划分会把"未来"的数据放进训练集，虽然随机打乱后不存在"用未来预测过去"的严格泄漏（因为特征都来自过去），但会导致测试集里的时间点分布在训练时间范围内部，评估结果比真实上线场景乐观。在 `predict.py` 中通过**滚动推理**弥补了这一点，那才是更接近真实场景的评估。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/06-案例与面试/10-数据挖掘案例-电力负荷预测.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「模型训练（src/train.py → model_train）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/06-案例与面试/10-数据挖掘案例-电力负荷预测.md)
