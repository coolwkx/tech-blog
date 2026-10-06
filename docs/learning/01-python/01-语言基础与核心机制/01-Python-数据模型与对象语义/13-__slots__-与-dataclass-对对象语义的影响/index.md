---
article_id: kp-e6731d5df57c6f90
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-2996977d7379
learning_sourceId: 2996977d7379
learning_order: 12
learning_objective: 理解并验证：__slots__ 与 dataclass 对对象语义的影响
---

# __slots__ 与 dataclass 对对象语义的影响

> **学习目标**：能够解释「__slots__ 与 dataclass 对对象语义的影响」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：基础语法（函数、类、列表/字典）；知道「引用」与「值」的区别会更顺。涉及 CPython 实现的地方都有标注，不需要 C 语言基础。
>
> **所属主题**：Python 数据模型与对象语义 · 深入机制

## 本次只学这一点

| 特性 | 普通类 | `__slots__` 类 | `@dataclass` | `frozen=True` |
| --- | --- | --- | --- | --- |
| 属性存储 | `__dict__`（约 296 字节） | 固定槽位 | 同普通类 | 同普通类 |
| 新增属性 | 可以 | 未声明则 `AttributeError` | 可以 | 不可以（`FrozenInstanceError`） |
| `__eq__` | 按身份 | 按身份 | 按字段生成 | 按字段生成 |
| `__hash__` | 按身份 | 按身份 | 因生成 `__eq__` 而变成 `None` | 按字段生成 |
| 弱引用 | 支持 | 需显式加入 `"__weakref__"` | 支持 | 支持 |

```python
import sys
from dataclasses import dataclass

class WithDict:
 def __init__(self, x): self.x = x

class WithSlots:
 __slots__ = ("x",)
 def __init__(self, x): self.x = x

a, b = WithDict(1), WithSlots(1)
print(hasattr(a, "__dict__"), hasattr(b, "__dict__")) # True False
print(sys.getsizeof(a), sys.getsizeof(b)) # 48 40（CPython 3.13，64 位）

@dataclass(frozen=True)
class Point:
 x: int
 y: int = 0

@dataclass
class Mutable: x: int

print(Point(1) == Point(1), hash(Point(1)) == hash(Point(1))) # True True
print(Mutable.__hash__ is None) # True —— 生成的 __eq__ 把 __hash__ 置为 None
# hash(Mutable(1)) -> TypeError: unhashable type: 'Mutable'
```

三点提醒：`__slots__` 只省内存、加约束，不改变「一切皆对象」，子类若未定义 `__slots__` 会重新获得 `__dict__` 使优化失效；`@dataclass(eq=True)`（默认）生成 `__eq__` 从而把 `__hash__` 置为 `None`，要进 `set` 就用 `frozen=True`、`eq=False` 或 `unsafe_hash=True`；`frozen=True` 只拦属性赋值，字段内部的可变对象照样能改。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/01-基础与语法/01-Python数据模型与对象语义.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「__slots__ 与 dataclass 对对象语义的影响」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/01-基础与语法/01-Python数据模型与对象语义.md)
