---
article_id: kp-734da537b0318f15
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-035144ef44a8
learning_sourceId: 035144ef44a8
learning_order: 0
learning_objective: 理解并验证：模块的三种来源
---

# 模块的三种来源

> **学习目标**：能够解释「模块的三种来源」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数与全局变量（02 篇）、类与对象（03 篇）、`try/except ImportError`（04 篇）。
>
> **所属主题**：模块与包管理 · 核心概念

## 本次只学这一点

| 来源 | 说明 | 例子 |
| --- | --- | --- |
| 内置模块 built-in | 编译进解释器，随 Python 一起发布 | `sys`、`time`、`math`、`itertools` |
| 标准库 standard library | 随 Python 安装的一大批 `.py`/扩展模块 | `os`、`json`、`re`、`socket`、`pathlib` |
| 第三方包 third-party | 用 `pip` 从 PyPI 安装到 `site-packages` | `numpy`、`pandas`、`requests` |
| 自定义模块 | 你自己写的 `.py` 文件 | `A_module.py`、`student.py` |

**一个 `.py` 文件就是一个模块**；**一个包含 `__init__.py` 的目录就是一个包**。模块和包都是"命名空间容器"，用来把相关的函数、类、变量组织在一起。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/05-模块与包管理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「模块的三种来源」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/05-模块与包管理.md)
