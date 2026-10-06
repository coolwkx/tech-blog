---
article_id: kp-f3be754a7bd21274
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-c695752cdddc
learning_sourceId: c695752cdddc
learning_order: 4
learning_objective: 理解并验证：list 的增删改查
---

# list 的增删改查

> **学习目标**：能够解释「list 的增删改查」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：会安装并运行 Python（3.8+）；知道变量、`print`、`input` 的基本用法；了解 `int / float / str / bool` 四种标量类型。
>
> **所属主题**：基础语法与数据类型 · 核心概念

## 本次只学这一点

| 目的 | 方法 | 说明 |
| --- | --- | --- |
| 增（1 个） | `lst.append(x)` | **只能接一个参数**，追加到末尾 |
| 增（多个） | `lst.extend(iterable)` | 逐个追加，等价于 `lst += iterable` |
| 增（指定位置） | `lst.insert(i, x)` | 在索引 i 处插入，原元素后移 |
| 删（按下标） | `del lst[i]` / `lst.pop(i)` | `pop` 会返回被删元素 |
| 删（按值） | `lst.remove(v)` | 只删第一个匹配项；不存在则 `ValueError` |
| 删（清空） | `lst.clear()` | — |
| 查 | `lst.index(v)` / `v in lst` | `index` 找不到抛异常，`in` 返回布尔 |
| 改 | `lst[i] = x` / `lst[1:3] = [a, b]` | 切片赋值可以改变列表长度 |
| 排序 | `lst.sort(key=..., reverse=...)` | **原地**排序，返回 `None` |
| 排序（新表） | `sorted(lst)` | 返回新列表 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/01-基础与语法/01-基础语法与数据类型.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「list 的增删改查」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/01-基础与语法/01-基础语法与数据类型.md)
