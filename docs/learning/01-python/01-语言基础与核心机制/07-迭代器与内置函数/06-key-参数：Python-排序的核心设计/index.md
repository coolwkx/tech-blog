---
article_id: kp-25966153126c6ab1
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-25d313dff349
learning_sourceId: 25d313dff349
learning_order: 5
learning_objective: 理解并验证：key 参数：Python 排序的核心设计
---

# key 参数：Python 排序的核心设计

> **学习目标**：能够解释「key 参数：Python 排序的核心设计」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：序列与字典（01 篇）、函数作为参数与 lambda（02 篇）、`yield` 生成器（06 篇）。
>
> **所属主题**：迭代器与内置函数 · 核心概念

## 本次只学这一点

`sorted` / `list.sort()` / `min` / `max` / `groupby` 都接受 `key`：它对每个元素**调用一次**，用返回值参与比较，最后返回原元素。

| 需求 | 写法 |
| --- | --- |
| 按绝对值 | `sorted(xs, key=abs)` |
| 按长度 | `sorted(words, key=len)` |
| 按字典字段 | `sorted(rows, key=lambda r: r["score"])` |
| 按多个字段 | `sorted(rows, key=lambda r: (r["dept"], -r["score"]))` |
| 用 `operator` 更快更清晰 | `sorted(rows, key=itemgetter("dept", "score"))` |
| 按属性 | `sorted(objs, key=attrgetter("age", "name"))` |

**多级排序技巧**：Python 的 `key` 只能返回一个值，所以把多个排序依据**打包成元组**；元组按元素依次比较，因此"先按 A 升序、再按 B 降序"要写成 `(A, -B)`（数值才能取负；字符串降序需要多次稳定排序或自定义包装类）。

**稳定排序的含义**：`sorted` 是稳定排序 —— 键相同的元素保持原有相对顺序。实测 `sorted` 结果里 `王凯旋`（90 分）排在 `刘浩存`（90 分）之前，与它们在原列表中的顺序一致。这个性质让"多轮排序"成为可行方案：先按次要键排一次，再按主要键排一次，最终结果就是多级排序。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/07-迭代器与内置函数.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「key 参数：Python 排序的核心设计」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/07-迭代器与内置函数.md)
