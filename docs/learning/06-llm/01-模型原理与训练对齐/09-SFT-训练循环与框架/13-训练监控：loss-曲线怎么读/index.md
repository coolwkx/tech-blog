---
article_id: kp-d8c32b96e98582df
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-b7b8e8f583cb
learning_sourceId: b7b8e8f583cb
learning_order: 12
learning_objective: 理解并验证：训练监控：loss 曲线怎么读
---

# 训练监控：loss 曲线怎么读

> **学习目标**：能够解释「训练监控：loss 曲线怎么读」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：因果语言模型的训练目标；tokenizer 与特殊 token（BOS/EOS/PAD）；交叉熵损失；LoRA 的注入方式（见 [03 篇](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)）与显存账本（见 [02 篇](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)）。
>
> **所属主题**：SFT 训练循环与框架 · 关键机制

## 本次只学这一点

| 曲线形状 | 诊断 | 处理 |
| --- | --- | --- |
| 训练 loss 与验证 loss 同步平滑下降并收敛 | 正常 | 继续，按验证指标选 checkpoint |
| 训练 loss 持续下降，验证 loss 先降后升 | 过拟合 | 减少 epoch、加 dropout/weight decay、增数据 |
| loss 一开始就变成 NaN / inf | 学习率过大、fp16 溢出、数据含脏样本 | 降学习率、换 bf16、检查数据 |
| loss 剧烈震荡（锯齿状） | 学习率过大、batch 太小、warmup 不足 | 降学习率、加 warmup、增有效 batch |
| loss 几乎不降（平的） | 标签全被掩码成 -100、`target_modules` 没匹配上、学习率过小 | 检查 `labels != -100` 的比例、检查可训练参数 |
| loss 断崖式降到极低（如 0.01） | 数据泄漏（训练集与验证集重复、packing 未做 block-diagonal mask） | 去重、检查 mask |
| loss 周期性台阶 | 学习率调度器的阶梯点或数据按长度排序 | 正常，关注趋势 |

**梯度范数**：`grad_norm` 是第二个必须监控的量。

- 长期在 $10^{-3}$ 量级并且 loss 不降 → 学习率过小或梯度被裁剪过头；
- 频繁出现尖峰（$\gg$ `max_grad_norm`）→ 数据中有异常样本（超长、乱码）或学习率过大；
- 突然变成 0 → 该 batch 的所有 label 都是 -100（整批被掩码），此时 loss 为 nan 或 0，需要过滤。

**OOM 排查顺序**（按代价从低到高）：

```text
1. 降 per_device_train_batch_size 到 1，用 gradient_accumulation_steps 补回有效 batch
2. 开 gradient_checkpointing（注意同时把 use_cache=False）
3. 降 max_seq_len（检查是否有超长样本被截断）
4. 关掉 packing 或检查 packing 实现是否产生超长序列
5. 换优化器：adamw -> paged_adamw_8bit / adafactor
6. 换精度：fp32 -> bf16；QLoRA 场景把 bnb_4bit_compute_dtype 调低
7. 上 ZeRO 分片 / FSDP / CPU offload（见第 02 篇）
8. 仍不行则换更小的模型，或先做 LoRA
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/05-SFT训练循环与框架.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「训练监控：loss 曲线怎么读」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/05-SFT训练循环与框架.md)
