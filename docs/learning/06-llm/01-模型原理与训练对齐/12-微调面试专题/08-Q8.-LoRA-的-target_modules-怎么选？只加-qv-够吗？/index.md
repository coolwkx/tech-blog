---
article_id: kp-2942b135eef16589
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-bb7d4d1575e8
learning_sourceId: bb7d4d1575e8
learning_order: 7
learning_objective: 理解并验证：Q8. LoRA 的 target_modules 怎么选？只加 qv 够吗？
---

# Q8. LoRA 的 target_modules 怎么选？只加 qv 够吗？

> **学习目标**：能够解释「Q8. LoRA 的 target_modules 怎么选？只加 qv 够吗？」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer 基本结构、SFT 流程、LoRA/QLoRA 的原理、显存构成（权重/梯度/优化器状态/激活/KV cache）、常用评测指标。
>
> **所属主题**：-微调面试专题 · 第二组：方法与参数

## 本次只学这一点

<details markdown="1">
<summary markdown="1">参考答案</summary>

**30 秒版**：`q_proj` + `v_proj` 是历史默认（来自原论文），参数量最省；但要效果最好，通常是把注意力（q/k/v/o）和 FFN（gate/up/down）全部加上。选择原则是「参数量预算允许时，覆盖面越广越好」。

**展开版**：

| 配置 | 相对参数量 | 效果 | 适用 |
|---|---|---|---|
| 只 `q_proj`、`v_proj` | 1× | 基线 | 极小样本、快速试验 |
| `q/k/v/o` | 2× | 通常 +0.5~1.5 点 | 通用选择 |
| `q/k/v/o` + FFN | 3~4× | 通常再 +0.5~1 点 | 数据量较大、任务较难 |
| 全部线性层 | 4×+ | 边际收益递减 | 逼近全参场景 |

**关键认知**：`target_modules` 对效果的影响常常**大于 r**。很多「r 调了没反应」的实验，真实瓶颈是覆盖面太窄。

**实例化时的写法差异**（不同框架的关键字不同，但都要显式指定）：

```python
from peft import LoraConfig, TaskType

cfg = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8,                     # 低秩维度
    lora_alpha=16,           # 缩放 = alpha / r = 2
    lora_dropout=0.05,       # 小数据集上建议 0.05 ~ 0.1
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    bias="none",             # 通常不训 bias，进一步省参数
)
```

**追问预判**：
- *「`bias` 该不该训？」* —— 一般 `none`。训练 bias 收益很小，但对齐类任务上偶尔有帮助；`all` 会显著增加参数量且更容易过拟合。
- *「modules_to_save 是干什么的？」* —— 用于把某些模块（如 `lm_head`、分类头）设为全参训练并与 LoRA 一起保存。当新增了词表 token 或换了任务头时通常需要它，否则保存的 adapter 加载后会缺这些权重。

</details>

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/08-微调面试专题.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Q8. LoRA 的 target_modules 怎么选？只加 qv 够吗？」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/08-微调面试专题.md)
