---
article_id: kp-9f4aeaa9177cbb0f
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-c0a892e8e152
learning_sourceId: c0a892e8e152
learning_order: 0
learning_objective: 理解并验证：NumPy 是什么，为什么快
---

# NumPy 是什么，为什么快

> **学习目标**：能够解释「NumPy 是什么，为什么快」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 基础（列表、元组、字典、lambda、`import`）；了解"矩阵"的基本概念即可，无需线性代数基础。
>
> **所属主题**：-NumPy数值计算 · 核心概念

## 本次只学这一点

NumPy（Numerical Python）是开源科学计算库，**用于快速处理任意维度的数组**，核心对象是 `ndarray`（N-dimensional array），描述"**相同类型** items 的集合"。与原生 `list` 的效率对比（实测：1 亿个随机数求和）：

| 方式 | 耗时（Wall time） | 说明 |
| --- | --- | --- |
| Python `sum(list)` | **1.13 s** | 逐个取出 Python 对象、解引用、调用 `__add__` |
| `np.sum(ndarray)` | **134 ms** | 连续内存 + C 循环 + 向量化 |

| 快的原因 | 说明 |
| --- | --- |
| 内存块风格 | `ndarray` 所有元素类型相同，数据地址**连续**，批量操作无需寻址跳转；`list` 存的是**指针**，元素对象散落在堆上，是"分离式存储" |
| 向量化/并行运算 | 一次操作作用到整个数组，省掉显式循环；多核时自动并行 |
| 底层 C 实现、释放 GIL | 数组运算不受 Python 逐行执行与全局解释器锁的限制 |

代价：`ndarray` 要求元素**同构**，通用性不如 `list`，但在数值计算场景下这个约束正好换来性能。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「NumPy 是什么，为什么快」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)
