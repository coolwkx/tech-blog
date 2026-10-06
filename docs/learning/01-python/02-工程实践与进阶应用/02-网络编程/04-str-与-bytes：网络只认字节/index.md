---
article_id: kp-c804f1b89d1e125b
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-a921e5aac5e4
learning_sourceId: a921e5aac5e4
learning_order: 3
learning_objective: 理解并验证：str 与 bytes：网络只认字节
---

# str 与 bytes：网络只认字节

> **学习目标**：能够解释「str 与 bytes：网络只认字节」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数与异常（02、04 篇）、`with` 与文件读写（04 篇）、多线程（08 篇，用于多客户端）。
>
> **所属主题**：网络编程 · 核心概念

## 本次只学这一点

网络上传输的一切都是 `bytes`。

| 方向 | 方法 | 示例 |
| --- | --- | --- |
| `str` → `bytes` | `s.encode("utf-8")` | `"你好".encode` → `b'\xe4\xbd\xa0\xe5\xa5\xbd'` |
| `bytes` → `str` | `b.decode("utf-8")` | `b'\xe4\xbd\xa0\xe5\xa5\xbd'.decode` → `"你好"` |
| 字面量 | `b"hello"` | `b` 前缀表示 bytes |

**编码必须两端一致**，推荐统一 `utf-8`。一边用 `gbk` 一边用 `utf-8` 就会 `UnicodeDecodeError` 或乱码。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/04-并发与网络/09-网络编程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「str 与 bytes：网络只认字节」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/04-并发与网络/09-网络编程.md)
