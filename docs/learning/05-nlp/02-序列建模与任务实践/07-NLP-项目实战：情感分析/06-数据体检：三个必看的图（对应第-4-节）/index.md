---
article_id: kp-6edd6f0d9847e71f
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-cea0dd524785
learning_sourceId: cea0dd524785
learning_order: 5
learning_objective: 理解并验证：数据体检：三个必看的图（对应第 4 节）
---

# 数据体检：三个必看的图（对应第 4 节）

> **学习目标**：能够解释「数据体检：三个必看的图（对应第 4 节）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇 TF-IDF、第 05 篇文本分类流水线与评估指标、第 08/09 篇 BERT 微调、第 01 篇的文本数据分析。
>
> **所属主题**：NLP 项目实战：情感分析 · 方法细节

## 本次只学这一点

| 图 | 代码要点 | 看什么结论 |
|----|----------|-----------|
| 标签数量分布 | `sns.countplot(x="label", data=train_data, hue="label")` | 正负比例，决定是否需要增强 |
| 句子长度分布 | 新增 `sentence_length` 列；`sns.countplot` 柱状图 + `sns.displot(kde=True)` 密度曲线 | 定 `max_len`；长尾明显则考虑分块 |
| 正负样本长度散点 | `sns.stripplot(y="sentence_length", x="label", data=train_data, hue="label")` | **是否存在长度偏差**：如果正面评论系统性更长，模型可能学到「长=正面」的伪特征 |

第三张图是情感分析特有的检查项。很多真实数据集里，负面评论因为要列举问题而更长，或正面评论因为要夸而更长；一旦存在这种相关性，模型会走捷径，换到新数据上就崩。发现后应做长度分桶评估（把样本按长度分段分别算准确率），确认模型不是靠长度。

**词频与高频词云**（原样做法）：

```python
# 统计词表规模
train_vocab = set(chain(*map(lambda x: jieba.lcut(x), train_data["sentence"])))

# 只取形容词（词性 a）按类别画词云，能直接看出极性用词差异
def get_a_list(text):
 return [g.word for g in pseg.lcut(text) if g.flag == "a"]

p_a_words = list(chain(*map(get_a_list, train_data[train_data["label"] == 1]["sentence"])))
# WordCloud(font_path='SimHei.ttf', max_words=100, background_color="white").generate("".join(p_a_words))
```

词云的真正用途不是「好看」，而是**发现脏数据**：如果正面词云里出现「差 / 烂 / 垃圾」，要么是标注错误，要么是停用词/分词有问题，需要人工审核清洗。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/11-NLP项目实战-情感分析.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「数据体检：三个必看的图（对应第 4 节）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/11-NLP项目实战-情感分析.md)
