---
article_id: kp-c4c37cf82b7d7d9a
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-e8d5245408fe
learning_sourceId: e8d5245408fe
learning_order: 3
learning_objective: 理解并验证：变量作用域与 LEGB 规则
---

# 变量作用域与 LEGB 规则

> **学习目标**：能够解释「变量作用域与 LEGB 规则」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：变量与赋值、可变 vs 不可变类型（见 01 篇）、`if / for / while` 基本语法。
>
> **所属主题**：函数与作用域 · 核心概念

## 本次只学这一点

Python 查找一个名字时，按 **LEGB** 四级顺序，找到就停：

| 层级 | 名称 | 范围 | 例子 |
| --- | --- | --- | --- |
| **L** | Local | 当前函数的局部变量 | 函数体内的赋值 |
| **E** | Enclosing | 外层函数的局部变量（闭包场景） | 嵌套函数的父函数变量 |
| **G** | Global | 当前模块的全局变量 | 模块顶层赋值 |
| **B** | Built-in | 内置命名空间 | `len`、`print`、`ValueError` |
```text
g = "global" # G

def outer:
 e = "enclosing" # E
 def inner:
 l = "local" # L
 print(l, e, g) # local enclosing global
 inner

outer
```
两个关键推论：

1. **"赋值即声明"**：函数体里只要对某名字赋值，该名字在整个函数体内就是**局部变量**，哪怕赋值语句在读取之后。所以下面会报 `UnboundLocalError`：
 ```python
 x = 10
 def f:
 print(x) # UnboundLocalError!
 x = 20 # 这一行让 x 变成了局部变量
 ```
2. **读取不需要声明，写入才需要**：读取外层变量天然可以（E/G 层都能读），但**想改写**就必须显式声明 `global` 或 `nonlocal`。

| 声明 | 作用 | 用在哪 |
| --- | --- | --- |
| `global x` | 让函数内的 `x = ...` 写到模块全局 | 全局计数器、配置开关 |
| `nonlocal x` | 让内层函数的 `x = ...` 写到外层函数 | 闭包中的可变状态（见 06 篇） |
| 不声明 | 在函数内新建一个局部变量，遮蔽外层同名变量 | 绝大多数场景的正确做法 |
```text
count = 0
def increment:
 global count
 count += 1

increment; increment
print(count) # 2
```
```text
def counter:
 n = 0
 def inc:
 nonlocal n # 没有这行会 UnboundLocalError
 n += 1
 return n
 return inc

c1, c2 = counter, counter # 两次调用各有独立的 n
print(c1, c1, c1, c2) # 1 2 3 1
```
> `c1` 和 `c2` 的 `n` 互不影响 —— 每次调用 `counter` 都会新建一个栈帧、一套局部变量。这正是闭包能"保存状态"的原理（06 篇展开）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/02-函数与装饰器/02-函数与作用域.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「变量作用域与 LEGB 规则」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/02-函数与装饰器/02-函数与作用域.md)
