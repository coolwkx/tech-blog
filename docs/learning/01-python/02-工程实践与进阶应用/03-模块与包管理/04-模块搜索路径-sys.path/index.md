---
article_id: kp-a6f2e7ff7995de61
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-035144ef44a8
learning_sourceId: 035144ef44a8
learning_order: 3
learning_objective: 理解并验证：模块搜索路径 sys.path
---

# 模块搜索路径 sys.path

> **学习目标**：能够解释「模块搜索路径 sys.path」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数与全局变量（02 篇）、类与对象（03 篇）、`try/except ImportError`（04 篇）。
>
> **所属主题**：模块与包管理 · 核心概念

## 本次只学这一点

```python
import sys
print(sys.path)
# ['<入口脚本目录>', ... 标准库路径 ..., ... site-packages ...]
```
| 查找顺序 | 位置 |
| --- | --- |
| 1 | 入口脚本所在目录 / `-m` 时的当前工作目录 |
| 2 | 环境变量 `PYTHONPATH` 中的目录 |
| 3 | 标准库目录 |
| 4 | `site-packages`（pip 安装的第三方包） |
| 5 | `.pth` 文件追加的路径 |

临时追加路径：`sys.path.append("/some/dir")`（**注意顺序**：`append` 放最后，`insert(0, ...)` 会**遮蔽**同名官方模块，很危险）。规范做法是把项目根目录作为入口运行，或用 `pip install -e .` 做可编辑安装。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/05-模块与包管理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「模块搜索路径 sys.path」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/05-模块与包管理.md)
