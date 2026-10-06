---
article_id: kp-a67ff2acf462df79
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-d512e4a67eb2
learning_sourceId: d512e4a67eb2
learning_order: 2
learning_objective: 理解并验证：软链接 vs 硬链接
---

# 软链接 vs 硬链接

> **学习目标**：能够解释「软链接 vs 硬链接」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：建议先掌握 [01-Linux基础命令](../../../../../02-data/01-Linux与SQL/01-Linux基础命令.md) 中的 `ls/cd/mkdir/cp/mv/rm/find/grep/管道/重定向/vi`。
>
> **所属主题**：-Linux实用操作 · 核心概念

## 本次只学这一点

| 维度 | 软链接（symbolic link） | 硬链接（hard link） |
| --- | --- | --- |
| 创建命令 | `ln -s 源 链接名` | `ln 源 链接名` |
| 类比 | Windows/Mac 的快捷方式 | 同一份数据的第二个名字 |
| `ls -l` 显示 | `lrwxrwxrwx ... ip -> /etc/.../ifcfg-ens33` | 与普通文件无异 |
| 源删除后 | 链接失效（悬空链接） | 数据仍在，另一个名字照常可读 |
| 跨分区 | 可以 | 不可以（inode 不能跨文件系统） |
| 典型用途 | 把深层配置/目录挂到好记的路径下 | 同一文件多入口的动态备份 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/01-Linux与SQL/02-Linux实用操作.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「软链接 vs 硬链接」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/01-Linux与SQL/02-Linux实用操作.md)
