---
article_id: kp-806fddc5170d5159
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-a5477d7405c8
learning_sourceId: a5477d7405c8
learning_order: 8
learning_objective: 理解并验证：统计、逻辑与 where
---

# 统计、逻辑与 where

> **学习目标**：能够解释「统计、逻辑与 where」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：列表与嵌套结构（01 篇）、列表推导式（07 篇）、函数与类（02、03 篇）。
>
> **所属主题**：NumPy 入门 · 核心概念

## 本次只学这一点

| 分类 | 函数 |
| --- | --- |
| 聚合 | `min` `max` `mean` `median` `std` `var` `sum` `prod` |
| 下标 | `argmin` `argmax` `argsort` |
| 累计 | `cumsum` `cumprod` |
| 判空 | `isnan` `isinf` `isfinite` |
| 逻辑 | `logical_and` `logical_or` `logical_not` `all` `any` |
| 三元 | `np.where(cond, x, y)` |
| 去重/排序 | `np.unique` `np.sort()` `np.argsort` |
```python
np.unique(np.array([[1, 2, 1], [2, 3, 4]])) # [1 2 3 4]，展平后去重，返回一维新数组
np.sort(a) # 返回排序后的新数组，原数组不变
a.sort() # 原地排序，返回 None
```
**`nan` 的三个反直觉行为**：

| 行为 | 结果 | 原因 |
| --- | --- | --- |
| `np.nan == np.nan` | `False` | IEEE 754 规定 NaN 不等于任何值（包括自身） |
| `np.isnan(x)` | 判断是否 NaN 的**唯一可靠方式** | 不能用 `==` |
| `arr.sum` 含 NaN | 结果是 `nan` | NaN 会"传染" |

解决：用 `np.nansum` / `np.nanmean` / `np.nanstd`，或先 `arr[~np.isnan(arr)]` 过滤。

> `np.where` 支持嵌套实现多分支，配合 `logical_and` / `logical_or` 表达复合条件：
> ```python
> np.where(np.logical_and(tmp > 60, tmp < 90), 1, 0)
> ```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/11-NumPy入门.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「统计、逻辑与 where」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/11-NumPy入门.md)
