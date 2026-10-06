---
article_id: kp-9f62e9a6416cb4ed
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-3ced58665e5a
learning_sourceId: 3ced58665e5a
learning_order: 1
learning_objective: 理解并验证：索引对齐：Pandas 最重要的一条规则
---

# 索引对齐：Pandas 最重要的一条规则

> **学习目标**：能够解释「索引对齐：Pandas 最重要的一条规则」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：NumPy 的 ndarray、广播与 `axis` 语义（11 篇）、列表/字典（01 篇）、文件读写与编码（04 篇）。
>
> **所属主题**：Pandas 数据处理 · 核心概念

## 本次只学这一点

**两个 Series/DataFrame 做运算时，优先按"行索引 / 列名"匹配，而不是按位置**。匹配不上的位置自动填 `NaN`。
```python
a = pd.Series([1, 2, 3], index=["x", "y", "z"])
b = pd.Series([10, 20], index=["y", "z"])
(a + b).to_dict # {'x': nan, 'y': 12.0, 'z': 23.0}
a.add(b, fill_value=0).to_dict # {'x': 1.0, 'y': 12.0, 'z': 23.0}
```
| 场景 | 行为 |
| --- | --- |
| `Series + 标量` | 每个元素都参与运算 |
| `Series + Series` | 按索引对齐，不匹配 → `NaN` |
| `DataFrame + 标量` | 每个元素都参与运算 |
| `DataFrame + DataFrame` | 按**行索引 + 列名**双向对齐 |
| 想要"缺失当 0" | 用 `add` / `sub` / `mul` / `div` 的 `fill_value=` |

> 这条规则是很多"结果里莫名多出 NaN"的根因。合并前先 `print(a.index.equals(b.index))` 检查一下索引是否一致。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/12-Pandas数据处理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「索引对齐：Pandas 最重要的一条规则」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/12-Pandas数据处理.md)
