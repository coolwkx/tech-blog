---
article_id: kp-2b00d8598f86c79b
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-c695752cdddc
learning_sourceId: c695752cdddc
learning_order: 8
learning_objective: 理解并验证：引用、浅拷贝与"别名"
---

# 引用、浅拷贝与"别名"

> **学习目标**：能够解释「引用、浅拷贝与"别名"」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：会安装并运行 Python（3.8+）；知道变量、`print`、`input` 的基本用法；了解 `int / float / str / bool` 四种标量类型。
>
> **所属主题**：基础语法与数据类型 · 核心概念

## 本次只学这一点

```python
a = [1, 2, 3]
b = a # 别名：两个名字，一个对象
b.append(4)
print(a) # [1, 2, 3, 4] ← 很多 bug 的源头

c = a.copy # 浅拷贝：新列表，元素还是原引用
c.append(5)
print(a) # 不受影响
```
- `list.copy` / `dict.copy` / `set.copy` 都是**浅拷贝**；
- 嵌套结构要真正隔离必须用 `copy.deepcopy`（第 03 篇详述）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/01-基础与语法/01-基础语法与数据类型.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「引用、浅拷贝与"别名"」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/01-基础与语法/01-基础语法与数据类型.md)
