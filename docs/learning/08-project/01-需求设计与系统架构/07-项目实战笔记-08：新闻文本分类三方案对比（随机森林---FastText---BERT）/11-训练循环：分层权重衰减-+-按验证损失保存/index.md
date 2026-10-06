---
article_id: kp-5807a66df9e69b0a
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-8f6e59312d25
learning_sourceId: 8f6e59312d25
learning_order: 12
learning_objective: 理解并验证：训练循环：分层权重衰减 + 按验证损失保存
---

# 训练循环：分层权重衰减 + 按验证损失保存

> **学习目标**：能够解释「训练循环：分层权重衰减 + 按验证损失保存」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：TF-IDF 与词袋模型、jieba 分词、`sklearn` 的 `TfidfVectorizer` / `RandomForestClassifier`、PyTorch 训练循环、BERT 的 `[CLS]` 与 attention mask。
>
> **所属主题**：项目实战笔记 08：新闻文本分类三方案对比（随机森林 / FastText / BERT） · 核心实现

## 本次只学这一点

```python
no_decay = ["bias", "LayerNorm.bias", "LayerNorm.weight"]
optimizer_grouped_parameters = [
{"params": [p for n, p in model.named_parameters if not any(nd in n for nd in no_decay)],
"weight_decay": 0.01},
{"params": [p for n, p in model.named_parameters if any(nd in n for nd in no_decay)],
"weight_decay": 0.0},
]
optimizer = AdamW(optimizer_grouped_parameters, lr=config.learning_rate)

dev_best_loss = float("inf")
for epoch in range(config.num_epochs):
    for i, (trains, labels) in enumerate(tqdm(train_iter)):
        outputs = model(trains)
        model.zero_grad()
        loss = loss_fn(outputs, labels)
        loss.backward()
        optimizer.step

        if total_batch % 100 == 0 and total_batch != 0:
            dev_acc, dev_loss = evaluate(config, model, dev_iter)
            if dev_loss < dev_best_loss:
                dev_best_loss = dev_loss
                torch.save(model.state_dict, config.save_path)
                improve = "*"
                model.train # ★ 评估后必须切回 train 模式
```

**两个必须理解的设计**：

**（1）为什么 bias 和 LayerNorm 不做权重衰减。** `weight_decay`（L2）的作用是把参数往 0 拉，防过拟合的机制是抑制"权重大但只在少数样本起作用"的特征。但：**bias** 只负责平移激活值，不控制任何特征强度，往 0 拉只损害表达能力；**LayerNorm 的 γ/β** 见 `y = γ·(x-μ)/σ + β`，把 γ 往 0 拉会让 LayerNorm 退化成"只归一化、不恢复尺度"，后面的层收到的输入被压到接近零均值单位方差，模型容量被严重限制——**这是对表示能力的直接损害，而不是正则化。** 这是 BERT 原论文的标准配置。

**（2）为什么按 `dev_loss` 而不是 `dev_acc` 保存。** 准确率是离散的（10000 条样本最小变化 0.01%），训练后期会长时间不动，模型"看起来没进步但实际在变好"；loss 连续，对每一点改善都有响应。**但 loss 更低 ≠ 准确率更高**——最终选模型时仍应按业务指标。更成熟的做法是**两者都记录、按业务指标选**（对照 PET 项目里"保存 F1 最优模型"）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/03-文本分类系统/08-项目-新闻文本分类三方案对比（随机森林FastTextBERT）.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「训练循环：分层权重衰减 + 按验证损失保存」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/03-文本分类系统/08-项目-新闻文本分类三方案对比（随机森林FastTextBERT）.md)
