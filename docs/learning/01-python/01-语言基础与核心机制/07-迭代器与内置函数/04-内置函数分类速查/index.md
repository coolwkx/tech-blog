---
article_id: kp-8c4e6a63f834b336
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-25d313dff349
learning_sourceId: 25d313dff349
learning_order: 3
learning_objective: 理解并验证：内置函数分类速查
---

# 内置函数分类速查

> **学习目标**：能够解释「内置函数分类速查」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：序列与字典（01 篇）、函数作为参数与 lambda（02 篇）、`yield` 生成器（06 篇）。
>
> **所属主题**：迭代器与内置函数 · 核心概念

## 本次只学这一点

| 分类 | 函数 | 说明 |
| --- | --- | --- |
| 迭代与序列 | `len` `iter` `next` `enumerate` `zip` `reversed` `sorted` `range` | 遍历与重排 |
| 聚合 | `sum` `min` `max` `any` `all` | 归约统计，`any`/`all` 短路 |
| 函数式 | `map` `filter` | 配合 `functools.reduce` 使用 |
| 类型与判断 | `type` `isinstance` `issubclass` `bool` `int` `float` `str` `list` `dict` `set` `tuple` | 转换与类型检查 |
| 数值 | `abs` `round` `divmod` `pow` `bin` `oct` `hex` | 数学与进制 |
| 自省与调试 | `id` `repr` `vars` `dir` `hasattr` `getattr` `setattr` `callable` `help` | 反射 |
| 输入输出 | `print` `input` `open` | — |
| 其他 | `chr` `ord` `hash` `format` `slice` `frozenset` `object` | — |

**注意：`reduce` 不是内置函数**，Python 3 把它移到了 `functools`（因为大部分场景用 `sum`、`max`、推导式更清晰）：
```python
from functools import reduce
reduce(lambda a, b: a + b, [3, 1, 4, 1, 5], 0) # 14
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/07-迭代器与内置函数.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「内置函数分类速查」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/07-迭代器与内置函数.md)
