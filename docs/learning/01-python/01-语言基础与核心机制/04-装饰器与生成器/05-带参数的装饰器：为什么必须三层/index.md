---
article_id: kp-09c482f7c20fbfe1
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-2e1a353ffbef
learning_sourceId: 2e1a353ffbef
learning_order: 4
learning_objective: 理解并验证：带参数的装饰器：为什么必须三层
---

# 带参数的装饰器：为什么必须三层

> **学习目标**：能够解释「带参数的装饰器：为什么必须三层」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数是一等对象、高阶函数、LEGB 与 `nonlocal`（02 篇）、可变默认参数陷阱（02 篇）、类与 `@property` 的宿主类（03 篇）。
>
> **所属主题**：装饰器与生成器 · 核心概念

## 本次只学这一点

```python
def log(level): # 第 1 层：接收装饰器自己的参数
    def decorator(func): # 第 2 层：接收被装饰的函数
        @functools.wraps(func)
        def wrapper(*a, **k): # 第 3 层：接收调用时的实参
            print(f"[{level}] 调用 {func.__name__}")
            return func(*a, **k)
        return wrapper
    return decorator

@log(level="DEBUG")
def add(a, b):
    return a + b
```
`@log(level="DEBUG")` 的求值过程：先算 `log(level="DEBUG")` 得到 `decorator`，再等价于 `add = decorator(add)`。

**为什么不能写成两层 `def decorator(func, level)`？** 因为 `@` 后面的表达式求值结果必须是一个"只接收函数"的可调用对象。Python 只会把被装饰函数作为**唯一**参数传给 `@` 的结果，所以装饰器自己需要的参数必须在更外层先"固化"进闭包。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/02-函数与装饰器/06-装饰器与生成器.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「带参数的装饰器：为什么必须三层」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/02-函数与装饰器/06-装饰器与生成器.md)
