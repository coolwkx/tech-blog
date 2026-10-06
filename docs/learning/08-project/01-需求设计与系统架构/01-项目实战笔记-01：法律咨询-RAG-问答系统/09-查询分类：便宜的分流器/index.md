---
article_id: kp-d2be7cc2d0382a24
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-e94c0577cb2f
learning_sourceId: e94c0577cb2f
learning_order: 9
learning_objective: 理解并验证：查询分类：便宜的分流器
---

# 查询分类：便宜的分流器

> **学习目标**：能够解释「查询分类：便宜的分流器」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 工程化基础、向量检索原理（Embedding / 余弦相似度 / ANN）、LangChain 的 Document 与 TextSplitter 抽象、FastAPI 基础、MySQL 与 Redis 基本操作。
>
> **所属主题**：项目实战笔记 01：法律咨询 RAG 问答系统 · 核心实现

## 本次只学这一点

```python
class QueryClassifier:
    label_map = {"通用知识": 0, "专业咨询": 1}

    def __init__(self, model_path="bert_query_classifier"):
        self.tokenizer = BertTokenizer.from_pretrained("./bert-base-chinese")
        self.device = torch.device("cuda" if torch.cuda.is_available else "cpu")
        self.model = (BertForSequenceClassification.from_pretrained(model_path)
        if os.path.exists(model_path)
    else BertForSequenceClassification.from_pretrained(
    "bert-base-chinese", num_labels=2))
    self.model.to(self.device)

    def predict_category(self, query):
        if self.model is None:
            return "通用知识" # 兜底：走便宜路径
        enc = self.tokenizer(query, truncation=True, padding=True,
        max_length=128, return_tensors="pt")
        enc = {k: v.to(self.device) for k, v in enc.items()}
        with torch.no_grad:
            logits = self.model(**enc).logits
            return "专业咨询" if torch.argmax(logits, 1).item == 1 else "通用知识"
```

训练用 5000 条混合数据集（`training_dataset_hybrid_5000.json`），`bert-base-chinese` 微调 3 epoch、batch=8，验证集准确率约 93%，混淆矩阵 `[[460, 40], [30, 470]]`。**之所以不用规则**：当事人问法太散，"押金不退"和"能不能退押金"要靠语义。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/01-问答与RAG系统/01-项目-法律咨询RAG问答系统.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「查询分类：便宜的分流器」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/01-问答与RAG系统/01-项目-法律咨询RAG问答系统.md)
