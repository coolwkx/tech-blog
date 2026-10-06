---
article_id: kp-e1f23a91e1560041
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-2996977d7379
learning_sourceId: 2996977d7379
learning_order: 9
learning_objective: 理解并验证：可变性、传参与默认参数
---

# 可变性、传参与默认参数

> **学习目标**：能够解释「可变性、传参与默认参数」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：基础语法（函数、类、列表/字典）；知道「引用」与「值」的区别会更顺。涉及 CPython 实现的地方都有标注，不需要 C 语言基础。
>
> **所属主题**：Python 数据模型与对象语义 · 深入机制

## 本次只学这一点

```python
def mutate(items): items.append("new") # 原地修改：调用者可见
def rebind(items): items = items + ["new"] # 重新绑定本地名：调用者不可见

data = [1]
mutate(data)
rebind(data)
print(data) # [1, 'new'] —— rebind 没生效

t = ([1], 2)
try: t[0] += [2] # 先 __iadd__ 成功，再 __setitem__ 失败
except TypeError as exc: print(type(exc).__name__, exc)
print(t) # ([1, 2], 2) —— 异常抛了，数据已经改了

def bad(value, acc=[]): # [] 在 def 执行时创建一次，存进 __defaults__
 acc.append(value); return acc

def good(value, acc=None):
 acc = [] if acc is None else acc
 acc.append(value); return acc

print(bad(1), bad(2), bad.__defaults__) # [1, 2] [1, 2] ([1, 2],) —— 共享同一个 list
print(good(1), good(2)) # [1] [2]
```

`t[0] += [2]` 是「半成功」的经典形态：展开为「取 `t[0]` → 原地 `extend` → 写回 `t[0]`」，第三步失败但第二步的副作用已发生。默认值是函数对象的属性（`__defaults__` / `__kwdefaults__`），随函数对象长生不死；只有不可变默认值（`None`、数字、字符串、元组、`frozenset`）才天然安全，`def f(x=time.time)` 同理只在定义时求值一次。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/01-基础与语法/01-Python数据模型与对象语义.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「可变性、传参与默认参数」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/01-基础与语法/01-Python数据模型与对象语义.md)
