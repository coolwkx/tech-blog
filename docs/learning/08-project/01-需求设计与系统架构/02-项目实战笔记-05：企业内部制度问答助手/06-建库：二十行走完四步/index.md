---
article_id: kp-beb78644fdb17f35
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-bbd88f00e6f8
learning_sourceId: bbd88f00e6f8
learning_order: 6
learning_objective: 理解并验证：建库：二十行走完四步
---

# 建库：二十行走完四步

> **学习目标**：能够解释「建库：二十行走完四步」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 基础、向量检索的基本概念（Embedding / 相似度 / Top-K）、`pip` 环境管理、Streamlit 的最简用法。
>
> **所属主题**：项目实战笔记 05：企业内部制度问答助手 · 核心实现

## 本次只学这一点

```text
# local_db.py
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

def get_vector:
 # 第一步：加载文档 → Document 对象列表
 loader = PyMuPDFLoader("员工手册.pdf")
 data = loader.load
 print(f"len(data):{len(data)}")

 # 第二步：切分文本
 text_splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=20)
 split_docs = text_splitter.split_documents(data)
 print("split_docs size:", len(split_docs))

 # 第三步：初始化嵌入模型（把文字变成向量）
 embeddings = OllamaEmbeddings(model="mxbai-embed-large")

 # 第四步：向量化并持久化到 FAISS
 db = FAISS.from_documents(split_docs, embeddings)
 db.save_local("./faiss/policy")

if __name__ == '__main__':
 get_vector
```

**四个步骤各自在做什么、出错时表现如何**：

| 步骤 | 出错时的典型表现 | 排查方向 |
| --- | --- | --- |
| `loader.load` | `len(data)` 是 1 或 0 | 扫描版 PDF 提不出文字，需要 OCR；检查文件路径 |
| `split_documents` | 块数过多/过少 | 打印几个 `split_docs[i].page_content` 肉眼看切得合不合理 |
| `OllamaEmbeddings` | 连接被拒 / 模型不存在 | `ollama serve` 是否在跑、`ollama list` 里有没有该模型 |
| `FAISS.from_documents` | 维度不一致 | 建库和查询必须用**同一个** embedding 模型 |

**为什么 `chunk_size=50` 这么小**：这是本项目的关键判断，不是笔误。看知识库的内容形态：

```text
年假天数： 天
报销标准：市内交通 元/天
打卡方式：指纹打卡
```

这是**键值对式的短字段列表**，一行就是一条完整信息。用 500 字的块，会把"报销制度"和"考勤管理"混在同一个块里；检索时命中这个块，喂给 LLM 的上下文里就有一半是噪声。用 50 字，每个块基本就是 1-2 行，语义纯度最高。

**代价是**：那个跨段问题（"出发地"+"到账时间"）需要 `k=2` 才能凑齐两段信息。这也解释了为什么第二段代码里 k 取 2 而不是 1。

> **反过来说**：如果知识库是连续叙述型文本（手册、报告、合同），50 字就太小了——单块信息不完整，向量语义被稀释，反而检索不准。**chunk_size 必须跟着内容的"信息密度"走，没有通用最优值。**

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/01-问答与RAG系统/05-项目-企业内部制度问答助手.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「建库：二十行走完四步」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/01-问答与RAG系统/05-项目-企业内部制度问答助手.md)
