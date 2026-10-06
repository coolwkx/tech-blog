---
article_id: kp-23328d06bbca9ed6
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-8f6e59312d25
learning_sourceId: 8f6e59312d25
learning_order: 9
learning_objective: 理解并验证：FastText：两条命令完成训练与调参
---

# FastText：两条命令完成训练与调参

> **学习目标**：能够解释「FastText：两条命令完成训练与调参」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：TF-IDF 与词袋模型、jieba 分词、`sklearn` 的 `TfidfVectorizer` / `RandomForestClassifier`、PyTorch 训练循环、BERT 的 `[CLS]` 与 attention mask。
>
> **所属主题**：项目实战笔记 08：新闻文本分类三方案对比（随机森林 / FastText / BERT） · 核心实现

## 本次只学这一点

```python
model = fasttext.train_supervised(
input=train_data_path,
autotuneValidationFile=dev_data_path, # 在验证集上随机搜索最优超参
autotuneDuration=100, # 搜索时间预算（秒），默认 300
wordNgrams=2, # 手动固定，不参与搜索
verbose=3) # 打印每一个 trial 的超参
result = model.test(test_data_path) # (10000, 0.9172, 0.9172)
model.save_model("./toutiao_fasttext_{}.bin".format(int(time.time)))
```

`autotune` 搜索的超参：`lr`（0.1）、`dim`（100）、`ws`（5）、`epoch`（5）、`minCount`（5）、`wordNgrams`（1）、`loss`（softmax）、`minn/maxn`。

搜索日志揭示了一个重要结论：

```text
Trial = 1: epoch=5, lr=0.1, dim=100 → currentScore = 0.912
Warning : wordNgrams is manually set to a specific value. It will not be automatically optimized.
Trial = 2: epoch=1, lr=0.705001, dim=320 → Best score: 0.912000
Training again with best arguments → (10000, 0.9172, 0.9172)
```

**两点解读**：

- **那个 Warning 是"人工先验 + 自动搜索"的混合策略**：把你确定的参数（`wordNgrams=2`）固定住，把不确定的交给搜索。搜索空间小、更快出结果，比"全部手调"省力，比"全部交给搜索"高效。
- **100 秒搜索只把 91.65% 提到 91.72%（+0.07 点），最终选的还是默认参数。** 这恰恰是最有信息量的结果：**FastText 对这个任务的超参敏感度极低**。对比"字切分 vs 词切分"带来 0.72 点差异——**数据层面的收益是超参层面的 10 倍。所以这个阶段该调的是数据，不是参数。**

`model.test` 返回 `(样本数, 精确率, 召回率)`。单标签分类下 FastText 的"精确率"就等于 accuracy（只输出 top-1），所以两个数相同，容易误以为算错了。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/03-文本分类系统/08-项目-新闻文本分类三方案对比（随机森林FastTextBERT）.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「FastText：两条命令完成训练与调参」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/03-文本分类系统/08-项目-新闻文本分类三方案对比（随机森林FastTextBERT）.md)
