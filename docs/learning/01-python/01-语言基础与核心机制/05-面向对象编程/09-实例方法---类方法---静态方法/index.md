---
article_id: kp-96d0080c003649f4
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-71dac73742c8
learning_sourceId: 71dac73742c8
learning_order: 8
learning_objective: 理解并验证：实例方法 / 类方法 / 静态方法
---

# 实例方法 / 类方法 / 静态方法

> **学习目标**：能够解释「实例方法 / 类方法 / 静态方法」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数与参数传递（02 篇）、可变 vs 不可变类型与对象身份 `id`（01 篇）、元组拆包。
>
> **所属主题**：面向对象编程 · 核心概念

## 本次只学这一点

| 类型 | 定义 | 第一个参数 | 调用方式 | 典型用途 |
| --- | --- | --- | --- | --- |
| 实例方法 | `def m(self, ...)` | `self`（实例） | `obj.m` | 绝大多数业务方法 |
| 类方法 classmethod | `@classmethod` + `def m(cls, ...)` | `cls`（类） | `Cls.m` / `obj.m` | 工厂方法、替代构造函数 |
| 静态方法 staticmethod | `@staticmethod` + `def m(...)` | 无 | `Cls.m` / `obj.m` | 与类相关的工具函数 |
```text
class Dog:
 species = "犬科"
 def __init__(self, name):
 self.name = name

 @classmethod
 def create(cls, name):
 return cls(name) # 写 cls 而不是 Dog，子类调用时才能拿到子类

 @staticmethod
 def bark:
 return "汪汪"

print(Dog.create("旺财"), Dog.species, Dog.bark) # Dog(旺财) 犬科 汪汪
```
判断标准：**要不要用到实例数据（`self`）→ 实例方法；要不要用到类数据或需要返回本类实例 → 类方法；两者都不需要 → 静态方法。**

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/03-面向对象与数据模型/03-面向对象编程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「实例方法 / 类方法 / 静态方法」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/03-面向对象与数据模型/03-面向对象编程.md)
