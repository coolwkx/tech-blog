---
article_id: kp-8ee0ad54e9905b02
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-fb8e5382c0c0
learning_sourceId: fb8e5382c0c0
learning_order: 6
learning_objective: 理解并验证：数据预处理（utils/common.py）
---

# 数据预处理（utils/common.py）

> **学习目标**：能够解释「数据预处理（utils/common.py）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：pandas 时间序列操作（`str` 切片、`shift`、`to_timedelta`）、特征工程五大组成（见 [09-特征工程](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)）、XGBoost 与网格搜索（见 [06-集成学习](../../../../../03-ml/04-集成与无监督/06-集成学习.md)、[08-模型评估与调优](../../../../../03-ml/03-评估与调优/08-模型评估与调优.md)）。
>
> **所属主题**：数据挖掘案例：电力负荷预测 · 算法细节

## 本次只学这一点

```python
def data_preprocessing(path):
 """
 1.获取数据源
 2.时间格式化，转为 2024-12-20 09:00:00 这种格式
 3.按时间升序排序
 4.去重
 """
 data = pd.read_csv(path)
 data['time'] = pd.to_datetime(data['time']).dt.strftime('%Y-%m-%d %H:%M:%S')
 data.sort_values(by='time', inplace=True)
 data.drop_duplicates(inplace=True)
 return data
```

**四步的必要性**：

| 步骤 | 为什么必须做 |
| --- | --- |
| 时间格式化 | 后续要用**字符串切片** `str[11:13]` 取小时、`str[5:7]` 取月份；格式不统一会切成垃圾 |
| 按时间升序 | 滑窗特征 `shift(i)` 的语义依赖"上一行 = 上一小时"，顺序错则特征完全错误 |
| 去重 | 重复的时间戳会让"昨日同时刻"字典出现覆盖，也可能导致数据泄漏 |
| 提前做（在特征工程前） | 保证后续所有特征都在干净、有序的数据上构造 |

**MAPE（平均绝对百分比误差）工具函数**：低版本 sklearn 没有该指标，需自己实现。但要注意这份实现有个**潜在问题**——它是误差率乘 100 **再取算术平均**，而正确口径通常是"先算 $\lvert(y-\hat y)/y\rvert$ 的均值，再乘 100"，若 $y$ 中存在 0 会除零。

$$\text{MAPE} = \frac{1}{n}\sum_{i=1}^{n}\left\lvert\frac{y_i-\hat y_i}{y_i}\right\rvert\times100\%$$

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/06-案例与面试/10-数据挖掘案例-电力负荷预测.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「数据预处理（utils/common.py）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/06-案例与面试/10-数据挖掘案例-电力负荷预测.md)
