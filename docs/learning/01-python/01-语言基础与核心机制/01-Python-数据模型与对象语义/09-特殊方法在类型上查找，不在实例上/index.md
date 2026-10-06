---
article_id: kp-d41e0af0f0f2cb6f
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-2996977d7379
learning_sourceId: 2996977d7379
learning_order: 8
learning_objective: 理解并验证：特殊方法在类型上查找，不在实例上
---

# 特殊方法在类型上查找，不在实例上

> **学习目标**：能够解释「特殊方法在类型上查找，不在实例上」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：基础语法（函数、类、列表/字典）；知道「引用」与「值」的区别会更顺。涉及 CPython 实现的地方都有标注，不需要 C 语言基础。
>
> **所属主题**：Python 数据模型与对象语义 · 深入机制

## 本次只学这一点

```python
class Bag:
 def __init__(self, items): self._items = list(items)
 def __len__(self): return len(self._items)
 def __getitem__(self, index): return self._items[index]
 def __contains__(self, value): return value in self._items

bag = Bag([10, 20, 30])
print(len(bag), bag[1], 20 in bag) # 3 20 True
print(list(bag)) # [10, 20, 30] —— 没有 __iter__，靠 __getitem__ 旧协议

bag.__len__ = lambda: 999 # 挂到实例字典上
print(bag.__len__, len(bag)) # 999 3 —— 内置函数忽略实例属性
```

`len(bag)` 仍返回 `3`：`len` 走 C 层 `PyObject_Size` → `type(bag)` 的类型槽（`sq_length`），完全绕开实例 `__dict__`。由此得到三条实践规则：

- 特殊方法必须定义在**类**上，`self.__len__ = ...` 对内置函数无效；
- 内置函数提供回退：`iter(bag)` 在没有 `__iter__` 时退化为 `bag[0]`、`bag[1]`… 直到 `IndexError`，而 `bag.__iter__` 直接 `AttributeError`；
- 内置函数承担校验：`__len__` 返回负数抛 `ValueError: __len__ should return >= 0`，返回非整数抛 `TypeError`；没有长度语义的对象（如生成器）得到明确的 `TypeError: object of type 'generator' has no len`，而不是默默返回 `0`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/01-基础与语法/01-Python数据模型与对象语义.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「特殊方法在类型上查找，不在实例上」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/01-基础与语法/01-Python数据模型与对象语义.md)
