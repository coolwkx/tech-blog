---
article_id: kp-2bff3004ce6467f4
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-c0a892e8e152
learning_sourceId: c0a892e8e152
learning_order: 2
learning_objective: 理解并验证：dtype 常用类型
---

# dtype 常用类型

> **学习目标**：能够解释「dtype 常用类型」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 基础（列表、元组、字典、lambda、`import`）；了解"矩阵"的基本概念即可，无需线性代数基础。
>
> **所属主题**：-NumPy数值计算 · 核心概念

## 本次只学这一点

| 类型 | 描述 | 简写 |
| --- | --- | --- |
| `np.bool_` | 布尔，1 字节 | `'b'` |
| `np.int8` | −128 ~ 127 | `'i1'` |
| `np.int16` | −32768 ~ 32767 | `'i2'` |
| `np.int32` | −2³¹ ~ 2³¹−1 | `'i4'` |
| `np.int64` | −2⁶³ ~ 2⁶³−1（**整数默认**） | `'i8'` |
| `np.uint8` | 无符号，0 ~ 255 | `'u1'` |
| `np.float16` | 半精度：符号 1 + 指数 5 + 尾数 10 | `'f2'` |
| `np.float32` | 单精度：符号 1 + 指数 8 + 尾数 23 | `'f4'` |
| `np.float64` | 双精度：符号 1 + 指数 11 + 尾数 52（**小数默认**） | `'f8'` |
| `np.complex64/128` | 复数，两个 32/64 位浮点表示实部虚部 | `'c8'/'c16'` |
| `np.object_` | 任意 Python 对象 | `'O'` |
| `np.bytes_` / `np.str_` | 定长字节串 / Unicode 串 | `'S'` / `'U'` |

> 历史上还有 `np.string_` 与 `np.unicode_`，它们**已被弃用并在 NumPy 2.x 中移除**。新代码请直接写 `np.bytes_`、`np.str_`，或用 `dtype='S12'`、`dtype='U12'`。区别：`S`（bytes）只支持 ASCII，`U`（str）支持 Unicode。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「dtype 常用类型」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)
