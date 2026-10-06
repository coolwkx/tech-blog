---
article_id: kp-c7a84fd66e19c0de
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-2996977d7379
learning_sourceId: 2996977d7379
learning_order: 7
learning_objective: 理解并验证：== 与 is：缓存与 interning 的真相
---

# == 与 is：缓存与 interning 的真相

> **学习目标**：能够解释「== 与 is：缓存与 interning 的真相」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：基础语法（函数、类、列表/字典）；知道「引用」与「值」的区别会更顺。涉及 CPython 实现的地方都有标注，不需要 C 语言基础。
>
> **所属主题**：Python 数据模型与对象语义 · 深入机制

## 本次只学这一点

`is` 比较身份（CPython 比指针），不可重载；`==` 比较值，走 `__eq__`，失败则反射，最后回退到身份比较。**`is` 只用于单例**：`None`、`True`、`False`、`NotImplemented`、`Ellipsis`，以及自造哨兵（`_MISSING = object`）。

```python
import sys

print(1 == 1.0, 1 is 1.0) # True False
print({1: "a"}[1.0], {True: "x"}[1]) # a x —— 相等且哈希相同的键互相命中
nan = float("nan")
print(nan == nan, nan is nan) # False True（但 {nan: "v"}[nan] 能命中：字典先比身份）

print(int("256") is int("256")) # True —— 小整数缓存
print(int("257") is int("257")) # False
x = "hello"
y = "".join(["hel", "lo"])
print(x == y, x is y) # True False
print(sys.intern(y) is x) # True —— 显式驻留后是同一对象
```

| 对象 | 规则 | 能否依赖 |
| --- | --- | --- |
| 小整数 | CPython 预创建 `-5..256` 的 int 对象（`small_ints`），这些值在任何地方都是同一对象 | 不能，是实现细节 |
| 同一 code object 的常量 | `co_consts` 去重，所以同一段代码里 `"hi there" is "hi there"` 为 `True`，`10**3 is 1000` 也为 `True`（常量折叠） | 不能，位置一变就变 |
| 跨 code object 的字符串 | 只有「看起来像标识符」的常量在编译期被 intern（`hello`、`hello_world`、`x1` 是；`hello world`、`a-b`、`1.5` 不是，`sys.intern` 也不会自动生效） | 不能 |
| `sys.intern(s)` | 显式放入驻留表并返回表中的对象，适合大量重复键的解析器 | 可以，但要显式调用 |

实践结论：`if x is 5`、`if s is "abc"` 属于 bug 级写法（CPython 会给出 `SyntaxWarning`）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/01-基础与语法/01-Python数据模型与对象语义.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「== 与 is：缓存与 interning 的真相」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/01-基础与语法/01-Python数据模型与对象语义.md)
