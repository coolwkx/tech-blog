---
article_id: kp-d06e40191261f0e3
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-6f07590fb31d
learning_sourceId: 6f07590fb31d
learning_order: 3
learning_objective: 理解并验证：文档解析：多格式 + 分层切分
---

# 文档解析：多格式 + 分层切分

> **学习目标**：能够解释「文档解析：多格式 + 分层切分」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：LangChain 六大组件（见《08-LangChain基础》）、Milvus 与向量检索（见《07-向量数据库与Milvus》）、embedding 与相似度。
>
> **所属主题**：-RAG系统构建 · 关键机制

## 本次只学这一点

**多格式支持**：`document_processor.py` 用「扩展名 → 加载器」的字典做分发，扩展只需加一行。

| 扩展名 | 加载器 | 说明 |
|---|---|---|
| `.txt` | `TextLoader` | 需指定 `encoding="utf-8"` |
| `.pdf` | `OCRPDFLoader` | 走 OCR，能识别扫描件 |
| `.docx` | `OCRDOCLoader` | Word 文档 |
| `.ppt` / `.pptx` | `OCRPPTLoader` | 演示文稿 |
| `.jpg` / `.png` | `OCRIMGLoader` | 图片（**图片或表格采用 PaddleOCR 实现识别**） |
| `.md` | `UnstructuredMarkdownLoader` | Markdown |

**为什么需要 OCR 加载器**：、扫描 PDF、图表里的文字**没有文本层**，
普通 `PyPDFLoader` 抽出来是空的；OCR 才能把它们变成可检索的文本。

**元数据注入**（每个 `Document` 都带上）：

| 元数据 | 来源 | 用途 |
|---|---|---|
| `source` | 目录名去掉 `_data`（如 `ai_data` → `ai`） | **学科过滤**（对应 `valid_sources`） |
| `file_path` | 文件完整路径 | 溯源、按格式选切分器 |
| `timestamp` | 处理时刻的 ISO 时间 | 时效管理 |

**分层切分（父块 / 子块）**是整套方案的核心：

| 层级 | 大小 | 切分器 | 作用 |
|---|---|---|---|
| 父块 | `parent_chunk_size=1200` | `ChineseRecursiveTextSplitter` 或 `MarkdownTextSplitter` | 提供完整上下文，交给 LLM |
| 子块 | `child_chunk_size=300` | 同上（更小粒度） | **建立向量索引**、参与检索 |

流程：文档 → 父块（`parent_id = doc_{i}_parent_{j}`，并把父块原文写进 `parent_content` 元数据）
→ 每个父块再切成子块（`id = {parent_id}_child_{k}`，同时带上 `parent_id` 与 `parent_content`）。

**为什么用「子块检索 + 父块返回」**：子块小，向量表示聚焦、检索精度高；父块大，上下文完整、生成质量好。
检索命中的是子块，但送给 LLM 的是它所属的**父块原文**，一举两得。
**Markdown 文件用专用切分器**：按标题层级切，天然贴合文档结构。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/07-检索增强RAG/09-RAG系统构建.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「文档解析：多格式 + 分层切分」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/07-检索增强RAG/09-RAG系统构建.md)
