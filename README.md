# 📚 技术复习笔记博客

[![Notes CI](https://github.com/coolwkx/tech-blog/actions/workflows/notes-ci.yml/badge.svg)](https://github.com/coolwkx/tech-blog/actions/workflows/notes-ci.yml)
[![Docs](https://img.shields.io/badge/docs-online-brightgreen.svg)](https://coolwkx.github.io/tech-blog/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 一站式技术复习知识库：**Python → 数据处理与统计 → 机器学习 → 深度学习 → NLP → 大语言模型 → AI Agent → 项目实战**
>
> 每个知识点按「核心概念 → 可运行示例 → 常见坑 → 面试问答 → 自测题」组织，目标是**半小时内能重新捡起来**。

## 🎯 这个仓库是什么

| 问题 | 回答 |
| --- | --- |
| 定位 | 个人复习笔记库（优先保证准确性，暂不追求面面俱到） |
| 内容来源 | 课程学习 + 项目实践 + 论文与官方文档，全部经重新提炼、纠错与校正 |
| 组织方式 | 9 个领域，每领域分若干系列，每系列若干篇单一知识点笔记 |
| 质量标准 | 每篇必有可运行示例、常见坑表、自测题；断链与代码语法由 CI 强制检查 |
| 不收录 | 大段复制粘贴的原文、无出处的结论、模型权重与数据集等大文件 |

## 🚀 快速开始

```bash
git clone https://github.com/coolwkx/tech-blog.git
cd tech-blog

# 方式一：直接读 Markdown（无需任何依赖）
# docs/README.md 是总入口

# 方式二：本地起站点（带全文搜索与侧边栏）
pip install mkdocs-material
mkdocs serve # http://127.0.0.1:8000

# 方式三：在线看
# https://coolwkx.github.io/tech-blog/
```

## 🗂️ 目录结构

```text
tech-blog/
├─ README.md # 你正在看的这个文件
├─ mkdocs.yml # 站点配置（nav 由脚本生成）
├─ docs/ # 全部笔记（mkdocs 的 docs_dir）
│ ├─ README.md # 博客首页 / 总索引
│ ├─ roadmap.md # 跨领域学习路线
│ ├─ 01-python/ # 🐍 Python
│ ├─ 02-data/ # 📦 数据处理与统计
│ ├─ 03-ml/ # 📊 机器学习
│ ├─ 04-dl/ # 🧠 深度学习
│ ├─ 05-nlp/ # 📝 自然语言处理
│ ├─ 06-llm/ # 🤖 大语言模型
│ ├─ 07-agent/ # 🕹️ AI Agent
│ └─ 08-project/ # 🚀 项目实战
├─ templates/ # 笔记 / 章节 / 论文 / 面试题模板
├─ tools/
│ ├─ lint_notes.py # 内容质检（断链 / 代码语法 / 结构 / nav）
│ └─ build_index.py # 重新生成分区索引与 mkdocs nav
├─ resources/ # 原始索引（**只放清单，不放文件**）
└─ .github/workflows/ # CI：质检 → 构建 → 发布 Pages
```

**命名约定**：分区 `NN-英文短名`；章节 `NN-英文短名`；笔记 `NN-中文标题.md`；速查区固定为 `90-cheatsheet`。
一篇笔记只讲一个知识点，超过 400 行就拆。

## ✅ 质量保证

CI 在每次 push 时执行三道检查：

| 检查 | 工具 | 规则 |
| --- | --- | --- |
| 内部链接 | `tools/lint_notes.py` | 不允许断链（兄弟仓库引用除外） |
| 代码块 | `tools/lint_notes.py` | 所有 ```python 块必须能通过 `ast.parse` |
| 文章结构 | `tools/lint_notes.py` | 必须有「一句话总结 / 前置知识 / 常见坑 / 自测题 / 延伸阅读」 |
| 站点构建 | `mkdocs build` | 配置与 nav 必须有效 |

本地自查：

```bash
python tools/lint_notes.py # 质检
python tools/build_index.py # 改过目录或 nav 后刷新索引
```

## ✍️ 写作规范

- 中文为主，**英文术语保留原文**（`gradient checkpointing` 不硬译成「梯度检查点法」）。
- 每篇必须包含：一句话总结、前置知识、学完能做到、核心概念表、可运行示例、常见坑表、面试问答、自测题、延伸阅读。
- 引用外部结论必须给出链接；数字要给量级与出处。
- 示例代码必须亲自跑过（CI 会做语法检查，跑通与否靠自己负责）。
- 不使用图片作为主要信息载体（GitHub 与站点上易失效），必要图示用文本图或表格。

## 📄 License

[MIT](LICENSE) © 2026
