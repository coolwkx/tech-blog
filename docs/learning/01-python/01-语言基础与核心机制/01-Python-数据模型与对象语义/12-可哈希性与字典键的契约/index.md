---
article_id: kp-04fdd7908b094e40
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-2996977d7379
learning_sourceId: 2996977d7379
learning_order: 11
learning_objective: 理解并验证：可哈希性与字典键的契约
---

# 可哈希性与字典键的契约

> **学习目标**：能够解释「可哈希性与字典键的契约」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：基础语法（函数、类、列表/字典）；知道「引用」与「值」的区别会更顺。涉及 CPython 实现的地方都有标注，不需要 C 语言基础。
>
> **所属主题**：Python 数据模型与对象语义 · 深入机制

## 本次只学这一点

`dict` / `set` 的查找分两步：用 `hash(key)` 定位桶，再用 `==` 确认。由此得到两条硬约束：**相等必须同哈希**（`a == b` ⇒ `hash(a) == hash(b)`），**键的哈希在生命周期内必须稳定**。

```python
print(hash(1) == hash(1.0) == hash(True) == 1) # True —— 数值与布尔统一哈希
try: hash([1, 2])
except TypeError as exc: print(type(exc).__name__, exc) # unhashable type: 'list'

class CaseInsensitive: # 正确示范：__eq__ 与 __hash__ 一致
    def __init__(self, text): self.text = text
    def __eq__(self, other):
        return isinstance(other, CaseInsensitive) and self.text.lower() == other.text.lower()
    def __hash__(self): return hash(self.text.lower())

    print({CaseInsensitive("Key"): 1}[CaseInsensitive("kEy")]) # 1

    class Broken: # 只定义 __eq__，__hash__ 被隐式置为 None
        def __init__(self, text): self.text = text
        def __eq__(self, other):
            return isinstance(other, Broken) and self.text == other.text

        print(Broken.__hash__ is None) # True
        # hash(Broken("a")) -> TypeError: unhashable type: 'Broken'
```

`list` 不能做键不是语法限制而是语义不允许：它可以原地变化，哈希会失效，CPython 干脆不给它 `__hash__`。自定义类定义了 `__eq__` 却没有 `__hash__` 时，`__hash__` 被隐式设为 `None`——因为「值相等」一旦可自定义，默认的按身份哈希就不再自洽。

可哈希：`int`、`float`、`str`、`bytes`、`bool`、`None`、`frozenset`、元素全部可哈希的 `tuple`、未重载 `__eq__` 的普通类实例（按身份）。不可哈希：`list`、`dict`、`set`、任何 `__hash__` 为 `None` 的类。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/01-基础与语法/01-Python数据模型与对象语义.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「可哈希性与字典键的契约」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/01-基础与语法/01-Python数据模型与对象语义.md)
