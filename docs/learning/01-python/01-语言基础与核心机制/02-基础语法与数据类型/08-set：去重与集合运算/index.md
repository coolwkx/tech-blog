---
article_id: kp-68ad7fbf490ffacd
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-c695752cdddc
learning_sourceId: c695752cdddc
learning_order: 7
learning_objective: 理解并验证：set：去重与集合运算
---

# set：去重与集合运算

> **学习目标**：能够解释「set：去重与集合运算」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：会安装并运行 Python（3.8+）；知道变量、`print`、`input` 的基本用法；了解 `int / float / str / bool` 四种标量类型。
>
> **所属主题**：基础语法与数据类型 · 核心概念

## 本次只学这一点

```python
nums = {1, 2, 3, 2, 4} # 自动去重 → {1, 2, 3, 4}
empty = set # 空集合必须这样写，{} 是空字典！
nums.add(8) # 添加元素用 add，不是 append
nums.remove(1) # 不存在会报 KeyError
nums.discard(999) # 不存在也不报错
```
| 运算 | 运算符 | 方法 | 含义 |
| --- | --- | --- | --- |
| 并集 | `a \| b` | `a.union(b)` | 两边都算 |
| 交集 | `a & b` | `a.intersection(b)` | 两边都有 |
| 差集 | `a - b` | `a.difference(b)` | 只在 a 中 |
| 对称差 | `a ^ b` | `a.symmetric_difference(b)` | 只在一侧 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/01-基础与语法/01-基础语法与数据类型.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「set：去重与集合运算」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/01-基础与语法/01-基础语法与数据类型.md)
