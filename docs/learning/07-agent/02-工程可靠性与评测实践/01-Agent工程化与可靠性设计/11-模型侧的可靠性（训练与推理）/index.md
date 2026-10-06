---
article_id: kp-fe266e625fd4b43a
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-0ae5654d8e63
learning_sourceId: 0ae5654d8e63
learning_order: 10
learning_objective: 理解并验证：模型侧的可靠性（训练与推理）
---

# 模型侧的可靠性（训练与推理）

> **学习目标**：能够解释「模型侧的可靠性（训练与推理）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的工具协议与错误处理、[05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的状态持久化、[08-大宗商品价格监控Agent项目复盘](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md)。
>
> **所属主题**：-Agent工程化与可靠性设计 · 关键机制

## 本次只学这一点

医疗问诊机器人的训练脚本（`train.py`）体现了模型侧的稳健性设计：

| 机制 | 实现 | 作用 |
| --- | --- | --- |
| 验证集评估 | 每个 epoch 后 `validate_epoch` 计算验证 loss | 及时发现过拟合 |
| 最优模型保存 | `if validate_loss < best_val_loss:` 保存 `min_ppl_model` | 最终用的是最好的检查点而非最后一个 |
| 梯度累积 | `if (batch_idx + 1) % gradient_accumulation_steps == 0` | 显存不足时模拟大 batch |
| 梯度裁剪 | `clip_grad_norm_(model.parameters(), args.max_grad_norm)` | 防梯度爆炸 |
| 学习率调度 | `get_linear_schedule_with_warmup` | 预热 + 线性衰减 |
| 损失忽略项 | `ignore_index=-100`，`labels.ne(ignore_index)` | padding 不参与损失与准确率计算 |

推理侧则用三个技巧控制生成质量：**屏蔽 `[UNK]`**（`next_token_logits[unk_id] = -float('Inf')`）、**重复惩罚**（对已生成 token 降权）、**`[SEP]` 作为停止符**（避免无限生成）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「模型侧的可靠性（训练与推理）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md)
