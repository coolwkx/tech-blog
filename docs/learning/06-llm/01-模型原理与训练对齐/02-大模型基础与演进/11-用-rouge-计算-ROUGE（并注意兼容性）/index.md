---
article_id: kp-697e2c42489983ef
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-6495f5dc2b1b
learning_sourceId: 6495f5dc2b1b
learning_order: 10
learning_objective: 理解并验证：用 rouge 计算 ROUGE（并注意兼容性）
---

# 用 rouge 计算 ROUGE（并注意兼容性）

> **学习目标**：能够解释「用 rouge 计算 ROUGE（并注意兼容性）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：概率论中的链式法则与条件概率、softmax、交叉熵、Python 基础（列表/字典/循环）。
>
> **所属主题**：-大模型基础与演进 · 可运行示例

## 本次只学这一点

```python
# 依赖：pip install rouge
from rouge import Rouge

generated_text = "This is some generated text."
reference_texts = ["This is another generated reference text."]

rouge = Rouge
scores = rouge.get_scores(generated_text, reference_texts[0])[0]
# 注意：get_scores 返回的是列表，取 [0] 才是这一对文本的分数
print("ROUGE-1 precision:", scores["rouge-1"]["p"])
print("ROUGE-1 recall:", scores["rouge-1"]["r"])
print("ROUGE-1 f1:", scores["rouge-1"]["f"])
```

> 常见坑：`rouge` 包只按空格切词且不区分大小写，中文必须先分词（如 jieba）再以空格拼接；
> 该包在较新 Python 上可能有兼容问题，若安装失败可用 `rouge-chinese` 或自行实现 ROUGE-N 召回率。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/01-大模型基础与演进.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「用 rouge 计算 ROUGE（并注意兼容性）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/01-大模型基础与演进.md)
