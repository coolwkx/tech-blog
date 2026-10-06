---
article_id: kp-7f66aca98cc49bda
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-71dac73742c8
learning_sourceId: 71dac73742c8
learning_order: 2
learning_objective: 理解并验证：__init__ / __str__ / __del__ 三个最常用的魔法方法
---

# __init__ / __str__ / __del__ 三个最常用的魔法方法

> **学习目标**：能够解释「__init__ / __str__ / __del__ 三个最常用的魔法方法」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数与参数传递（02 篇）、可变 vs 不可变类型与对象身份 `id`（01 篇）、元组拆包。
>
> **所属主题**：面向对象编程 · 核心概念

## 本次只学这一点

魔法方法（magic method / dunder method）以双下划线包围，**由解释器在特定时机自动调用**，不需要手动写。

| 魔法方法 | 触发时机 | 典型用途 |
| --- | --- | --- |
| `__init__(self, ...)` | 对象创建后立即调用 | 初始化实例属性 |
| `__new__(cls, ...)` | 更早，负责"创建"对象本体 | 单例、不可变类型子类化（进阶） |
| `__str__(self)` | `print(obj)` / `str(obj)` / f-string | 给人看的可读表示 |
| `__repr__(self)` | 交互式环境直接输入对象、`repr(obj)` | 给开发者看的、尽量能重建对象 |
| `__del__(self)` | 对象引用计数归零、程序退出时 | 释放外部资源（但**不要依赖它**） |
| `__eq__` / `__hash__` | `==` / `hash` | 值语义比较、放进 set |
| `__len__` / `__getitem__` | `len(obj)` / `obj[i]` | 让自定义对象"像序列" |
```python
class Car:
    def __init__(self, color, number): # 创建对象时自动调用
        self.color = color
        self.number = number

        def __str__(self): # print(car) 时自动调用
            return f"车的颜色:{self.color},轮胎个数:{self.number}"

        print(Car("Red", 4)) # 车的颜色:Red,轮胎个数:4
```
> `__del__` 的定位：它由**垃圾回收**触发，触发时机不确定（循环引用时甚至可能不触发）。真正要"确保释放"的资源（文件、连接）请用 `with` 上下文管理器（04 篇），不要写 `__del__`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/03-面向对象与数据模型/03-面向对象编程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「__init__ / __str__ / __del__ 三个最常用的魔法方法」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/03-面向对象与数据模型/03-面向对象编程.md)
