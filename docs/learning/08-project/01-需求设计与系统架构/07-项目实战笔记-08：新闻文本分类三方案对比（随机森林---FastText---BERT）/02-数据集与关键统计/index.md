---
article_id: kp-b9a31d896c450091
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-8f6e59312d25
learning_sourceId: 8f6e59312d25
learning_order: 1
learning_objective: 理解并验证：数据集与关键统计
---

# 数据集与关键统计

> **学习目标**：能够解释「数据集与关键统计」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：TF-IDF 与词袋模型、jieba 分词、`sklearn` 的 `TfidfVectorizer` / `RandomForestClassifier`、PyTorch 训练循环、BERT 的 `[CLS]` 与 attention mask。
>
> **所属主题**：项目实战笔记 08：新闻文本分类三方案对比（随机森林 / FastText / BERT） · 项目目标与业务背景

## 本次只学这一点

```text
train.txt 180000 条 | dev.txt 10000 条 | test.txt 10000 条 | class.txt 10 类
格式： 文本 \t 数字标签
```

```text
label → 0 finance 1 realty 2 home 3 education 4 science
 5 society 6 politics 7 sports 8 game 9 fashion

Counter({3:18000, 4:18000, 1:18000, 7:18000, 5:18000,
 9:18000, 8:18000, 2:18000, 6:18000, 0:18000}) ← 严格均衡，每类 10.0%

length_mean = 19.21 length_std = 3.86
```

**这两个统计数字各自决定了一个关键决策**：

- **类别严格均衡** → 所以 `accuracy` 在这里是可信指标。若类别不均衡（某类占 60%），单看 accuracy 会被多数类掩盖，必须看 macro-F1 或每类指标。这是评估时最常踩的坑。
- **平均 19.21 字、标准差 3.86** → BERT 的 `pad_size` 取 32 即可（19.21 + 2×3.86 ≈ 27，覆盖 95% 以上样本）。用 BERT 默认的 512 是巨大浪费：**注意力成本 O(L²)，512 相比 32 是 256 倍计算量。**

**这就是"先做数据分析再写模型"的价值**：一次 20 行的统计脚本，直接决定了后面所有模型的输入长度和成本。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/03-文本分类系统/08-项目-新闻文本分类三方案对比（随机森林FastTextBERT）.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「数据集与关键统计」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/03-文本分类系统/08-项目-新闻文本分类三方案对比（随机森林FastTextBERT）.md)
