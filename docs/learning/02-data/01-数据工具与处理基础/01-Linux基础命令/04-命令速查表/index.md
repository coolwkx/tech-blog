---
article_id: kp-b2f87d557ea61f55
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-94cd3f2167c7
learning_sourceId: 94cd3f2167c7
learning_order: 3
learning_objective: 理解并验证：命令速查表
---

# 命令速查表

> **学习目标**：能够解释「命令速查表」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：无需编程基础；了解 Windows 的盘符、文件夹、快捷方式概念即可类比。
>
> **所属主题**：-Linux基础命令 · 核心概念

## 本次只学这一点

| 命令 | 作用 | 常用选项 / 写法 |
| --- | --- | --- |
| `ls` | list，列出目录内容 | `-a` 显示隐藏文件；`-l` long 长格式；`-h` human 人性化大小；可合并为 `ls -alh`；`ll` 等价 `ls -l` |
| `pwd` | print work directory，打印当前所在目录 | 无参数 |
| `cd` | change directory，切换目录 | `cd /`、`cd ~`、`cd -` |
| `mkdir` | make directory，创建目录 | `-p` 递归创建多级目录，如 `mkdir -p aa/bb/cc` |
| `touch` | 创建空文件（或更新时间戳） | `touch 1.txt` |
| `cat` | 一次性输出文件全部内容 | 文件大时会刷屏 |
| `more` | 分页查看文件 | `b` 上一页、`d`/空格 下一页、回车 下一行、`q` 退出 |
| `cp` | copy，复制 | `-r` 递归复制目录（复制文件夹必须加） |
| `mv` | move，移动 / 重命名 | `mv 源 目标`，同目录下即为改名 |
| `rm` | remove，删除 | `-r` 递归、`-f` 强制不提示；**没有回收站** |
| `which` | 查看命令的可执行文件在哪 | `which python` |
| `find` | 按名字或大小查找文件 | `find / -name '*.txt'`、`find / -size +10M` |
| `grep` | 按关键字过滤行 | `-n` 显示行号，如 `grep -n python 1.txt` |
| `\|` | 管道：把前一个命令的输出当作后一个命令的输入 | `cat 1.txt \| grep python \| grep pandas` |
| `echo` | 输出内容到终端，类似 print | `echo hello` |
| `` ` `` | 反引号：把命令的执行结果嵌入到另一条命令里 | `echo \`pwd\`` 输出的是路径而非 "pwd" |
| `>` `>>` | 重定向：`>` 覆盖写，`>>` 追加写 | `ls / >> 1.txt` |
| `tail` | 查看文件末尾，常用于看日志 | `-n` 指定行数（默认 10）、`-f` 持续追踪；`tail -10f python.log` |
| `vi` / `vim` | 文本编辑器 | 三者模式 + `:wq` / `:q!` |
| `--help` | 查看命令帮助 | `ls --help` |
| `man` | 查看命令手册 | `man ls`、`man ls >> ls.txt` |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/01-Linux与SQL/01-Linux基础命令.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「命令速查表」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/01-Linux与SQL/01-Linux基础命令.md)
