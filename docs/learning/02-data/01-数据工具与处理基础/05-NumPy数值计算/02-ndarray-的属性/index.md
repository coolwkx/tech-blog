---
article_id: kp-4787e17c42355c1b
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-c0a892e8e152
learning_sourceId: c0a892e8e152
learning_order: 1
learning_objective: 理解并验证：ndarray 的属性
---

# ndarray 的属性

> **学习目标**：能够解释「ndarray 的属性」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 基础（列表、元组、字典、lambda、`import`）；了解"矩阵"的基本概念即可，无需线性代数基础。
>
> **所属主题**：-NumPy数值计算 · 核心概念

## 本次只学这一点

| 属性 | 含义 | 示例（`arr = np.arange(15).reshape(3,5)`） |
| --- | --- | --- |
| `ndarray.shape` | 维度的元组 | `(3, 5)` |
| `ndarray.ndim` | 维数（轴的个数） | `2` |
| `ndarray.size` | 元素总个数 | `15` |
| `ndarray.itemsize` | 单个元素占用的字节数 | `8`（int64） |
| `ndarray.dtype` | 元素类型 | `int64` |

属性也有等价函数写法：`np.shape(arr)`、`np.ndim(arr)`、`np.size(arr)`；类型本身是 `<class 'numpy.ndarray'>`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「ndarray 的属性」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)
