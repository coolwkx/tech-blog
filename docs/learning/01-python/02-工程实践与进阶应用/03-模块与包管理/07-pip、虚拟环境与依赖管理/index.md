---
article_id: kp-45136aa79457b808
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-035144ef44a8
learning_sourceId: 035144ef44a8
learning_order: 6
learning_objective: 理解并验证：pip、虚拟环境与依赖管理
---

# pip、虚拟环境与依赖管理

> **学习目标**：能够解释「pip、虚拟环境与依赖管理」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数与全局变量（02 篇）、类与对象（03 篇）、`try/except ImportError`（04 篇）。
>
> **所属主题**：模块与包管理 · 核心概念

## 本次只学这一点

| 任务 | 命令 |
| --- | --- |
| 创建虚拟环境 | `python -m venv .venv` |
| 激活（Windows PowerShell） | `.\.venv\Scripts\Activate.ps1` |
| 激活（macOS/Linux） | `source .venv/bin/activate` |
| 安装 | `pip install numpy` / `pip install numpy==2.3.5` |
| 查看已装 | `pip list` / `pip show numpy` |
| 导出依赖 | `pip freeze > requirements.txt` |
| 按清单安装 | `pip install -r requirements.txt` |
| 卸载 | `pip uninstall numpy` |

**为什么必须用虚拟环境**：不同项目的依赖版本常常冲突（A 项目要 pandas 1.x，B 项目要 pandas 3.x），装在全局环境里只能有一个版本。虚拟环境为每个项目隔离一套 `site-packages`。

`requirements.txt` 建议写**直接依赖 + 版本约束**，而不是 `pip freeze` 出来的全量清单（那会把间接依赖也钉死，升级时很痛苦）：
```text
numpy>=2.0,<3.0
pandas>=2.2
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/05-模块与包管理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「pip、虚拟环境与依赖管理」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/05-模块与包管理.md)
