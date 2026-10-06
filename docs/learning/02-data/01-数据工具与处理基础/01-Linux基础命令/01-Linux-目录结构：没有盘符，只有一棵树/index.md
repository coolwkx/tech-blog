---
article_id: kp-d3085a6e3a2bd28a
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-94cd3f2167c7
learning_sourceId: 94cd3f2167c7
learning_order: 0
learning_objective: 理解并验证：Linux 目录结构：没有盘符，只有一棵树
---

# Linux 目录结构：没有盘符，只有一棵树

> **学习目标**：能够解释「Linux 目录结构：没有盘符，只有一棵树」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：无需编程基础；了解 Windows 的盘符、文件夹、快捷方式概念即可类比。
>
> **所属主题**：-Linux基础命令 · 核心概念

## 本次只学这一点

Windows 是"森林结构"：有 C:、D: 等多个盘符，每棵树各自独立。
Linux 是"单根结构"：**只有一个根目录 `/`**，所有设备、分区都挂在同一棵树上。

| 目录 | 存放内容 | 记忆点 |
| --- | --- | --- |
| `/bin` | 基础命令（cd、mv、cp、ls…） | binary，普通用户可用 |
| `/sbin` | 系统管理类命令（ifconfig、reboot…） | super/user binary，多为 root 使用 |
| `/etc` | 系统与软件的配置文件 | 改配置基本都在这里，如 `/etc/hosts`、`/etc/profile` |
| `/root` | root 账号的家目录 | 超管专属 |
| `/home` | 普通账号的家目录集合 | 每个普通用户是 `/home/用户名` 一个子目录 |
| `/usr` | 用户级程序与资源（`/usr/share/fonts` 等） | 类似 Windows 的 Program Files |
| `/tmp` | 临时文件 | 重启可能被清理 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/01-Linux与SQL/01-Linux基础命令.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Linux 目录结构：没有盘符，只有一棵树」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/01-Linux与SQL/01-Linux基础命令.md)
