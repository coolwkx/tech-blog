---
article_id: kp-7998be2e2d1693bc
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-8b0a9bea9dde
learning_sourceId: 8b0a9bea9dde
learning_order: 5
learning_objective: 理解并验证：训练与预测的关键实现
---

# 训练与预测的关键实现

> **学习目标**：能够解释「训练与预测的关键实现」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇 TF-IDF、第 05 篇文本分类流水线与评估指标、第 09 篇 BERT 微调、第 11 篇情感分析项目的工程范式。
>
> **所属主题**：NLP 项目实战：医疗文本分类 · 方法细节

## 本次只学这一点

```python
class MedicalTextDataset(Dataset):
    def __getitem__(self, idx):
        encoding = self.tokenizer(
        str(self.texts[idx]),
        add_special_tokens=True, # 自动加 [CLS] 与 [SEP]
        max_length=self.max_length, # 128
        padding='max_length',
        truncation=True,
        return_tensors='pt',
    )
    return {
'input_ids': encoding['input_ids'].flatten,
'attention_mask': encoding['attention_mask'].flatten,
'labels': torch.tensor(self.labels[idx], dtype=torch.long),
}
```

预测时两个必须动作：

```python
self.model.eval # 切换到评估模式，关闭 dropout
with torch.no_grad: # 不计算梯度，省显存
 outputs = self.model(**inputs)
 probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
 pred = torch.argmax(probs, dim=-1).item
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/12-NLP项目实战-医疗文本分类.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「训练与预测的关键实现」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/12-NLP项目实战-医疗文本分类.md)
