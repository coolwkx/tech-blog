---
article_id: kp-ea4ddfc4429f1c86
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-8f6e59312d25
learning_sourceId: 8f6e59312d25
learning_order: 8
learning_objective: 理解并验证：随机森林：最小的可用基线
---

# 随机森林：最小的可用基线

> **学习目标**：能够解释「随机森林：最小的可用基线」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：TF-IDF 与词袋模型、jieba 分词、`sklearn` 的 `TfidfVectorizer` / `RandomForestClassifier`、PyTorch 训练循环、BERT 的 `[CLS]` 与 attention mask。
>
> **所属主题**：项目实战笔记 08：新闻文本分类三方案对比（随机森林 / FastText / BERT） · 核心实现

## 本次只学这一点

```python
tfidf = TfidfVectorizer(stop_words=open(STOP_WORDS).read.split())
text_vectors = tfidf.fit_transform(content['words'].values())
x_train, x_test, y_train, y_test = train_test_split(
text_vectors, content['label'], test_size=0.2, random_state=0)
model = RandomForestClassifier # n_estimators=100, gini, 不限深
model.fit(x_train, y_train)
ic(accuracy_score(model.predict(x_test), y_test)) # ic| accuracy: 0.8148
```

**TF-IDF 在做什么**：

```text
TF = 某词在本文档出现次数 / 本文档总词数 → 这个词对本文档有多重要
IDF = log(总文档数 / 包含该词的文档数 + 1) → 这个词有多稀有（+1 防除零）
TF-IDF = TF × IDF
```

核心思想：**某个词在本文档出现得多（TF 高）、在整个语料很少见（IDF 高），它就有很强的类别区分能力。** 代入本项目：18 万篇新闻里"的"几乎每篇都有 → IDF 极低 → 不参与分类；"湖人"只在体育类出现 → IDF 高 → 强特征。**这也解释了为什么还要叠加 `stop_words`**：把 IDF 已能压下去的词再压一遍，顺便减小特征维度。

随机森林是 Bagging 集成：有放回抽样 100 次训 100 棵树，每棵树只看随机的一部分特征，预测时投票。**随机性有两个来源（样本抽样 + 特征抽样），让单棵树的过拟合在投票里被平均掉。** 它训练几分钟、无需 GPU、不用调参就有 81.48%——**在真实项目里，"先有一个能上线的 80 分模型"比"花三个月追求 95 分"往往更有价值，因为你能立刻开始收集真实反馈。**

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/03-文本分类系统/08-项目-新闻文本分类三方案对比（随机森林FastTextBERT）.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「随机森林：最小的可用基线」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/03-文本分类系统/08-项目-新闻文本分类三方案对比（随机森林FastTextBERT）.md)
