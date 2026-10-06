---
article_id: kp-fb3605e98cf51050
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-2e1a353ffbef
learning_sourceId: 2e1a353ffbef
learning_order: 0
learning_objective: 理解并验证：从闭包到装饰器
---

# 从闭包到装饰器

> **学习目标**：能够解释「从闭包到装饰器」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数是一等对象、高阶函数、LEGB 与 `nonlocal`（02 篇）、可变默认参数陷阱（02 篇）、类与 `@property` 的宿主类（03 篇）。
>
> **所属主题**：装饰器与生成器 · 核心概念

## 本次只学这一点

回顾闭包的三个条件：**有嵌套、有引用、有返回**。装饰器在闭包基础上加第四条：**有额外功能**。
```text
def my_decorator(func): # 外层函数：参数是"被装饰的函数"
 def wrapper: # 内层函数：将来真正替代原函数的东西
 print("开始执行...") # 额外功能（前置）
 func # 引用外层变量 func（原函数）
 print("执行完成！") # 额外功能（后置）
 return wrapper # 返回内层函数对象

@my_decorator
def say_hi:
 print("hi")
```
`@my_decorator` 完全等价于：
```text
def say_hi:
 print("hi")
say_hi = my_decorator(say_hi) # 名字被重新绑定到 wrapper
```
**装饰发生在"定义时"**：解释器读到 `@my_decorator` 那一行就立刻调用 `my_decorator(say_hi)`，把结果赋回 `say_hi`。之后每次 `say_hi` 调用的其实都是 `wrapper`。

| 概念 | 含义 |
| --- | --- |
| decorator | 接收一个函数、返回一个函数的高阶函数 |
| `@` 语法糖 | 等价于 `f = decorator(f)`，写在函数定义上一行 |
| wrapper / inner | 包装函数，负责"加料"并调用原函数 |
| 装饰时机 | 模块加载（定义）时执行一次 |
| 调用时机 | 每次调用被装饰的名字时执行 wrapper 体 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/02-函数与装饰器/06-装饰器与生成器.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「从闭包到装饰器」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/02-函数与装饰器/06-装饰器与生成器.md)
