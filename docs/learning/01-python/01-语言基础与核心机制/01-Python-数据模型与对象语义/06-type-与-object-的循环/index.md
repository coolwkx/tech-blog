---
article_id: kp-a590409735f15e93
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-2996977d7379
learning_sourceId: 2996977d7379
learning_order: 5
learning_objective: 理解并验证：type 与 object 的循环
---

# type 与 object 的循环

> **学习目标**：能够解释「type 与 object 的循环」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：基础语法（函数、类、列表/字典）；知道「引用」与「值」的区别会更顺。涉及 CPython 实现的地方都有标注，不需要 C 语言基础。
>
> **所属主题**：Python 数据模型与对象语义 · 深入机制

## 本次只学这一点

```python
print(type(3) is int) # True
print(type(int) is type) # True
print(type(type) is type) # True
print(type(object) is type) # True
print(object.__bases__) # 
print(type.__bases__) # (<class 'object'>,)
print(isinstance(object, type)) # True
print(int.__mro__) # (<class 'int'>, <class 'object'>)
```

类也是对象，其类型是 `type`（自定义元类替换这个位置）；`object` 是所有类的基类且自身没有基类；`isinstance` 检查 `type(x)` 是否在目标类的 MRO 中，所以子类实例也算。判断类型优先用 `isinstance`，只有明确要排除子类时才写 `type(x) is C`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/01-基础与语法/01-Python数据模型与对象语义.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「type 与 object 的循环」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/01-基础与语法/01-Python数据模型与对象语义.md)
