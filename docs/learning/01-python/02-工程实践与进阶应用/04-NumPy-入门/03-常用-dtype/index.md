---
article_id: kp-bbb2802fe1405abb
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-a5477d7405c8
learning_sourceId: a5477d7405c8
learning_order: 2
learning_objective: 理解并验证：常用 dtype
---

# 常用 dtype

> **学习目标**：能够解释「常用 dtype」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：列表与嵌套结构（01 篇）、列表推导式（07 篇）、函数与类（02、03 篇）。
>
> **所属主题**：NumPy 入门 · 核心概念

## 本次只学这一点

| 类型 | 描述 | 简写 |
| --- | --- | --- |
| `np.bool_` | 布尔 | `'?'` |
| `np.int8 / int16 / int32 / int64` | 有符号整数（1/2/4/8 字节） | `'i1' / 'i2' / 'i4' / 'i8'` |
| `np.uint8 / uint16 / uint32 / uint64` | 无符号整数 | `'u1' / 'u2' / 'u4' / 'u8'` |
| `np.float16 / float32 / float64` | 半/单/双精度浮点 | `'f2' / 'f4' / 'f8'` |
| `np.complex64 / complex128` | 复数 | `'c8' / 'c16'` |
| `np.str_`（原 `np.unicode_`） | Unicode 字符串 | `'U'` |
| `np.bytes_`（原 `np.string_`） | 字节串（只支持 ASCII） | `'S'` |
| `np.object_` | 任意 Python 对象 | `'O'` |

**默认规则**：整数不指定就是 `int64`，小数不指定就是 `float64`（Windows 上整数曾默认 `int32`）。

> ⚠️ 用 `np.string_` / `np.unicode_`：这两个别名在 NumPy 2.0 已**移除**，现在应写 `np.bytes_` / `np.str_`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/11-NumPy入门.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「常用 dtype」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/11-NumPy入门.md)
