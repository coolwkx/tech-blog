---
article_id: kp-392159db2343090c
learning_kind: article
learning_category: 08-project
learning_direction: practice
learning_topic: topic-314d719df758
learning_sourceId: 314d719df758
learning_order: 15
learning_objective: 理解并验证：踩坑与解决
---

# 踩坑与解决

> **学习目标**：能够解释「踩坑与解决」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT 与 MLM（掩码语言模型）预训练目标、`[MASK]` token 的语义、`AutoModelForMaskedLM` 与 `AutoTokenizer`、HuggingFace `datasets.map(batched=True)`、PyTorch 训练循环与 `CrossEntropyLoss`。
>
> **所属主题**：项目实战笔记 06：电商评论分类（BERT+PET 与 BERT+P-Tuning） · 踩坑与解决

## 本次只学这一点

| 现象 | 根因 | 解决 | 如何预防 |
| --- | --- | --- | --- |
| P-Tuning 指标明显偏低但训练不报错 | `attention_mask` 沿用了 tokenizer 的返回值，伪 token `[unused*]` 被当成 `[PAD]` 忽略，软模板失效 | `get_attention_mask` 按 `id > 0` 重新生成 | **只要手工往序列插了 token，就必须重算 attention_mask**；这类 bug 不报错、只掉点，最耗时间 |
| `mask_position` 全部偏移，预测全错 | 伪 token 插在前面后 `[MASK]` 实际位置整体右移 | `mask_positions = [len(p_tokens_ids) + start_mask_position + i ...]` | 位置一律**从最终 input_ids 反查**（像 PET 用 `np.where`），不要手算偏移 |
| 报 `Lable Error: "xxx" not in label_dict` | 模型的预测词不在 verbalizer 表里 | 传 `hard_mapping=True` 走最长公共子串兜底 | 映射表要覆盖"主标签 + 常见子标签 + 主标签自身" |
| 推理结果总是返回"无" | `hard_mapping=False`，或主标签没把自己列进子标签 | 打开 `hard_mapping`；确保 `主标签\t主标签,子标签1,...` | 建表时自查：`find_main_label(主标签)` 是否等于主标签本身 |
| `ValueError: too many values to unpack` | 评论内容含制表符，`split('\t')` 切出 3 段以上 | `split('\t', 1)` 限制只切一刀 | 解析"标签 + 自由文本"格式时**永远限制 split 次数** |
| 训练 loss 不降，或某些类别 loss 天然偏高 | `mlm_loss` 里没除以 `len(sub_mask_labels)`，子标签多的类别 loss 被放大 | `cur_loss = cur_loss / len(single_sub_mask_labels)` | 变长目标做加权平均前一律先按个数归一化 |
| 换了模板后准确率掉 20 个百分点 | PET 的硬模板本身不稳定 | 尝试多个模板取最优；或改用 P-Tuning 软模板 | 硬模板的效果对写法极度敏感，**必须当超参数来调** |
| 标签是 3 个字时被截断，永远预测不对 | `max_label_len=2` 只留 2 个 `[MASK]` | 按数据集里最长的标签词设置 `max_label_len` | 设值前先统计所有子标签的长度分布 |
| 伪 token 数量改大后报错 | `[unused]` 只有 99 个，且必须与 `p_embedding_num` 匹配 | `p_embedding_num ≤ 99`，且 `[unused1]`..`[unusedN]` 要连续 | 用 `[unused]` 做软模板前先确认词表有多少可用空位 |
| 训到最后一个 checkpoint 效果反而变差 | 小样本训练波动大，最后一步未必最好 | 每个 `valid_steps` 评估，保存 **F1 最优**的 `model_best` | 小样本场景**必须按验证指标选模型**，不能默认用最后一个 |
| `datasets` 映射时异常样本被静默跳过 | 代码里用了裸 `except: continue` | 至少打印被跳过的样本 | 静默跳数据会让"训练集 63 条"实际只有 50 条参与，且你毫无感知 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/03-文本分类系统/06-项目-电商评论分类（BERT+PET与P-Tuning）.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「踩坑与解决」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/03-文本分类系统/06-项目-电商评论分类（BERT+PET与P-Tuning）.md)
