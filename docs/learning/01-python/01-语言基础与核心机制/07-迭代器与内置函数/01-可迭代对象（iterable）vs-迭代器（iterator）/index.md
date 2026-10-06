---
article_id: kp-b29f87063b3516d4
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-25d313dff349
learning_sourceId: 25d313dff349
learning_order: 0
learning_objective: 理解并验证：可迭代对象（iterable）vs 迭代器（iterator）
---

# 可迭代对象（iterable）vs 迭代器（iterator）

> **学习目标**：能够解释「可迭代对象（iterable）vs 迭代器（iterator）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：序列与字典（01 篇）、函数作为参数与 lambda（02 篇）、`yield` 生成器（06 篇）。
>
> **所属主题**：迭代器与内置函数 · 核心概念

## 本次只学这一点

| 概念 | 需要实现 | 能否被 `for` | 能否 `next` | 例子 |
| --- | --- | --- | --- | --- |
| 可迭代对象 iterable | `__iter__` | ✅ | ❌ | `list`、`dict`、`str`、`set`、`range`、文件对象 |
| 迭代器 iterator | `__iter__` + `__next__` | ✅ | ✅ | `list_iterator`、生成器、`map` / `filter` / `zip` 对象 |

关键事实（实测）：
```text
list 有 __iter__: True | 有 __next__: False
list_iterator 都有: True True
iter(it) is it: True
```
- **列表是可迭代对象但不是迭代器**：它没有 `__next__`，所以 `next([1,2])` 会报 `TypeError: 'list' object is not an iterator`；
- **迭代器一定也是可迭代对象**：它的 `__iter__` 直接返回 `self`（`iter(it) is it` 为 `True`）；
- 内置函数 `iter(x)` 调用 `x.__iter__`，`next(it)` 调用 `it.__next__`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/07-迭代器与内置函数.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「可迭代对象（iterable）vs 迭代器（iterator）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/07-迭代器与内置函数.md)
