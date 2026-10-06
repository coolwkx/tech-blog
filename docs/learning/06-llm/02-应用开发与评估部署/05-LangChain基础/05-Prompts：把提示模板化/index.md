---
article_id: kp-95b087ab226b754a
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-1043063b962d
learning_sourceId: 1043063b962d
learning_order: 4
learning_objective: 理解并验证：Prompts：把提示模板化
---

# Prompts：把提示模板化

> **学习目标**：能够解释「Prompts：把提示模板化」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：大模型 API 与消息角色（见《05-大模型API与调用实践》）、embedding 与向量检索（见《07-向量数据库与Milvus》）。
>
> **所属主题**：-LangChain基础 · 关键机制

## 本次只学这一点

| 模板 | 关键参数 | 用途 |
|---|---|---|
| `PromptTemplate` | `template`、`input_variables` | zero-shot 场景，把提示参数化复用 |
| `FewShotPromptTemplate` | `examples`、`example_prompt`、`prefix`、`suffix`、`input_variables`、`example_separator` | few-shot 场景，让模型理解更复杂的业务 |

```python
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate

prompt = PromptTemplate(template="我的邻居姓{lastname}，他生了个儿子，给他儿子起个名字",
input_variables=["lastname"])

examples = [{"word": "开心", "antonym": "难过"}, {"word": "粗", "antonym": "细"}]
example_prompt = PromptTemplate(input_variables=["word", "antonym"],
template="单词:{word}\n反义词:{antonym}")
few_shot = FewShotPromptTemplate(examples=examples, example_prompt=example_prompt,
prefix="给出每个单词的反义词", suffix="单词:{input}\n反义词:",
input_variables=["input"], example_separator="\n")
print(few_shot.format(input="高"))
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Prompts：把提示模板化」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)
