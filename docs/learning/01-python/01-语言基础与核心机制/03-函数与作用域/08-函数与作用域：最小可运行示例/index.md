---
article_id: kp-7d0547abf73b39ec
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-e8d5245408fe
learning_sourceId: e8d5245408fe
learning_order: 7
learning_objective: 理解并验证：函数与作用域：最小可运行示例
---

# 函数与作用域：最小可运行示例

> **学习目标**：能够解释「函数与作用域：最小可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：变量与赋值、可变 vs 不可变类型（见 01 篇）、`if / for / while` 基本语法。
>
> **所属主题**：函数与作用域 · 最小可运行示例

## 本次只学这一点

```text
# ---------- 1) 可变默认参数：经典陷阱与正确写法 ----------
def add_item_bad(item, box=[]): # 默认列表在"定义时"创建一次，被所有调用共享
 box.append(item)
 return box

print(add_item_bad("a")) # ['a']
print(add_item_bad("b")) # ['a', 'b'] ← 上一次的结果还在！

def add_item_ok(item, box=None): # 用 None 做哨兵，每次调用重新建列表
 if box is None:
 box = []
 box.append(item)
 return box

print(add_item_ok("a")) # ['a']
print(add_item_ok("b")) # ['b'] ← 正确

# ---------- 2) 默认值在定义时求值，而不是调用时 ----------
x = 10
def f(v=x):
 return v
x = 99
print(f) # 10，不是 99

# ---------- 3) LEGB 名字查找 ----------
g = "global"
def outer:
 e = "enclosing"
 def inner:
 l = "local"
 print(l, e, g) # local enclosing global
 inner
outer

# ---------- 4) nonlocal 让闭包持有可变状态 ----------
def counter:
 n = 0
 def inc:
 nonlocal n
 n += 1
 return n
 return inc

c1, c2 = counter, counter
print(c1, c1, c1, c2) # 1 2 3 1

# ---------- 5) 参数顺序：位置 → 默认 → *args → 仅关键字 → **kwargs ----------
def show(a, b=2, *args, **kwargs):
 return a, b, args, kwargs

print(show(1)) # (1, 2, (), {})
print(show(1, 3, 5, 7, name="wkx")) # (1, 3, (5, 7), {'name': 'wkx'})
print(show(*[1, 2, 3], **{"x": 9})) # (1, 2, (3,), {'x': 9})

# ---------- 6) 高阶函数：函数作为实参 ----------
def execute(func, data):
 return func(data)

print(execute(lambda v: v ** 2, 5)) # 25

# ---------- 7) 函数自省属性 ----------
def greet(name):
 """打招呼"""
 return f"你好 {name}"

print(greet.__name__, greet.__doc__, greet.__defaults__, greet.__annotations__)
# greet 打招呼 None {}
# ---------- 8) 可变对象作为实参：原地修改会影响外部 ----------
def modify(lst):
 lst.append(99)

data = [1, 2]
modify(data)
print("修改后:", data) # 修改后: [1, 2, 99]
```
**关键点说明**

| 位置 | 关键点 | 为什么 |
| --- | --- | --- |
| `box=[]` | 默认值在**定义时**只创建一次，存在 `add_item_bad.__defaults__` 里 | 想"每次新建"必须用 `None` 哨兵 |
| `def f(v=x)` | 默认值在定义时求值 | 解释器执行 `def` 语句时就算好并存进 `__defaults__` |
| `print(l, e, g)` | 从内到外依次找到 L、E、G | 这就是 LEGB，找到即停 |
| `nonlocal n` | 声明"n 是外层函数的变量" | 否则 `n += 1` 会让 `n` 变成局部变量并报 `UnboundLocalError` |
| `c1, c2 = counter` | 每次调用产生**独立的** `n` | 闭包保存的是各自栈帧里的 cell |
| `show(*[1,2,3], **{"x":9})` | 调用时的解包 | `*` 摊开序列，`**` 摊开字典 |
| `greet.__defaults__` | 是 `None` 而不是 `()` | 没有默认参数时该属性为 `None` |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/02-函数与装饰器/02-函数与作用域.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「函数与作用域：最小可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/02-函数与装饰器/02-函数与作用域.md)
