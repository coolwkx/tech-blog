---
article_id: kp-b66b366873f26000
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-2996977d7379
learning_sourceId: 2996977d7379
learning_order: 6
learning_objective: 理解并验证：名字绑定与 dis 字节码
---

# 名字绑定与 dis 字节码

> **学习目标**：能够解释「名字绑定与 dis 字节码」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：基础语法（函数、类、列表/字典）；知道「引用」与「值」的区别会更顺。涉及 CPython 实现的地方都有标注，不需要 C 语言基础。
>
> **所属主题**：Python 数据模型与对象语义 · 深入机制

## 本次只学这一点

```python
import dis

def total(seq):
    s = 0
    for item in seq:
        s += item
        return s

    dis.dis(total)
```

```text
 3 RESUME 0
 4 LOAD_CONST 1 (0)
 STORE_FAST 1 (s)
 5 LOAD_FAST 0 (seq)
 GET_ITER
 L1: FOR_ITER 7 (to L2)
 STORE_FAST 2 (item)
 6 LOAD_FAST_LOAD_FAST 18 (s, item)
 BINARY_OP 13 (+=)
 STORE_FAST 1 (s)
 JUMP_BACKWARD 9 (to L1)
 5 L2: END_FOR
 ... （后续为 POP_TOP / LOAD_FAST / RETURN_VALUE，略）
```

迭代对象来自 `GET_ITER`（即 `iter(seq)`），不是下标遍历。`s += item` 编译成 `BINARY_OP 13 (+=)`：运行时先试 `__iadd__`，不可用则退化为 `__add__`，然后**无条件 `STORE_FAST s`**——所以「`+=` 一定是原地修改」是错的，对不可变对象它等价于 `s = s + item`。含 `STORE` 的名字还会被编译器判定为局部变量，这正是下面这个高频错误的原因：

```text
counter = 0

def bump:
 counter += 1 # 含 STORE，counter 被判定为局部变量

try:
 bump
except UnboundLocalError as exc:
 print(type(exc).__name__, exc)
 # UnboundLocalError cannot access local variable 'counter' where it is not associated with a value
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/01-基础与语法/01-Python数据模型与对象语义.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「名字绑定与 dis 字节码」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/01-基础与语法/01-Python数据模型与对象语义.md)
