---
article_id: kp-0d332a42d5becd32
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-eeb0dcb17743
learning_sourceId: eeb0dcb17743
learning_order: 5
learning_objective: 理解并验证：用 RAGAS 跑评估：代码结构
---

# 用 RAGAS 跑评估：代码结构

> **学习目标**：能够解释「用 RAGAS 跑评估：代码结构」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：RAG 完整链路（见《09-RAG系统构建》）、LLM 调用与 Prompt 设计（见《04-提示词工程》）、embedding 与余弦相似度。
>
> **所属主题**：-RAG评估与优化 · 关键机制

## 本次只学这一点

`ragas_evaluate.py` 的五个步骤：

| 步骤 | 做什么 |
|---|---|
| ① 数据集加载 | 从 JSON 加载包含 question / answer / context / ground_truth 的评估数据集 |
| ② 数据格式转换 | 转换为 RAGAS 要求的 `Dataset` 格式 |
| ③ 环境配置 | 用 LangChain 的 OpenAI 模型与嵌入模型初始化 RAGAS 评估环境 |
| ④ 评估执行 | 计算 faithfulness、answer_relevancy、context_relevancy、context_recall |
| ⑤ 结果输出 | 打印并保存为 CSV，便于统计分析和多次运行比较 |

```python
# 依赖：pip install ragas datasets langchain-openai pandas
import json
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_relevancy, context_recall
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
```

**三个配置要点**：
① `ChatOpenAI` 用于生成评估所需的推理（如判断忠实度），需指定模型与 API Key；
② `OpenAIEmbeddings` 用于计算语义相似度（如答案相关性）；
③ **可替换为其他 LLM（如通义千问），只需适配 LangChain 的模型接口**——这意味着国内环境完全可以用
DashScope / 本地 Ollama 替代，不必依赖 OpenAI。

**结果示例**（字典，各指标 0~1，1 为最佳）：

```python
{'faithfulness': 0.95, 'answer_relevancy': 0.92, 'context_relevancy': 0.90, 'context_recall': 0.93}
```

结果保存为 CSV（`ragas_evaluation_results.csv`）的价值在于：**多次运行可横向比较**，
从而判断「这次改动到底有没有提升」。代码结构通用，可用于任何 RAG 系统评估，只需替换数据集与 LLM 配置；
也可扩展指标（如 `answer_correctness`）或添加自定义数据处理逻辑（如过滤低质量数据）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/07-检索增强RAG/10-RAG评估与优化.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「用 RAGAS 跑评估：代码结构」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/07-检索增强RAG/10-RAG评估与优化.md)
