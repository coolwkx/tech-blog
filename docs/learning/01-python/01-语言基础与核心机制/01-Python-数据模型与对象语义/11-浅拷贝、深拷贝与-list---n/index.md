---
article_id: kp-f4fdb38562cfc335
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-2996977d7379
learning_sourceId: 2996977d7379
learning_order: 10
learning_objective: 理解并验证：浅拷贝、深拷贝与 list * n
---

# 浅拷贝、深拷贝与 list * n

> **学习目标**：能够解释「浅拷贝、深拷贝与 list * n」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：基础语法（函数、类、列表/字典）；知道「引用」与「值」的区别会更顺。涉及 CPython 实现的地方都有标注，不需要 C 语言基础。
>
> **所属主题**：Python 数据模型与对象语义 · 深入机制

## 本次只学这一点

| 操作 | 外层 | 内层 | 循环引用 | 用途 |
| --- | --- | --- | --- | --- |
| `b = a` | 同一对象 | 共享 | 原样 | 起别名，不是拷贝 |
| `copy.copy(a)` / `list(a)` / `a[:]` | 新对象 | **共享** | 不修复 | 只需外层独立 |
| `copy.deepcopy(a)` | 新对象 | 递归新对象 | 靠 `memo` 修复成自洽的图 | 需要完全独立副本 |
| `[x] * n` | 新列表，n 个槽指向**同一个** `x` | 共享 | — | 只适合不可变元素 |

```python
import copy

inner = [1, 2]
data = {"k": inner}
shallow, deep = copy.copy(data), copy.deepcopy(data)
inner.append(3)
print(shallow, deep) # {'k': [1, 2, 3]} {'k': [1, 2]}

cyc = []
cyc.append(cyc) # 自引用
print(copy.copy(cyc)[0] is cyc) # True —— 浅拷贝不修复循环
dcyc = copy.deepcopy(cyc)
print(dcyc[0] is dcyc) # True —— deepcopy 让副本自洽

grid = [[0] * 2] * 2 # 两个槽指向同一个内层 list
grid[0][0] = 1
print(grid, grid[0] is grid[1]) # [[1, 0], [1, 0]] True
grid2 = [[0] * 2 for _ in range(2)] # 每次迭代新建内层 list
grid2[0][0] = 1
print(grid2) # [[1, 0], [0, 0]]
```

`deepcopy` 靠 `memo`（已复制对象表）保证循环引用不会无限递归，并保留副本内部的共享关系（同一个原对象在副本里仍只对应一个对象）。它按类型工作：自定义类默认可通过 `__reduce_ex__` 协议深拷贝，持有 socket、文件句柄、锁等不可拷贝资源时需要自己实现 `__deepcopy__`。`[0] * 2` 安全是因为 `0` 不可变；判断标准永远是「元素是否可变」。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/01-基础与语法/01-Python数据模型与对象语义.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「浅拷贝、深拷贝与 list * n」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/01-基础与语法/01-Python数据模型与对象语义.md)
