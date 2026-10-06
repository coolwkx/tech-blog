---
article_id: kp-c83a216e278fd7ab
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-2e1a353ffbef
learning_sourceId: 2e1a353ffbef
learning_order: 7
learning_objective: 理解并验证：@property：把方法伪装成属性
---

# @property：把方法伪装成属性

> **学习目标**：能够解释「@property：把方法伪装成属性」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数是一等对象、高阶函数、LEGB 与 `nonlocal`（02 篇）、可变默认参数陷阱（02 篇）、类与 `@property` 的宿主类（03 篇）。
>
> **所属主题**：装饰器与生成器 · 核心概念

## 本次只学这一点

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self._age = age

        @property
        def age(self): # getter
            return self._age

        @age.setter
        def age(self, value): # setter
            if not 0 <= value <= 150:
                raise ValueError("年龄必须在 0~150 之间")
            self._age = value

            @property
            def is_adult(self): # 只读的派生属性
                return self._age >= 18
```
| 装饰器 | 作用 |
| --- | --- |
| `@property` | 定义 getter，方法变成"只读属性" |
| `@x.setter` | 定义 setter，赋值时做校验 |
| `@x.deleter` | 定义 `del obj.x` 的行为 |

**为什么要用 property 而不是直接暴露属性？**

| 方案 | 优点 | 缺点 |
| --- | --- | --- |
| 公有属性 `self.age = age` | 简单、快 | 无法校验、无法在未来改成计算属性而不破坏调用方 |
| `get_age` / `set_age` | 可校验 | Java 风格，调用方要改写法 |
| `@property` | 调用写法不变（`p.age`），内部可校验/计算/惰性 | 略有性能开销；容易被误以为"廉价" |

**关键优势**：`p.age` 的调用形式在"直接属性 → property"之间**不变**，所以可以先把属性写成公有的，等需要校验时再升级成 property，调用方代码一行都不用改。

`type(Person.age)` 是 `<class 'property'>` —— 说明 property 是一个**数据描述符**，放在类上拦截了实例属性的读写。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/02-函数与装饰器/06-装饰器与生成器.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「@property：把方法伪装成属性」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/02-函数与装饰器/06-装饰器与生成器.md)
