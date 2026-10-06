---
article_id: kp-4b1627a39be825c4
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-3d8f081f5ed3
learning_sourceId: 3d8f081f5ed3
learning_order: 5
learning_objective: 理解并验证：LangChain 内置工具一览
---

# LangChain 内置工具一览

> **学习目标**：能够解释「LangChain 内置工具一览」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的工具协议、[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的 ReAct 结构、[../llm/08-LangChain基础.md](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)。
>
> **所属主题**：-LangChain与工具编排 · 核心概念

## 本次只学这一点

通过 `get_all_tool_names()` 打印出全部工具名，按用途归类如下：

| 类别 | 工具名 |
| --- | --- |
| 搜索 | `google-search`、`bing-search`、`ddg-search`、`metaphor-search`、`searx-search`、`serpapi`、`google-serper`、`google-scholar`、`searchapi`、`wikipedia`、`arxiv`、`pubmed` |
| 代码与终端 | `python_repl`、`terminal`、`bash`（部分版本）、`wolfram-alpha` |
| HTTP 请求 | `requests`、`requests_get`、`requests_post`、`requests_patch`、`requests_put`、`requests_delete` |
| 计算 | `llm-math` |
| 天气 / 地理 | `openweathermap-api`、`open-meteo-api` |
| 多媒体与业务 | `dalle-image-generator`、`eleven_labs_text2speech`、`google_cloud_texttospeech`、`news-api`、`tmdb-api`、`podcast-api`、`sceneXplain` |
| 基础设施与协作 | `awslambda`、`graphql`、`human`、`memorize`、`sleep`、`golden-query`、`twilio`、`dataforseo-api-search` |

使用 `load_tools(["serpapi", "llm-math"], llm=llm)` 加载；其中 `llm-math` 内部依赖 LLM 来解析算式，所以必须把 `llm` 一并传入。使用 serpapi 需要申请 token、设置环境变量 `SERPAPI_API_KEY` 并安装 `google-search-results`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「LangChain 内置工具一览」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md)
