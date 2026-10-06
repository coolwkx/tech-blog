---
article_id: kp-bf192855e258790e
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-94a81d666c0a
learning_sourceId: 94a81d666c0a
learning_order: 13
learning_objective: 理解并验证：训练配置与常用超参
---

# 训练配置与常用超参

> **学习目标**：能够解释「训练配置与常用超参」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 08 篇的 Transformer Encoder 与 self-attention、第 04 篇的静态词向量局限、Python 类与 PyTorch 训练循环。
>
> **所属主题**：BERT 与预训练模型 · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install transformers torch
# BERT 微调的标准超参（Hugging Face 官方与的建议）
config = {
"learning_rate": 2e-5, # 或 3e-5 / 5e-5，必须很小
"batch_size": 16, # 16 或 32
"num_train_epochs": 3, # 3 或 4
"warmup_ratio": 0.1, # 前 10% steps 线性预热
"weight_decay": 0.01, # L2 正则
"max_grad_norm": 1.0, # 梯度裁剪
"max_length": 128, # 按句子长度分布定（头条项目用 32，医疗项目用 128）
}
print(config)
```

**为什么学习率必须这么小**：BERT 已经在大规模语料上预训练好了，学习率太大（如 0.01）会一步把预训练学到的知识冲垮，性能反而比随机初始化的模型更差。小学习率（2e-5）的作用是「只做微调」，保留预训练语义，同时适配新领域。

更精细的做法是**分层学习率**：底层用更小的学习率（1e-5），顶层和分类头用较大的学习率（1e-3~5e-5），因为底层学到的是通用语言特征，不该被小数据改动太多。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「训练配置与常用超参」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)
