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

# 方式二：预览与线上一致的学习界面
pip install -r requirements-site.txt
python tools/site.py preview # http://127.0.0.1:8000

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

## 技术学习空间

网站首页提供按知识体系浏览、完整文章阅读、全文搜索、深浅色主题、字号与行距调整、专注阅读、代码复制、公式和流程图，以及收藏、待复习、掌握标记、阅读位置和个人笔记。

学习记录保存在当前浏览器，可通过侧栏导出备份；不同设备、浏览器或网站域名之间不会自动同步。首页只加载目录和摘要，使用搜索时再加载正文索引。文章正文按需加载，公式与流程图资源由仓库内置。

所有笔记仍以 `docs/` 中的 Markdown 为内容源。GitHub Actions 会先构建 MkDocs，再从本次构建的文章生成学习界面，不依赖线上内容快照。原有文章地址继续可用。

```bash
pip install -r requirements-site.txt
python tools/site.py preview
```

打开 http://localhost:8000 查看学习界面。`mkdocs serve` 仍用于预览原始文档布局；`learning-ui/` 保存学习界面模板，`tools/build_learning_site.py` 生成目录、正文与延迟加载的搜索索引。`site/` 是生成产物，不提交到仓库。

## 按知识点复习与维护

Python 分为「语言基础与核心机制」和「工程实践与进阶应用」两个方向。其他领域同样分为两个学习方向，每个方向下按主题选择独立知识点。`docs/learning/<领域>/<方向>/<主题>/<知识点>/index.md` 是独立学习页面；原有章节仍保留为综合参考与完整案例。

每个知识点写明本次目标、前置知识与来源。拆分保留原文的概念、公式和示例；项目片段可能依赖原文环境，页面明确提供上下文入口。不要把所有示例都视为独立程序。

### 统一构建与预览

```bash
pip install -r requirements-site.txt
python tools/site.py build
python tools/site.py preview
```

本地预览和 CI 使用同一个构建入口，发布前检查页面编号、目录、正文、内部链接和分领域搜索索引的一致性。浏览器的学习记录可通过侧栏导出、导入；导入提供合并和替换，未知编号保留，格式错误不会覆盖已有记录。

### 新增或移动文章

- 新文章先运行 `python tools/register_articles.py`，生成一次性的 `article_id`。移动或改名时保留这个编号，不能按新路径重新生成。
- 独立知识点的 front matter 设置 `learning_kind: article`、`learning_category`、`learning_direction`、`learning_topic` 和 `learning_sourceId`；综合原文使用 `reference`。
- 更新 `learning-map.json` 的目录登记和 `mkdocs.yml` 的导航，保持主题、方向和来源明确。知识点不必因目录改名而改变编号。
- 修改原文时同步审阅对应知识点：独立页面是可编辑 Markdown，而非每次部署强行切割原文。
- 运行 `python tools/lint_notes.py`、`node tests/records.test.cjs` 和 `python tools/site.py build` 后提交。

搜索优先匹配标题与摘要，正文按领域加载；搜索框可以选择单一领域，避免每次下载全部索引。收藏、复习和笔记仍只保存在当前浏览器，跨设备需导出、导入备份。


### 缓存与地址兼容

浏览器会缓存学习界面和已打开的正文、索引与公式图表资源；未打开的内容不保证离线可用。新版本就绪时显示更新按钮，保存阅读位置后再更新，避免阅读中途强制刷新。缓存限额为 400 个资源，不存储 GitHub 凭据。

`learning-map.json` 中登记已发布路径。移动文章时保留 front matter 中的 `article_id`，更新目录登记与导航；构建会给原地址生成跳转，旧学习记录继续按同一编号匹配。
