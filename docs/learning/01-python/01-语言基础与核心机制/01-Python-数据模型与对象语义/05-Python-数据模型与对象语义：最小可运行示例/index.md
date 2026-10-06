---
article_id: kp-d3d8cc50840a1da8
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-2996977d7379
learning_sourceId: 2996977d7379
learning_order: 4
learning_objective: 理解并验证：Python 数据模型与对象语义：最小可运行示例
---

# Python 数据模型与对象语义：最小可运行示例

> **学习目标**：能够解释「Python 数据模型与对象语义：最小可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：基础语法（函数、类、列表/字典）；知道「引用」与「值」的区别会更顺。涉及 CPython 实现的地方都有标注，不需要 C 语言基础。
>
> **所属主题**：Python 数据模型与对象语义 · 最小可运行示例

## 本次只学这一点

```python
import copy

# 1) 对象三元组：id / type / 值
a = [1, 2, 3]
b = [1, 2, 3]
print(type(a), a == b, a is b) # <class 'list'> True False

# 2) 名字绑定：alias 与 a 是同一个对象
alias = a
alias.append(4)
print(a) # [1, 2, 3, 4]

# 3) += 走 __iadd__（原地），+ 走 __add__（新建并重新绑定）
m = [1]
n = m
m += [2]
p = [1]
q = p
p = p + [2]
print(m, n, p, q) # [1, 2] [1, 2] [1, 2] [1]

# 4) 浅拷贝共享内层，深拷贝不共享
inner = [1]
shallow = copy.copy([inner])
deep = copy.deepcopy([inner])
inner.append(2)
print(shallow, deep) # [[1, 2]] [[1]]

# 5) 可变默认参数的正确写法：None 哨兵
def collect(value, acc=None):
 acc = [] if acc is None else acc
 acc.append(value)
 return acc

print(collect(1), collect(2)) # [1] [2]
```

**逐行说明**：

| 代码 | 作用 | 容易误解的点 |
| --- | --- | --- |
| `a == b` / `a is b` | 值相等 / 身份相同 | `==` 对 list 逐元素比较，与是否同一对象无关 |
| `alias = a` | 新名字指向同一 list | 不是复制；`alias is a` 为 `True` |
| `alias.append(4)` | 原地修改 | 只有这一个对象，通过 `a` 也能看到变化 |
| `m += [2]` | `list.__iadd__` 原地扩展并返回 `self` | `n is m` 仍为 `True`，`n` 一起变成 `[1, 2]` |
| `p = p + [2]` | `list.__add__` 造新 list 再绑定给 `p` | `q` 仍指向旧对象 |
| `copy.copy([inner])` | 新外层 + 共享内层 | `inner` 变化会同时反映到 `shallow` |
| `copy.deepcopy([inner])` | 递归复制，内层也是新对象 | `inner` 变化不影响 `deep` |
| `acc=None` 哨兵 | `None` 是不可变单例，天然安全 | 写 `acc=[]` 会跨调用累积（见 4.5） |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/01-基础与语法/01-Python数据模型与对象语义.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Python 数据模型与对象语义：最小可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/01-基础与语法/01-Python数据模型与对象语义.md)
