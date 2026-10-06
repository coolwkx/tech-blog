---
article_id: kp-f185bdb05b95d818
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-e8d5245408fe
learning_sourceId: e8d5245408fe
learning_order: 2
learning_objective: 理解并验证：参数四件套与"绑定顺序"
---

# 参数四件套与"绑定顺序"

> **学习目标**：能够解释「参数四件套与"绑定顺序"」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：变量与赋值、可变 vs 不可变类型（见 01 篇）、`if / for / while` 基本语法。
>
> **所属主题**：函数与作用域 · 核心概念

## 本次只学这一点

| 参数形式 | 写法 | 接收内容 | 注意 |
| --- | --- | --- | --- |
| 位置参数 positional | `def f(a, b)` | 按顺序一一对应 | 数量不匹配抛 `TypeError` |
| 关键字参数 keyword | `f(b=1, a=2)` | 按名字对应 | 提高了可读性，顺序可打乱 |
| 默认参数 default | `def f(a, b=10)` | 不传就用默认值 | **默认值在函数定义时求值一次** |
| 可变位置 `*args` | `def f(*args)` | 打包成 `tuple` | 名字可以是别的，`*` 才是关键 |
| 可变关键字 `**kwargs` | `def f(**kwargs)` | 打包成 `dict` | 同上 |
| 仅关键字参数 | `def f(a, *, b)` | `b` 只能按关键字传 | Python 3 特性，提高接口安全性 |
| 仅位置参数 | `def f(a, /, b)` | `a` 只能按位置传 | Python 3.8+，可用于 API 兼容 |

**定义时的书写顺序（背下来）**：
```text
位置参数 → 默认参数 → *args → 仅关键字参数 → **kwargs
def f(a, b=1, *args, c, d=2, **kwargs): ...
```
**调用时的传参规则**：关键字参数必须在位置参数之后；同一个参数不能既按位置又按关键字传（`f(1, a=1)` 会报 `TypeError: got multiple values for argument 'a'`）。

打包与解包是一对：
```python
def show(a, b, *args, **kwargs):
 return a, b, args, kwargs

nums = [1, 2, 3]
extra = {"x": 9}
print(show(*nums, **extra)) # (1, 2, (3,), {'x': 9})
```
- **打包**：定义时 `*args` 把多余的位置实参收进元组，`**kwargs` 把多余的关键字实参收进字典。
- **解包**：调用时 `*nums` 把列表"摊开"成多个位置实参，`**extra` 把字典摊开成多个关键字实参。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/02-函数与装饰器/02-函数与作用域.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「参数四件套与"绑定顺序"」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/02-函数与装饰器/02-函数与作用域.md)
