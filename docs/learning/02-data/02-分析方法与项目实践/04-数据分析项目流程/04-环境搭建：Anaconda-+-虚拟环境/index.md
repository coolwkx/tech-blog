---
article_id: kp-3608f6f10c057746
learning_kind: article
learning_category: 02-data
learning_direction: practice
learning_topic: topic-91025ff85275
learning_sourceId: 91025ff85275
learning_order: 3
learning_objective: 理解并验证：环境搭建：Anaconda + 虚拟环境
---

# 环境搭建：Anaconda + 虚拟环境

> **学习目标**：能够解释「环境搭建：Anaconda + 虚拟环境」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：本目录 [01-Linux基础命令](../../../../../02-data/01-Linux与SQL/01-Linux基础命令.md) ～ [10-RFM用户价值分析实战](../../../../../02-data/04-分析实战/10-RFM用户价值分析实战.md) 的全部内容；会安装软件、使用命令行与 Jupyter。
>
> **所属主题**：-数据分析项目流程 · 核心概念

## 本次只学这一点

Anaconda 是最流行的数据分析平台（全球两千多万人使用），附带大量常用数据科学包，基于 `conda`（包管理器 + 环境管理器）发展而来，帮助安装管理数据分析相关包并内置虚拟环境工具；Windows/macOS/Linux 都可用，**与本机已有 Python 不冲突**。

| 操作 | 命令 |
| --- | --- |
| 安装包 | `conda install 包名` / `pip install 包名` |
| 用国内镜像加速 | `pip install 包名 -i https://mirrors.aliyun.com/pypi/simple/` |
| 创建虚拟环境 | `conda create -n 环境名 python=3.11` |
| 进入 / 退出 | `conda activate 环境名` / `conda deactivate` |
| 查看 / 删除 | `conda env list` / `conda remove -n 环境名 --all` |
| 启动 Jupyter | `jupyter lab` / `jupyter notebook`（建议**以管理员身份**打开命令行） |

常用 pip 镜像：阿里云 `https://mirrors.aliyun.com/pypi/simple/`、豆瓣 `https://pypi.douban.com/simple/`、清华大学 `https://pypi.tuna.tsinghua.edu.cn/simple/`、中科大 `http://pypi.mirrors.ustc.edu.cn/simple/`。

**虚拟环境的价值**：每个项目一个独立环境，避免"项目 A 依赖 Pandas 1.x、项目 B 依赖 Pandas 2.x"的冲突，环境可复现、可整体删除。这与 Linux 里"每个服务独立账号、独立目录"的最小隔离思想一致。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/04-分析实战/11-数据分析项目流程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「环境搭建：Anaconda + 虚拟环境」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/04-分析实战/11-数据分析项目流程.md)
