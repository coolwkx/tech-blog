---
article_id: kp-6abd0c07275514f0
learning_kind: article
learning_category: 08-project
learning_direction: practice
learning_topic: topic-bbd88f00e6f8
learning_sourceId: bbd88f00e6f8
learning_order: 5
learning_objective: 理解并验证：关键技术选型与理由
---

# 关键技术选型与理由

> **学习目标**：能够解释「关键技术选型与理由」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 基础、向量检索的基本概念（Embedding / 相似度 / Top-K）、`pip` 环境管理、Streamlit 的最简用法。
>
> **所属主题**：项目实战笔记 05：企业内部制度问答助手 · 关键技术选型与理由

## 本次只学这一点

| 方案 | 优点 | 代价 | 本项目为何选它 |
| --- | --- | --- | --- |
| **LangChain** 统一编排 | Loader/Splitter/Embeddings/VectorStore/Chain 全部有统一接口，换组件只改一行 | 抽象层多，出错时堆栈深、难调试；版本间 API 频繁变动 | 本项目要展示"标准 RAG 流水线"，LangChain 就是这套标准的事实定义者 |
| **Ollama** 本地模型管理 | `ollama pull qwen2.5:7b` 一条命令，模型权重、量化、推理服务全托管 | 受本机显卡限制；7B 模型在 CPU 上很慢 | 离线私有化是企业内部制度问答的硬需求，数据不出内网 |
| **qwen2.5:7b** | 中文能力强；7B 参数量在 16G 显存上可跑 | 生成质量弱于云端大模型 | 中文行业问答，Qwen 系列的中文表现优于同规模 LLaMA 系 |
| **PyMuPDFLoader** | 速度快、对中文 PDF 的文本提取质量比 PyPDF2 好 | 需要装 `pymupdf`；扫描版 PDF 提不出文字（要 OCR） | 知识库主体是文字版 PDF 手册 |
| **FAISS（CPU 版）** | 纯本地库，`pip install faiss-cpu` 即用，零运维；检索极快 | 只支持向量检索，无标量过滤、无分布式、无持久化服务 | 单文档、单机、离线，FAISS 是性价比最高的选择 |
| **RecursiveCharacterTextSplitter** | 按 `\n\n → \n → 空格 → 字符` 递归尝试，尽量在语义边界断开 | 中文没有空格，50 字的块可能切断词 | 比 `CharacterTextSplitter` 更懂"什么位置适合断开" |
| `chunk_size=50, chunk_overlap=20` | 与这份短字段式 PDF 的"一条信息一行"结构匹配 | 块很小，单块信息量低，需要更高的 k | 员工手册是"键值对"式短文本，块大了会把无关字段混进来 |
| **Streamlit** | 零前端代码，`st.chat_input` + `st.chat_message` 直接出聊天界面 | 每次交互全脚本重跑；不适合复杂交互与生产部署 | 演示界面，50 行出成品，不值得上前后端分离 |
| `ConversationalRetrievalChain` | 内置 question condensation，多轮对话开箱可用 | 每次提问会多一次 LLM 调用（改写），延迟翻倍 | 省掉手写 Query 改写的工程量，工程性价比极高 |
| `allow_dangerous_deserialization=True` | 让 FAISS 本地索引能加载 | **反序列化不受信任的 pkl 可执行任意代码** | 索引是自己生成的所以接受；但必须知道这是个真实的安全开关 |

> **关于那个 `allow_dangerous_deserialization` 参数**：很多直接复制这行却不解释。FAISS 的 `save_local` 用 pickle 保存 docstore，`load_local` 默认拒绝加载 pickle（因为 pickle 反序列化可以执行任意代码）。传 `True` 表示"我信任这个文件"。**如果索引文件是从外部获取的（比如用户上传、网盘下载），这个参数绝不该开。** 面试里被问到"你代码里有没有安全隐患"，这就是一个能答出彩的点。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/01-问答与RAG系统/05-项目-企业内部制度问答助手.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「关键技术选型与理由」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/01-问答与RAG系统/05-项目-企业内部制度问答助手.md)
