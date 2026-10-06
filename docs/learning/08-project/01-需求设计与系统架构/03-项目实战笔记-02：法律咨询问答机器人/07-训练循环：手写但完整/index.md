---
article_id: kp-a891649bf983acd5
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-3e5bdcfe80e4
learning_sourceId: 3e5bdcfe80e4
learning_order: 7
learning_objective: 理解并验证：训练循环：手写但完整
---

# 训练循环：手写但完整

> **学习目标**：能够解释「训练循环：手写但完整」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer Decoder 结构与自注意力、因果语言模型（CLM）的 shift 对齐损失、PyTorch 的 `Dataset / DataLoader / collate_fn`、HuggingFace `transformers` 的 `GPT2LMHeadModel` 与 `BertTokenizerFast`。
>
> **所属主题**：项目实战笔记 02：法律咨询问答机器人 · 核心实现

## 本次只学这一点

```python
# train.py: train_epoch（精简）
def train_epoch(model, train_dataloader, optimizer, scheduler, epoch, args):
    model.train
    ignore_index = args.ignore_index # -100
    total_loss, epoch_correct_num, epoch_total_num = 0, 0, 0

    for batch_idx, (input_ids, labels) in enumerate(tqdm(train_dataloader)):
        input_ids, labels = input_ids.to(args.device), labels.to(args.device)

        outputs = model(input_ids, labels=labels) # 传了 labels，模型内部直接算 loss
        logits, loss = outputs.logits, outputs.loss.mean

        batch_correct_num, batch_total_num = calculate_acc(logits, labels, ignore_index)
        epoch_correct_num += batch_correct_num
        epoch_total_num += batch_total_num
        total_loss += loss.item

        # 梯度累积：把 loss 缩放后再 backward，4 步之后才更新一次参数
        if args.gradient_accumulation_steps > 1:
            loss = loss / args.gradient_accumulation_steps
            loss.backward()

            # 梯度裁剪，防止梯度爆炸
            torch.nn.utils.clip_grad_norm_(model.parameters(), args.max_grad_norm)

            if (batch_idx + 1) % args.gradient_accumulation_steps == 0:
                optimizer.step # 更新参数
                scheduler.step # 更新学习率（warmup + 线性衰减）
                optimizer.zero_grad() # 清空梯度

                return total_loss / len(train_dataloader)
```

优化器与调度器：

```python
def train(model, train_dataloader, validate_dataloader, args):
    # 总步数 = (每 epoch 步数 / 累积步数) × epoch 数
    t_total = len(train_dataloader) // args.gradient_accumulation_steps * args.epochs

    optimizer = transformers.AdamW(model.parameters(), lr=args.lr, eps=args.eps)
    scheduler = transformers.get_linear_schedule_with_warmup(
    optimizer, num_warmup_steps=args.warmup_steps, num_training_steps=t_total)

    best_val_loss = 10000
    for epoch in range(args.epochs):
        train_loss = train_epoch(model, train_dataloader, optimizer, scheduler, epoch, args)
        validate_loss = validate_epoch(model, validate_dataloader, epoch, args)

        # 保存困惑度最低的模型
        if validate_loss < best_val_loss:
            best_val_loss = validate_loss
            model.save_pretrained(os.path.join(args.save_model_path, 'min_ppl_model_bj'))
```

**`t_total` 为什么要除以 `gradient_accumulation_steps`**：`scheduler.step` 只在参数真正更新的那一步调用，所以总步数是"更新次数"而不是"前向次数"。写成 `len(dataloader) * epochs` 会导致学习率衰减到一半就归零，训练提前停滞——这是极高频的手写训练 bug。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/02-对话与生成系统/02-项目-法律咨询问答机器人.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「训练循环：手写但完整」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/02-对话与生成系统/02-项目-法律咨询问答机器人.md)
