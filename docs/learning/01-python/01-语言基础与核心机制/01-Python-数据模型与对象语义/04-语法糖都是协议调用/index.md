---
article_id: kp-f5f42650f1cdcf39
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-2996977d7379
learning_sourceId: 2996977d7379
learning_order: 3
learning_objective: 理解并验证：语法糖都是协议调用
---

# 语法糖都是协议调用

> **学习目标**：能够解释「语法糖都是协议调用」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：基础语法（函数、类、列表/字典）；知道「引用」与「值」的区别会更顺。涉及 CPython 实现的地方都有标注，不需要 C 语言基础。
>
> **所属主题**：Python 数据模型与对象语义 · 核心思想

## 本次只学这一点

`len`、`for`、`in`、`[]` 不检查「对象是不是 list」，而是在**类型**上查对应 dunder 再调用：

| 写法 | 实际走的协议 | 找不到时的回退 |
| --- | --- | --- |
| `len(x)` | `type(x).__len__(x)` | 无回退，抛 `TypeError`；返回值为负抛 `ValueError` |
| `x[k]` | `type(x).__getitem__(x, k)` | 无回退（赋值 `__setitem__`，删除 `__delitem__`） |
| `for i in x` | `iter(x)` → `type(x).__iter__(x)` | 旧式序列协议：反复 `__getitem__(0), __getitem__(1), ...` 直到 `IndexError` |
| `v in x` | `type(x).__contains__(x, v)` | 回退 `__iter__`，再回退 `__getitem__` |
| `x == y` | `type(x).__eq__(x, y)` | 返回 `NotImplemented` 则反射 `type(y).__eq__(y, x)`，最后回退 `is` |
| `x + y` | `type(x).__add__(x, y)` | 反射 `type(y).__radd__(y, x)` |
| `x += y` | `type(x).__iadd__(x, y)` | 退化为 `x = x + y`，即**重新绑定名字** |
| `hash(x)` | `type(x).__hash__(x)` | `object.__hash__` 由身份派生；类型里是 `None` 则抛 `TypeError` |
| `str(x)` | `__str__` | `__str__` 缺失时回退 `__repr__` |

**为什么用内置函数而不是直接调 dunder**：内置函数在**类型**上查找，并补上回退与校验；`x.__len__` 只是普通属性查找，会命中实例字典、拿不到旧协议能力。第 4.4 节有可运行证明。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/01-基础与语法/01-Python数据模型与对象语义.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「语法糖都是协议调用」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/01-基础与语法/01-Python数据模型与对象语义.md)
