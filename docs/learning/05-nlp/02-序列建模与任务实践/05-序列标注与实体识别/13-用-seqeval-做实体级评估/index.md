---
article_id: kp-cbeaa5926fa8329f
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-00dabbf9e8f9
learning_sourceId: 00dabbf9e8f9
learning_order: 12
learning_objective: 理解并验证：用 seqeval 做实体级评估
---

# 用 seqeval 做实体级评估

> **学习目标**：能够解释「用 seqeval 做实体级评估」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 01 篇的词性标注与 NER 两阶段拆解、概率论基础（条件概率、贝叶斯）、softmax 与交叉熵。
>
> **所属主题**：序列标注与实体识别 · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install seqeval
from seqeval.metrics import classification_report, f1_score

y_true = [["B-PER", "I-PER", "O", "B-ORG", "I-ORG", "I-ORG", "O"]]
y_pred = [["B-PER", "I-PER", "O", "B-ORG", "I-ORG", "O", "O"]]

print("实体级 F1:", round(f1_score(y_true, y_pred), 4))
print(classification_report(y_true, y_pred, digits=4))

# 对照：token 级准确率（会被 O 稀释，明显偏高）
tokens_total = sum(len(t) for t in y_true)
tokens_correct = sum(a == b for ta, tb in zip(y_true, y_pred) for a, b in zip(ta, tb))
print("token 级准确率: %.4f" % (tokens_correct / tokens_total))
```

运行后可以看到两个数字的明显落差——这正是「为什么必须用实体级 F1」的实证。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/06-序列标注与实体识别.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「用 seqeval 做实体级评估」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/06-序列标注与实体识别.md)
