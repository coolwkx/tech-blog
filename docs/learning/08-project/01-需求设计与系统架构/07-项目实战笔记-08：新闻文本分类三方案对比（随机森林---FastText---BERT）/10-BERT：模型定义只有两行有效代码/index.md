---
article_id: kp-915132fa282d2942
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-8f6e59312d25
learning_sourceId: 8f6e59312d25
learning_order: 11
learning_objective: 理解并验证：BERT：模型定义只有两行有效代码
---

# BERT：模型定义只有两行有效代码

> **学习目标**：能够解释「BERT：模型定义只有两行有效代码」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：TF-IDF 与词袋模型、jieba 分词、`sklearn` 的 `TfidfVectorizer` / `RandomForestClassifier`、PyTorch 训练循环、BERT 的 `[CLS]` 与 attention mask。
>
> **所属主题**：项目实战笔记 08：新闻文本分类三方案对比（随机森林 / FastText / BERT） · 核心实现

## 本次只学这一点

```python
class Model(nn.Module):
    def __init__(self, config):
        super(Model, self).__init__
        self.bert = BertModel.from_pretrained(config.bert_path, config=config.bert_config)
        self.fc = nn.Linear(config.hidden_size, config.num_classes) # 768 → 10

        def forward(self, x):
            context, mask = x[0], x[2]
            _, pooled = self.bert(context, attention_mask=mask, return_dict=False)
            return self.fc(pooled)
```

配置里的关键取舍：

```python
self.num_epochs = 2 # 只训 2 轮（多了过拟合且成本翻倍）
self.batch_size = 128
self.pad_size = 32 # 与数据分布匹配
self.learning_rate = 5e-5 # 远小于从头训练的 1e-3
```

**`lr=5e-5` 是微调的核心常识**：BERT 已经学到了很好的表示，用从头训练的大学习率会把它"冲毁"（catastrophic forgetting）。**微调的学习率要比从头训练小一到两个数量级。** 日志里第 1 轮就 Val Acc 92.1%、第 2 轮 93.0%，随后出现 `No optimization for a long time, auto-stopping...`（早停生效）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/03-文本分类系统/08-项目-新闻文本分类三方案对比（随机森林FastTextBERT）.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「BERT：模型定义只有两行有效代码」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/03-文本分类系统/08-项目-新闻文本分类三方案对比（随机森林FastTextBERT）.md)
