---
article_id: kp-6a8a93c04113950e
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-c0a892e8e152
learning_sourceId: c0a892e8e152
learning_order: 3
learning_objective: 理解并验证：创建数组的常用函数
---

# 创建数组的常用函数

> **学习目标**：能够解释「创建数组的常用函数」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 基础（列表、元组、字典、lambda、`import`）；了解"矩阵"的基本概念即可，无需线性代数基础。
>
> **所属主题**：-NumPy数值计算 · 核心概念

## 本次只学这一点

| 函数 | 作用 | 关键点 |
| --- | --- | --- |
| `np.array(obj, dtype=)` | 从列表/元组等创建 | **深拷贝**，与原数据独立 |
| `np.asarray(obj, dtype=)` | 从已有数组创建 | **浅拷贝**，输入已是 ndarray 且 dtype 一致时直接返回原对象 |
| `np.ones(shape)` / `np.zeros(shape)` | 全 1 / 全 0 | 默认 dtype 为 float64 |
| `np.ones_like(a)` / `np.zeros_like(a)` | 形状与 `a` 相同的全 1 / 全 0 | 省去手写 shape |
| `np.empty(shape)` | 只分配内存、**不初始化** | 内容是内存残留值，不是"随机数" |
| `np.arange(start, stop, step)` | 等差，**按步长** | 类似 `range`，不含 stop |
| `np.linspace(start, stop, num, endpoint)` | 等差，**按数量** | 默认含 stop（`endpoint=True`） |
| `np.logspace(start, stop, num, base)` | 等比，默认底数 10 | 生成 10^x |
| `np.random.rand(d0,...)` | [0.0, 1.0) 均匀分布浮点 | 参数是各维长度，不是 shape 元组 |
| `np.random.randn(d0,...)` | 标准正态分布（μ=0, σ=1） | — |
| `np.random.normal(loc, scale, size)` | 指定均值与标准差的正态分布 | `loc` 决定图形左右位置、`scale` 决定瘦高或矮胖 |
| `np.random.uniform(low, high, size)` | 指定区间的均匀分布 | — |
| `np.random.randint(low, high, size)` | 指定区间的整数 | 左闭右开 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「创建数组的常用函数」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)
