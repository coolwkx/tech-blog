---
article_id: kp-b8d6f2bd62053822
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-314d719df758
learning_sourceId: 314d719df758
learning_order: 13
learning_objective: 理解并验证：训练循环与评估
---

# 训练循环与评估

> **学习目标**：能够解释「训练循环与评估」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT 与 MLM（掩码语言模型）预训练目标、`[MASK]` token 的语义、`AutoModelForMaskedLM` 与 `AutoTokenizer`、HuggingFace `datasets.map(batched=True)`、PyTorch 训练循环与 `CrossEntropyLoss`。
>
> **所属主题**：项目实战笔记 06：电商评论分类（BERT+PET 与 BERT+P-Tuning） · 核心实现

## 本次只学这一点

```text
def model2train:
 model = AutoModelForMaskedLM.from_pretrained(pc.pre_model) # ★ 用 MLM 头，不换分类头
 tokenizer = AutoTokenizer.from_pretrained(pc.pre_model)
 verbalizer = Verbalizer(verbalizer_file=pc.verbalizer, tokenizer=tokenizer,
 max_label_len=pc.max_label_len)

 # 分层权重衰减：bias 和 LayerNorm 不衰减
 no_decay = ["bias", "LayerNorm.weight"]
 optimizer_grouped_parameters = [
 {"params": [p for n, p in model.named_parameters if not any(nd in n for nd in no_decay)],
 "weight_decay": pc.weight_decay},
 {"params": [p for n, p in model.named_parameters if any(nd in n for nd in no_decay)],
 "weight_decay": 0.0}]
 optimizer = torch.optim.AdamW(optimizer_grouped_parameters, lr=pc.learning_rate)

 train_dataloader, dev_dataloader = get_data
 max_train_steps = pc.epochs * len(train_dataloader)
 warm_steps = int(pc.warmup_ratio * max_train_steps)
 lr_scheduler = get_scheduler(name='linear', optimizer=optimizer,
 num_warmup_steps=warm_steps,
 num_training_steps=max_train_steps)

 criterion = torch.nn.CrossEntropyLoss
 global_step, best_f1 = 0, 0
 for epoch in range(pc.epochs):
 for batch in tqdm(train_dataloader):
 logits = model(input_ids=batch['input_ids'].to(pc.device),
 token_type_ids=batch['token_type_ids'].to(pc.device),
 attention_mask=batch['attention_mask'].to(pc.device)).logits

 # ★ 训练目标是"子标签"（软目标），不是原始标签
 mask_labels = batch['mask_labels'].numpy.tolist()
 sub_labels = [e['token_ids'] for e in verbalizer.batch_find_sub_labels(mask_labels)]

 loss = mlm_loss(logits, batch['mask_positions'].to(pc.device),
 sub_labels, criterion, pc.device)
 optimizer.zero_grad(); loss.backward(); optimizer.step; lr_scheduler.step

 global_step += 1
 if global_step % pc.valid_steps == 0:
 acc, precision, recall, f1, class_metrics = evaluate_model(
 model, metric, dev_dataloader, tokenizer, verbalizer)
 # 保存 F1 最优的模型（而不是最后一个）
 if f1 > best_f1:
 best_f1 = f1
 model.save_pretrained(os.path.join(pc.save_dir, "model_best"))
```

评估环节的关键是把预测出的 token **翻译回主标签**：

```python
def evaluate_model(model, metric, data_loader, tokenizer, verbalizer):
    model.eval
    with torch.no_grad:
        for batch in data_loader:
            logits = model(input_ids=..., attention_mask=..., token_type_ids=...).logits

            # ① mask_labels 去掉 [PAD]、转回文字作为 gold
            mask_labels = batch['mask_labels'].numpy.tolist()
            for i in range(len(mask_labels)):
                while tokenizer.pad_token_id in mask_labels[i]:
                    mask_labels[i].remove(tokenizer.pad_token_id)
                    mask_labels = [''.join(tokenizer.convert_ids_to_tokens(t)) for t in mask_labels]

                    # ② 预测 token → 子标签 → 主标签
                    predictions = convert_logits_to_ids(logits, batch['mask_positions']).cpu.numpy.tolist()
                    predictions = [e['label'] for e in verbalizer.batch_find_main_label(predictions)]

                    metric.add_batch(pred_batch=predictions, gold_batch=mask_labels)
                    return metric.compute['accuracy'], ..., metric.compute['class_metrics']
```

**这里有一个隐蔽的必要约束**：`gold` 用的是 `mask_labels`（原始标签词，如"衣服"），而 `pred` 是经 Verbalizer 反查的主标签。所以映射表必须保证**主标签词本身也是自己的子标签**——看 `verbalizer.txt`：

```text
电脑	电脑
水果	水果
衣服	衣服
```

每个主标签都把自己列为子标签之一，就是为了让 `find_main_label('水果')` 正确返回"水果"而不是走 `hard_mapping` 兜底。**自己实现时极容易忽略这一点。**

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/03-文本分类系统/06-项目-电商评论分类（BERT+PET与P-Tuning）.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「训练循环与评估」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/03-文本分类系统/06-项目-电商评论分类（BERT+PET与P-Tuning）.md)
