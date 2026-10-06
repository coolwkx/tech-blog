---
article_id: kp-25d4c9d63fa87690
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-25d313dff349
learning_sourceId: 25d313dff349
learning_order: 6
learning_objective: 理解并验证：推导式 vs map / filter
---

# 推导式 vs map / filter

> **学习目标**：能够解释「推导式 vs map / filter」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：序列与字典（01 篇）、函数作为参数与 lambda（02 篇）、`yield` 生成器（06 篇）。
>
> **所属主题**：迭代器与内置函数 · 核心概念

## 本次只学这一点

| 写法 | 可读性 | 性能 | 惰性 |
| --- | --- | --- | --- |
| `[x*2 for x in xs if x > 2]` | ⭐ 高 | 快 | ❌ 立即生成列表 |
| `list(map(lambda x: x*2, filter(lambda x: x > 2, xs)))` | 低 | 稍慢（lambda 调用开销） | ❌（被 `list` 消费） |
| `(x*2 for x in xs if x > 2)` | 高 | 快 | ✅ 生成器表达式 |

实测两种写法结果完全一致：`[6, 8, 10]`。

**结论**：功能能用推导式表达的，优先用推导式（更 Pythonic、更快）；`map` / `filter` 适合"已经有一个现成的具名函数"的场景，例如 `map(str.strip(), lines)`、`filter(None, xs)`（过滤掉所有假值）。**不要在 `map` 里塞 `lambda` 去做推导式能干的事。**

| 推导式类型 | 语法 | 结果类型 |
| --- | --- | --- |
| 列表推导 | `[f(x) for x in xs if cond]` | `list` |
| 集合推导 | `{f(x) for x in xs}` | `set`（自动去重） |
| 字典推导 | `{k: v for k, v in pairs}` | `dict` |
| 生成器表达式 | `(f(x) for x in xs)` | `generator`（惰性，**不是元组**） |

> 注意：**没有"元组推导式"**。`(i for i in range(5))` 是生成器表达式，`type` 是 `<class 'generator'>`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/07-迭代器与内置函数.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「推导式 vs map / filter」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/07-迭代器与内置函数.md)
