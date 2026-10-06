---
article_id: kp-b4d1c5f02ba6758d
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-c24a4924b596
learning_sourceId: c24a4924b596
learning_order: 11
learning_objective: 理解并验证：训练与验证的 checkpoint 策略
---

# 训练与验证的 checkpoint 策略

> **学习目标**：能够解释「训练与验证的 checkpoint 策略」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：因果语言模型与 `GPT2LMHeadModel`、多轮对话的上下文拼接、采样解码（temperature / top-k / top-p / repetition penalty）、Flask 模板渲染。
>
> **所属主题**：项目实战笔记 03：企业客服聊天机器人 · 核心实现

## 本次只学这一点

```python
# train.py（精简）
def train(model, train_dataloader, validate_dataloader, args):
    t_total = len(train_dataloader) // args.gradient_accumulation_steps * args.epochs
    optimizer = transformers.AdamW(model.parameters(), lr=args.lr, eps=args.eps)
    scheduler = transformers.get_linear_schedule_with_warmup(
    optimizer, num_warmup_steps=args.warmup_steps, num_training_steps=t_total)

    best_val_loss = 10000
    for epoch in range(args.epochs):
        train_loss = train_epoch(model, train_dataloader, optimizer, scheduler, epoch, args)

        # ① 每 10 个 epoch 定存一份（不依赖指标）
        if epoch % 10 == 0 or epoch == args.epochs:
            model.save_pretrained(os.path.join(args.save_model_path, 'bj_epoch{}'.format(epoch + 1)))

            # ② 验证 loss 创新低时存一份（min ppl）
            validate_loss = validate_epoch(model, validate_dataloader, epoch, args)
            if validate_loss < best_val_loss:
                best_val_loss = validate_loss
                model.save_pretrained(os.path.join(args.save_model_path, 'min_ppl_model_bj'))
```

**为什么要存两类 checkpoint**：困惑度（perplexity）最低 ≠ 人读起来最好。语料是"要点罗列"风格时，模型学会模板化输出反而 loss 更低。定存 + 最优存两条线，才会在事后有得选。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/02-对话与生成系统/03-项目-企业客服聊天机器人.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「训练与验证的 checkpoint 策略」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/02-对话与生成系统/03-项目-企业客服聊天机器人.md)
