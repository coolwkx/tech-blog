---
article_id: kp-aedc41f097f62ea4
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-a5477d7405c8
learning_sourceId: a5477d7405c8
learning_order: 5
learning_objective: 理解并验证：形状操作
---

# 形状操作

> **学习目标**：能够解释「形状操作」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：列表与嵌套结构（01 篇）、列表推导式（07 篇）、函数与类（02、03 篇）。
>
> **所属主题**：NumPy 入门 · 核心概念

## 本次只学这一点

| 操作 | 方法 | 是否改原数组 | 是否共享内存 |
| --- | --- | --- | --- |
| 改形状（返回新视图） | `a.reshape(2, 3)` | ❌ | ✅ 视图（前提是内存连续） |
| 改形状（原地） | `a.resize(2, 3)` / `a.shape = (2, 3)` | ✅ | — |
| 拉平（拷贝） | `a.flatten` | ❌ | ❌ 拷贝 |
| 拉平（视图） | `a.ravel` | ❌ | ✅ 尽量返回视图 |
| 行列互换 | `a.T` / `a.transpose` | ❌ | ✅ 视图 |
| 交换轴 | `a.swapaxes(0, 1)` | ❌ | ✅ 视图 |
| 自动推断维度 | `a.reshape(-1)` / `a.reshape(2, -1)` | ❌ | ✅ 视图 |
| 拼接 | `np.vstack` / `np.hstack` / `np.concatenate` | ❌ | ❌ 新数组 |
| 切分 | `np.split()` / `np.hsplit` / `np.vsplit` | ❌ | ✅ 视图 |
```python
x = np.arange(6)
r = x.reshape(2, 3)
print(np.shares_memory(x, r)) # True → reshape 是视图
print(np.shares_memory(x, r.flatten)) # False → flatten 是拷贝
```
> **`-1` 的含义**：让 NumPy 自己算这个维度。`m.reshape(-1)` 等价于拉平，`a.reshape(2, -1)` 表示"2 行，列数自己算"。这是处理"不确定行数"场景的常用技巧。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/11-NumPy入门.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「形状操作」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/11-NumPy入门.md)
