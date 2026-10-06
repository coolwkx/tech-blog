---
article_id: kp-f3f70db8bf36ee3f
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-25d313dff349
learning_sourceId: 25d313dff349
learning_order: 4
learning_objective: 理解并验证：重点函数逐个说清
---

# 重点函数逐个说清

> **学习目标**：能够解释「重点函数逐个说清」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：序列与字典（01 篇）、函数作为参数与 lambda（02 篇）、`yield` 生成器（06 篇）。
>
> **所属主题**：迭代器与内置函数 · 核心概念

## 本次只学这一点

| 函数 | 签名要点 | 输出示例（`nums = [3,1,4,1,5]`） |
| --- | --- | --- |
| `enumerate(it, start=0)` | 产出 `(下标, 元素)` 元组 | `list(enumerate("abc", 1))` → `[(1,'a'),(2,'b'),(3,'c')]` |
| `zip(*its)` | 按**最短**的截断 | `list(zip([1,2],"abcd"))` → `[(1,'a'),(2,'b')]` |
| `map(f, it)` | 惰性，返回 map 对象 | `list(map(lambda x: x*2, nums))` → `[6,2,8,2,10]` |
| `filter(f, it)` | `f` 返回真值才保留，惰性 | `list(filter(lambda x: x>2, nums))` → `[3,4,5]` |
| `sorted(it, key, reverse)` | 返回**新列表**，稳定排序 | `sorted(nums)` → `[1,1,3,4,5]` |
| `reversed(seq)` | 需要 `__reversed__` 或 `__len__`+`__getitem__` | `list(reversed([1,2,3]))` → `[3,2,1]` |
| `any` / `all` | 短路求值 | `any(x>4 for x in nums)` → `True` |
| `min` / `max` | 支持 `key=` 和 `default=` | `max(nums)` → `5` |
| `divmod(a, b)` | 同时得到商和余 | `divmod(17, 5)` → `(3, 2)` |
| `sum(it, start=0)` | `start` 对字符串无效 | `sum(nums)` → `14` |

> `zip(*its)` 配合拆包能实现"矩阵转置"：`list(zip(*[[1,2],[3,4]]))` → `[(1,3),(2,4)]`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/07-迭代器与内置函数.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「重点函数逐个说清」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/07-迭代器与内置函数.md)
