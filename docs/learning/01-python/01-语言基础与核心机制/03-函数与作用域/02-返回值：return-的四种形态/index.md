---
article_id: kp-267e661252671f0a
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-e8d5245408fe
learning_sourceId: e8d5245408fe
learning_order: 1
learning_objective: 理解并验证：返回值：return 的四种形态
---

# 返回值：return 的四种形态

> **学习目标**：能够解释「返回值：return 的四种形态」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：变量与赋值、可变 vs 不可变类型（见 01 篇）、`if / for / while` 基本语法。
>
> **所属主题**：函数与作用域 · 核心概念

## 本次只学这一点

| 写法 | 返回值 | 类型 | 说明 |
| --- | --- | --- | --- |
| 没有 `return` | `None` | `NoneType` | 隐式返回，不是"没有返回值" |
| `return` | `None` | `NoneType` | 等价于提前结束函数 |
| `return x` | `x` | 任意 | 返回单个对象 |
| `return a, b` | `(a, b)` | `tuple` | **本质是返回一个元组**，靠拆包接住 |
```python
def sum_odd_even(numbers):
    odd = even = 0
    for n in numbers:
        if n % 2 == 0:
            even += n
        else:
            odd += n
            return odd, even # 返回元组 (odd, even)

        odd, even = sum_odd_even([1, 2, 3, 4, 5, 6, 7, 8])
        print(odd, even) # 16 20
```
> 为什么 `return a, b` 是元组？因为逗号本身构造元组，`return` 只是把这个元组交出去。理解这一点后 `x, y = f` 就是普通的元组拆包，不是特例。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/02-函数与装饰器/02-函数与作用域.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「返回值：return 的四种形态」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/02-函数与装饰器/02-函数与作用域.md)
