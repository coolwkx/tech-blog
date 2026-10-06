---
article_id: kp-04937a58bbaa498a
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-a5477d7405c8
learning_sourceId: a5477d7405c8
learning_order: 3
learning_objective: 理解并验证：创建数组的方法
---

# 创建数组的方法

> **学习目标**：能够解释「创建数组的方法」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：列表与嵌套结构（01 篇）、列表推导式（07 篇）、函数与类（02、03 篇）。
>
> **所属主题**：NumPy 入门 · 核心概念

## 本次只学这一点

| 分类 | 函数 | 说明 |
| --- | --- | --- |
| 从序列 | `np.array(obj, dtype=)` | **拷贝**数据，得到新数组 |
| 从序列 | `np.asarray(obj, dtype=)` | 若已是 ndarray 且 dtype 一致 → **不拷贝，直接返回原对象** |
| 全 0 / 全 1 | `np.zeros(shape, dtype)` / `np.ones(shape, dtype)` | 默认 `float64` |
| 形状参照 | `np.zeros_like(a)` / `np.ones_like(a)` | 与 `a` 同形状同类型 |
| 未初始化 | `np.empty(shape)` | 速度快，内容是内存残留，**必须先赋值** |
| 等差（指定步长） | `np.arange(start, stop, step)` | **包左不包右**，类似 `range` |
| 等差（指定个数） | `np.linspace(start, stop, num, endpoint=True)` | **默认包左包右** |
| 等比 | `np.logspace(start, stop, num, base=10)` | 生成 `base^start ~ base^stop` |
| 单位矩阵 | `np.eye(n)` / `np.identity(n)` | 对角线为 1 |
| 随机 | `np.random.rand(...)` / `uniform` / `randint` / `randn` / `normal` | 见下表 |

**`arange` vs `linspace` 的关键区别**：
```python
np.arange(10, 50, 2) # 指定"步长" → [10 12 14 ... 48]
np.linspace(0, 100, 11) # 指定"个数" → [0. 10. 20. ... 100.]
np.linspace(1, 10, 10, endpoint=False) # [1. 1.9 2.8 ... 9.1]，不包含终点
```
**随机数函数**：

| 函数 | 分布 | 示例 |
| --- | --- | --- |
| `np.random.rand(d0, d1, ...)` | `[0,1)` 均匀，参数是**形状** | `rand(3, 4)` |
| `np.random.uniform(low, high, size)` | `[low, high)` 均匀，可指定范围 | `uniform(-1, 5, (3, 4))` |
| `np.random.randint(low, high, size)` | 整数均匀，**包左不包右** | `randint(1, 100, (4, 3))` |
| `np.random.randn(d0, d1, ...)` | 标准正态 `N(0,1)` | `randn(3, 4)` |
| `np.random.normal(loc, scale, size)` | 任意正态，`loc`=均值、`scale`=标准差 | `normal(0, 1, 100)` |
| `np.random.default_rng(seed)` | **新版推荐入口** | `rng.integers(1, 10, 5)` |

> 可复现性：固定种子才能复现实验。新版 API 推荐 `rng = np.random.default_rng(42)`，然后用 `rng.random` / `rng.integers` / `rng.normal`；老式全局 `np.random.seed(42)` 仍然可用，但会污染全局状态。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/11-NumPy入门.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「创建数组的方法」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/11-NumPy入门.md)
