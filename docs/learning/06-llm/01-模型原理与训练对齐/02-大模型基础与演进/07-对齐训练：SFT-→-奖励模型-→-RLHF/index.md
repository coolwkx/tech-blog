---
article_id: kp-7b65450199b84e82
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-6495f5dc2b1b
learning_sourceId: 6495f5dc2b1b
learning_order: 6
learning_objective: 理解并验证：对齐训练：SFT → 奖励模型 → RLHF
---

# 对齐训练：SFT → 奖励模型 → RLHF

> **学习目标**：能够解释「对齐训练：SFT → 奖励模型 → RLHF」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：概率论中的链式法则与条件概率、softmax、交叉熵、Python 基础（列表/字典/循环）。
>
> **所属主题**：-大模型基础与演进 · 关键机制

## 本次只学这一点

「预训练 + 微调」解决的是「会不会」，**对齐（alignment）**解决的是「听不听话、合不合人类偏好」。扩展（《大模型的强化学习》）把 RLHF 讲得很细，这里提炼最小必需框架。

RLHF-PPO 阶段同时要跑**四个模型**：

| 角色 | 作用 | 是否训练 | 初始化 |
|---|---|---|---|
| Actor | 要优化的目标语言模型，输出 token 即「动作」 | 训练 | 由 SFT 模型初始化 |
| Critic | 估计状态价值 $V(s)$，用于计算优势（advantage） | 训练 | 通常用 RM 或 SFT 初始化 |
| Reward Model | 给「prompt + response」打分，提供即时收益 $R_t$ | 冻结 | RW 阶段训练得到 |
| Reference Model | 用 KL 散度约束 Actor 不要偏离 SFT 分布太远 | 冻结 | 由 SFT 模型初始化 |

NLP 语境下的强化学习映射关系：**状态 = prompt + 已生成的前文，动作 = 下一个 token（动作空间即词表），收益 = 奖励模型给出的分数**。加入 Reference Model + KL 惩罚的动机是缓解 **reward hacking**（模型钻奖励模型的空子，输出看似高分实则跑偏的内容）。

工程代价：若训练 70B 模型，PPO 需要同时载入约 $70\times4=280$B 参数，其中约 $70\times2=140$B 需要训练——**这就是 PPO「非常耗卡」的根本原因**。后续一系列工作都在削减模型数量：

| 方法 | 保留的模型 | 关键思想 |
|---|---|---|
| PPO | Actor + Critic + RM + Ref（4 个） | 用 Critic 拟合基线以降低方差，加入 importance sampling 与 clip |
| GRPO | 去掉 Critic | 对同一 prompt 采样 G 个答案，用组内平均分作为 baseline；KL 惩罚整体加到最终 loss |
| ReMax | 去掉 Critic | 用 greedy 解码的奖励作基线（$r-r_{greedy}$） |
| DPO | Actor + Ref（2 个） | 不需要显式 RM，直接在偏好数据对（chosen/rejected）上做类监督式优化 |
| ORPO | 仅 Actor（1 个） | SFT Loss + Odds Ratio Loss 合二为一，直接在偏好数据上训练 |

SFT（监督微调）是整条链路的起点：它用「指令 → 高质量回答」的样本让模型学会遵循指令，之后才能谈偏好对齐。**记住这条主线：预训练（学知识）→ SFT（学听话）→ RM（学评分）→ PPO/DPO（学偏好）。**

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/01-大模型基础与演进.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「对齐训练：SFT → 奖励模型 → RLHF」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/01-大模型基础与演进.md)
