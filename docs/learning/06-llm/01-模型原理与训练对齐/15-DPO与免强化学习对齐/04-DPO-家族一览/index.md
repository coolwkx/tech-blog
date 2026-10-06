---
article_id: kp-f213a4f67609e56e
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-f5340ad3033e
learning_sourceId: f5340ad3033e
learning_order: 3
learning_objective: 理解并验证：DPO 家族一览
---

# DPO 家族一览

> **学习目标**：能够解释「DPO 家族一览」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Bradley-Terry 模型与排序损失、KL 散度、Sigmoid 与交叉熵、极大似然；读过第 01 篇（RLHF 与 KL 惩罚）和第 02 篇（奖励模型）会非常顺。
>
> **所属主题**：-DPO与免强化学习对齐 · 核心概念

## 本次只学这一点

| 方法 | 核心动机 | 与 DPO 的差异 | 是否需要参考模型 |
|---|---|---|---|
| DPO | 把 KL 约束下的 RL 最优解代回 BT 似然 | 基线 | 需要 |
| cDPO / rDPO | 标注必然有噪声，硬标签会过拟合 | 把标签按概率 $\epsilon$ 翻转，即目标用 $(1-\epsilon)\sigma(\cdot)+\epsilon\sigma(-\cdot)$ | 需要 |
| IPO | DPO 在「偏好确定性」（$p(y_w\succ y_l)=1$）时会把对数比推向无穷，导致过拟合 | 把 log-sigmoid 换成对「对数比与 $1/(2\beta)$ 的差」的平方损失，有界 | 需要 |
| KTO | 实际数据常是「单个回答 + 好/坏标签」，未必成对 | 基于前景理论的价值函数（对损失更敏感），直接用二值标签 | 需要 |
| ORPO | 想连参考模型也省掉 | 损失 = SFT 损失（在 chosen 上算交叉熵）$+\ \lambda\cdot$ odds ratio 惩罚 | **不需要** |
| SimPO | 参考模型占显存，且长度未归一化 | 用回答的平均对数概率作为隐式奖励，并加长度归一化与目标间隔 $\gamma$ | **不需要** |
| DPOP | DPO 可能把 chosen 的概率也压低 | 在 DPO 上加一项正则，限制 chosen 的对数比不低于参考 | 需要 |
| TDPO | PPO 有逐 token 的 KL 惩罚，DPO 没有 | 在 DPO 上加逐 token 的前向 KL 惩罚 | 需要 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/03-对齐与后训练/03-DPO与免强化学习对齐.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「DPO 家族一览」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/03-对齐与后训练/03-DPO与免强化学习对齐.md)
