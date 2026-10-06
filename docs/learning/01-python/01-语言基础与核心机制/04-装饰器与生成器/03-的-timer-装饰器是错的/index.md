---
article_id: kp-8b53c28c8ec509cd
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-2e1a353ffbef
learning_sourceId: 2e1a353ffbef
learning_order: 2
learning_objective: 理解并验证：的 timer 装饰器是错的
---

# 的 timer 装饰器是错的

> **学习目标**：能够解释「的 timer 装饰器是错的」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数是一等对象、高阶函数、LEGB 与 `nonlocal`（02 篇）、可变默认参数陷阱（02 篇）、类与 `@property` 的宿主类（03 篇）。
>
> **所属主题**：装饰器与生成器 · 核心概念

## 本次只学这一点

`python进阶/03-装饰器.py` 的"第 2 节 timer"写法如下：
```text
def timer(func):
 import time
 start = time.time # ❌ 在"装饰阶段"就取时间了
 func # ❌ 在装饰阶段就把原函数执行了
 end = time.time
 print(f"耗时: {end - start} 秒")
 # ❌ 没有 return wrapper

@timer
def say_hello:
 print("Hello!")
```
问题有三层：

1. `func` 在**装饰阶段**（也就是模块导入时）就被执行了，**不是**在调用 `say_hello` 时；
2. `timer` 返回 `None`，所以 `say_hello` 被重新绑定成 `None`；
3. 之后写 `say_hello` 会直接抛 `TypeError: 'NoneType' object is not callable`。

正确写法是把计时逻辑放进 `wrapper` 内部：
```python
import functools
import time

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter # ✅ 每次调用时取
        result = func(*args, **kwargs)
        print(f"{func.__name__} 耗时 {time.perf_counter - start:.4f}s")
        return result
    return wrapper

@timer
def slow(n):
    return sum(range(n))

slow(200000) # slow 耗时 0.0051s
```
> 顺带一提：计时优先用 `time.perf_counter`（单调时钟，不受系统时间调整影响），而不是 `time.time`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/02-函数与装饰器/06-装饰器与生成器.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「的 timer 装饰器是错的」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/02-函数与装饰器/06-装饰器与生成器.md)
