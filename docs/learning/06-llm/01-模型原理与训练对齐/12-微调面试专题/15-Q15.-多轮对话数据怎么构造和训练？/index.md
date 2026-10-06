---
article_id: kp-dd8ca13fb407fab6
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-bb7d4d1575e8
learning_sourceId: bb7d4d1575e8
learning_order: 14
learning_objective: 理解并验证：Q15. 多轮对话数据怎么构造和训练？
---

# Q15. 多轮对话数据怎么构造和训练？

> **学习目标**：能够解释「Q15. 多轮对话数据怎么构造和训练？」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer 基本结构、SFT 流程、LoRA/QLoRA 的原理、显存构成（权重/梯度/优化器状态/激活/KV cache）、常用评测指标。
>
> **所属主题**：-微调面试专题 · 第四组：训练与显存

## 本次只学这一点

<details markdown="1">
<summary markdown="1">参考答案</summary>

**30 秒版**：按对话轮次拼成一条序列，用角色模板（或 chat template）分隔，**只在 assistant 轮次上计算 loss**；注意超长样本按轮丢弃而不是硬截断，并保证 position id 与 attention mask 正确。

**展开版**——四个关键设计点：

1. **角色模板**：用基座模型官方 chat template，不要自己发明。模板与基座不匹配是多轮训练效果差的常见原因（模型没见过这种特殊 token 排布）。
2. **loss mask 粒度**：
   - 轮次级：只训 assistant 回复的 token；
   - 样本级：多轮中所有 assistant 轮次都训（推荐），或只训最后一轮（适合最后一轮是目标任务的场景）。
3. **长度处理**：按轮丢弃最老轮次，保留 system prompt（如果它是固定行为约束）与最后一轮；不要按 token 从中间硬切，会把一条回复切成两半。
4. **多样性**：数据要覆盖中断、用户纠错、话题切换、以及「无法回答」的情形。只训练「顺利的一问一答」会导致模型在真实对话中崩掉。

**要避免的三种坏数据**：

| 坏数据 | 后果 |
|---|---|
| 空 assistant 回复或占位的「（略）」 | 模型学会输出占位符 |
| 轮次不交替（连续两条 user） | 训练时角色混淆，推理时可能自问自答 |
| 把模型自己的历史错误回答当正样本 | 错误被强化，且会放大 |

```python
# 多轮数据的损失掩码示意（伪代码，需按具体 chat template 适配）
def build_labels(input_ids, assistant_spans, ignore_index=-100):
    """assistant_spans: List[Tuple[int, int]]，每个 assistant 回复的 [start, end) 区间"""
    labels = list(input_ids)
    keep = set()
    for s, e in assistant_spans:
        keep.update(range(s, e))
    for i in range(len(labels)):
        if i not in keep:
            labels[i] = ignore_index
    return labels
```

**追问预判**：
- *「多轮比单轮难在哪？」* —— 上下文依赖与错误累积。模型不仅要答对，还要和前文保持一致；训练数据里的历史错误会被当成上下文，进一步放大。
- *「system prompt 要参与 loss 吗？」* —— 不参与。它是行为约束的上下文，让模型学会「生成 system prompt」没有业务意义。

</details>

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/08-微调面试专题.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Q15. 多轮对话数据怎么构造和训练？」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/08-微调面试专题.md)
