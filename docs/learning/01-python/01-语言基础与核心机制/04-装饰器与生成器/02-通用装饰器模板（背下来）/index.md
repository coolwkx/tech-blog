---
article_id: kp-b74f8db945d3a0d8
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-2e1a353ffbef
learning_sourceId: 2e1a353ffbef
learning_order: 1
learning_objective: 理解并验证：通用装饰器模板（背下来）
---

# 通用装饰器模板（背下来）

> **学习目标**：能够解释「通用装饰器模板（背下来）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数是一等对象、高阶函数、LEGB 与 `nonlocal`（02 篇）、可变默认参数陷阱（02 篇）、类与 `@property` 的宿主类（03 篇）。
>
> **所属主题**：装饰器与生成器 · 核心概念

## 本次只学这一点

原函数可能有参数也可能有返回值，所以 wrapper 必须"透传"：
```python
import functools

def decorator(func):
    @functools.wraps(func) # 保护原函数的元信息
    def wrapper(*args, **kwargs): # 接收任意参数
        # === 前置增强 ===
        result = func(*args, **kwargs) # 调用原函数
        # === 后置增强 ===
        return result # 必须把结果返回出去
    return wrapper
```
| 必须做的三件事 | 漏掉的后果 |
| --- | --- |
| `*args, **kwargs` 透传参数 | 原函数带参时 `TypeError` |
| `return result` | 调用者拿到 `None`，链式调用断裂 |
| `@functools.wraps(func)` | `__name__` 变成 `"wrapper"`、`__doc__` 丢失，日志/调试/框架按名字查找全部失效 |

实测对比：
```text
无 wraps: wrapper None
有 wraps: bar 'bar 的文档'
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/02-函数与装饰器/06-装饰器与生成器.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「通用装饰器模板（背下来）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/02-函数与装饰器/06-装饰器与生成器.md)
