---
article_id: kp-8cdbd69701e661d2
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-2e1a353ffbef
learning_sourceId: 2e1a353ffbef
learning_order: 8
learning_objective: 理解并验证：装饰器与生成器：最小可运行示例
---

# 装饰器与生成器：最小可运行示例

> **学习目标**：能够解释「装饰器与生成器：最小可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数是一等对象、高阶函数、LEGB 与 `nonlocal`（02 篇）、可变默认参数陷阱（02 篇）、类与 `@property` 的宿主类（03 篇）。
>
> **所属主题**：装饰器与生成器 · 最小可运行示例

## 本次只学这一点

```text
import functools
import sys
import time

# ---------- 1) 通用装饰器模板：wraps + 透传参数 + 返回结果 ----------
def timer(func):
 @functools.wraps(func) # 保护 __name__ / __doc__
 def wrapper(*args, **kwargs): # 接收任意参数
 start = time.perf_counter # 计时必须在 wrapper 内
 result = func(*args, **kwargs)
 print(f"{func.__name__} 耗时 {time.perf_counter - start:.4f}s")
 return result # 必须把结果返回出去
 return wrapper

@timer
def slow_sum(n):
 return sum(range(n))

print("结果:", slow_sum(200000)) # slow_sum 耗时 0.0050s / 结果: 13800138000

# ---------- 2) 没有 wraps 会怎样 ----------
def plain(func):
 def wrapper(*a, **k):
 return func(*a, **k)
 return wrapper

@plain
def foo:
 """foo 的文档"""

print(foo.__name__, repr(foo.__doc__)) # wrapper None ← 元信息丢了

# ---------- 3) 多个装饰器：装饰由内到外，执行由外到内 ----------
def deco_a(func):
 @functools.wraps(func)
 def wrapper(*a, **k):
 print("A 进入"); r = func(*a, **k); print("A 退出"); return r
 return wrapper

def deco_b(func):
 @functools.wraps(func)
 def wrapper(*a, **k):
 print("B 进入"); r = func(*a, **k); print("B 退出"); return r
 return wrapper

@deco_a
@deco_b
def target:
 print(" 原函数执行")

target # A 进入 → B 进入 → 原函数执行 → B 退出 → A 退出

# ---------- 4) 带参数的装饰器：三层结构 ----------
def log(level): # 第 1 层：接收装饰器参数
 def decorator(func): # 第 2 层：接收被装饰函数
 @functools.wraps(func)
 def wrapper(*a, **k): # 第 3 层：接收调用实参
 print(f"[{level}] 调用 {func.__name__}")
 return func(*a, **k)
 return wrapper
 return decorator

@log(level="DEBUG")
def add(a, b):
 return a + b

print("add:", add(3, 4)) # [DEBUG] 调用 add / add: 7

# ---------- 5) 缓存装饰器：指数级加速 ----------
calls = {"n": 0}

@functools.lru_cache(maxsize=None)
def fib(n):
 calls["n"] += 1
 return n if n < 2 else fib(n - 1) + fib(n - 2)

print("fib(30) =", fib(30), "实际计算次数:", calls["n"]) # 832040 31

# ---------- 6) 生成器：内存对比 + 惰性 + 只能遍历一次 ----------
lst = [x ** 2 for x in range(100000)]
gen = (x ** 2 for x in range(100000))
print("列表内存:", sys.getsizeof(lst), "生成器内存:", sys.getsizeof(gen)) # 800984 200

g2 = (i for i in range(3))
print("第一次:", list(g2), "第二次:", list(g2)) # [0, 1, 2] []

def countdown(n):
 print(" 生成器启动")
 while n > 0:
 yield n # 暂停并返回值，下次从这里继续
 n -= 1
 print(" 生成器结束")

g = countdown(3)
print("next:", next(g)) # 3
print("继续:", next(g), next(g)) # 2 1
try:
 next(g)
except StopIteration:
 print("捕获到 StopIteration")

# ---------- 7) property：带校验的属性读写 ----------
class Person:
 def __init__(self, name, age):
 self.name = name
 self._age = age # 真实数据存在 _age

 @property
 def age(self):
 return self._age

 @age.setter
 def age(self, value):
 if not isinstance(value, int):
 raise TypeError("年龄必须是整数")
 if not 0 <= value <= 150:
 raise ValueError("年龄必须在 0~150 之间")
 self._age = value

 @property
 def is_adult(self):
 return self._age >= 18

p = Person("小明", 20)
print("age:", p.age, "| is_adult:", p.is_adult) # 20 | True
p.age = 25
print("setter 后:", p.age) # 25
for bad in (-5, 200, "x"):
 try:
 p.age = bad
 except (ValueError, TypeError) as e:
 print("拒绝", repr(bad), "->", type(e).__name__, e)
```

真实运行输出（节选）：

```text
slow_sum 耗时 0.0050s
结果: 13800138000
wrapper None
A 进入
B 进入
 原函数执行
B 退出
A 退出
[DEBUG] 调用 add
add: 7
fib(30) = 832040 实际计算次数: 31
列表内存: 800984 生成器内存: 200
第一次: [0, 1, 2] 第二次: []
 生成器启动
next: 3
继续: 2 1
 生成器结束
捕获到 StopIteration
age: 20 | is_adult: True
setter 后: 25
拒绝 -5 -> ValueError 年龄必须在 0~150 之间
拒绝 200 -> ValueError 年龄必须在 0~150 之间
拒绝 'x' -> TypeError 年龄必须是整数
```

**关键点说明**

| 位置 | 关键点 |
| --- | --- |
| `@functools.wraps(func)` | 复制 `__name__` / `__doc__` / `__module__`，否则调试信息全变成 `wrapper` |
| `start` 放在 `wrapper` 内 | 放在外层就是的错误写法，计时的是"装饰过程"而不是"调用过程" |
| `return result` | 漏掉则原函数返回值被吞成 `None` |
| `@deco_a` 在 `@deco_b` 上面 | 先 `deco_b` 包装、后 `deco_a` 包装；执行时 `A` 先跑 |
| `@log(level="DEBUG")` | `log(...)` 先返回 `decorator`，再由 `@` 作用到 `add` |
| `lru_cache` | 用参数做键缓存结果，把 `fib(30)` 从约 270 万次调用降到 **31 次** |
| `sys.getsizeof(gen)` 为 200 | 生成器只保存"规则 + 当前状态"，不保存数据；列表是 800984 字节 |
| `list(g2)` 第二次为 `[]` | 生成器是"一次性的迭代器"，耗尽即空 |
| `p.age = bad` 抛异常 | setter 里做校验，非法赋值不会污染 `_age` |
| `self._age` 而非 `self.age` | property 内部用同名属性会无限递归 → `RecursionError` |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/02-函数与装饰器/06-装饰器与生成器.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「装饰器与生成器：最小可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/02-函数与装饰器/06-装饰器与生成器.md)
