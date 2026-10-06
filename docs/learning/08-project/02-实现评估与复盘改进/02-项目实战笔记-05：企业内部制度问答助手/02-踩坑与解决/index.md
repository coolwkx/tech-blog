---
article_id: kp-26913396c491c3d3
learning_kind: article
learning_category: 08-project
learning_direction: practice
learning_topic: topic-bbd88f00e6f8
learning_sourceId: bbd88f00e6f8
learning_order: 9
learning_objective: 理解并验证：踩坑与解决
---

# 踩坑与解决

> **学习目标**：能够解释「踩坑与解决」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 基础、向量检索的基本概念（Embedding / 相似度 / Top-K）、`pip` 环境管理、Streamlit 的最简用法。
>
> **所属主题**：项目实战笔记 05：企业内部制度问答助手 · 踩坑与解决

## 本次只学这一点

| 现象 | 根因 | 解决 | 如何预防 |
| --- | --- | --- | --- |
| `FAISS.load_local` 报错，要求 `allow_dangerous_deserialization` | 新版 LangChain 默认拒绝加载 pickle | 传 `allow_dangerous_deserialization=True` | **只对自己生成的索引开这个开关**；外部来源的索引绝不能开，pickle 反序列化可执行任意代码 |
| 建库和查询用的 embedding 模型不一致，检索结果乱 | 两次代码里模型名不同（或默认值变了） | 建库与查询严格使用同一个模型名与版本 | 把 embedding 模型名写进配置文件，而不是在两处硬编码 |
| 问"年假有几天"，答案说"未提及" | `k=1`，只召回了一个块，而答案在另一个块里 | 调大 `k`（本项目用 2）；或优化切分让相关信息落进同一块 | 调 RAG 效果时，**先打印检索到的 `docs` 内容再下结论**——很多"模型不行"其实是"检索没召回到" |
| 检索到的块里混着无关字段 | `chunk_size` 太大，把"报销制度"和"考勤管理"混在一块 | 按内容形态调小 `chunk_size` | 定 chunk_size 前先肉眼看 10 条切分结果 |
| 答案里出现了知识库没有的数字 | Prompt 没有约束"不得编造" | 模板里加"不允许在答案中添加编造成分" | RAG 的 Prompt 必须包含**反幻觉约束 + 无答案时的兜底话术**两项 |
| 扫描版 PDF 建库后 `len(data)` 为 1、检索永远为空 | PyMuPDF 只能提取文字层，扫描件是图片 | 换成 OCR Loader（如 `OCRPDFLoader`，需 PaddleOCR） | 建库前先抽一页打印，确认拿到的是文字不是空字符串 |
| 每次提问都重新执行整段脚本，界面闪一下 | Streamlit 的默认执行模型：任何交互都重跑整个脚本 | 用 `st.session_state` 保存状态；把重资源（模型、索引）用 `@st.cache_resource` 缓存 | 记住 Streamlit 是"重跑式"而非"事件式"，所有状态必须显式放 `session_state` |
| 多用户同时访问，聊天记录互相串 | `chat_history` 是模块级全局变量 | 改放进 `st.session_state` | Streamlit 里任何"每会话独立"的状态都必须放 `session_state` |
| 界面上的"流式"其实等很久才出字 | 先拿完整答案再逐词渲染，是假流式 | 用 `chain.stream` / `llm.stream` + `st.write_stream` | 区分"视觉流式"和"真流式"，后者才是降低首字延迟的手段 |
| 首次提问特别慢（十几秒） | 模型冷启动 + 首次加载 FAISS 索引 + 首次 embedding | 服务启动时预热：跑一次空查询 | 任何"第一次特别慢"的服务都要做预热 |
| `ConversationalRetrievalChain` 已弃用警告 | LangChain 新版改用 `create_history_aware_retriever` + `create_retrieval_chain` | 按官方迁移文档改写 | LangChain 是快速演进库，**锁定版本号**（`requirements.txt` 精确到 patch 版本）比追新更重要 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/01-问答与RAG系统/05-项目-企业内部制度问答助手.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「踩坑与解决」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/01-问答与RAG系统/05-项目-企业内部制度问答助手.md)
