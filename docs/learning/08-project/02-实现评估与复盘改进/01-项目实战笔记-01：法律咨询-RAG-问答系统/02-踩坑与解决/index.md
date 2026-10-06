---
article_id: kp-93a8678689e6f857
learning_kind: article
learning_category: 08-project
learning_direction: practice
learning_topic: topic-e94c0577cb2f
learning_sourceId: e94c0577cb2f
learning_order: 13
learning_objective: 理解并验证：踩坑与解决
---

# 踩坑与解决

> **学习目标**：能够解释「踩坑与解决」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 工程化基础、向量检索原理（Embedding / 余弦相似度 / ANN）、LangChain 的 Document 与 TextSplitter 抽象、FastAPI 基础、MySQL 与 Redis 基本操作。
>
> **所属主题**：项目实战笔记 01：法律咨询 RAG 问答系统 · 踩坑与解决

## 本次只学这一点

| 现象 | 根因 | 解决 | 如何预防 |
| --- | --- | --- | --- |
| 评估时报 `KeyError: 1` | `evaluate_model` 把已经是数字的 label 又拿去查 `label_map`（key 是中文） | 直接使用传入的数字标签，只对 `texts` 分词：`true_labels = labels` | 约定"分词只发生在文本上，标签走出参口就已映射完毕"，别在多个方法里重复做同一层转换 |
| 子查询检索结果里有大量重复文档 | 用对象内存地址去重，内容相同但对象不同 | 改成 `{doc.page_content: doc for doc in all_docs}` 按内容去重 | 去重 key 要选**业务上唯一**的东西（文本/ID），不要用 Python 对象身份 |
| 重排序耗时陡增、收益不明显 | 对未去重的子块直接重排，同一父块被打分多次 | 先回溯父块、按 `parent_content` 去重，再对父块重排 | 精排成本 = 候选数 × CrossEncoder 前向，**进精排前先降候选**是通用原则 |
| 重启服务后第一次查询很慢 | Milvus 集合未 load 或 embedding/reranker 模型冷启动 | 集合存在时显式 `client.load_collection(name)`；模型在服务启动时预热 | 上线前跑一次"热身查询"，把懒加载都触发掉 |
| 会话历史裁剪 SQL 报错 | `DELETE ... WHERE id NOT IN (SELECT ... FROM 同一张表)` | 子查询外包一层派生表 `AS sub` | 记住 MySQL 的"不能在子查询里引用正在被修改的表"限制 |
| 相似但问法不同的 FAQ 问答不上 | 纯 BM25 是词面匹配，"多少钱"对不上"退还押金" | 降到 0.85 阈值以下自动走 RAG 兜底；也可做 Query 改写扩展同义词 | 不要试图把 FAQ 阈值调低来"提高命中"，那会把错误答案放出去；兜底链路才是正解 |
| 回答里偶尔出现"根据文档"但没有文档 | Prompt 里写了"如果答案来源于检索到的文档请说明"，模型对空上下文也照说 | 通用知识路径显式传 `context=""`，并在 Prompt 中区分有无上下文 | Prompt 的分支语义要在代码层面**真实**成立，不能只靠模型自觉 |
| 敏感信息（API Key、库密码）进了 Git | 配置直接写死在 `config.py` 默认值里 | 改走 `.env` + `dotenv`，`config.ini` 只留非敏感项 | 默认值一律给"安全的假值"，真值只从环境变量来 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/01-问答与RAG系统/01-项目-法律咨询RAG问答系统.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「踩坑与解决」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/01-问答与RAG系统/01-项目-法律咨询RAG问答系统.md)
