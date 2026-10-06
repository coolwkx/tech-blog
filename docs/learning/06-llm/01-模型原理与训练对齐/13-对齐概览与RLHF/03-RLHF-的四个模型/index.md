---
article_id: kp-b3bd8284add5fe28
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-91e7f327ca9f
learning_sourceId: 91e7f327ca9f
learning_order: 2
learning_objective: 理解并验证：RLHF 的四个模型
---

# RLHF 的四个模型

> **学习目标**：能够解释「RLHF 的四个模型」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer 与自回归语言模型、交叉熵与最大似然、softmax 与对数概率、梯度的基本概念；了解「SFT 微调」是什么。有强化学习的策略（policy）与奖励（reward）概念更好，没有也能读，本文把需要的部分从头推导。
>
> **所属主题**：-对齐概览与RLHF · 核心概念

## 本次只学这一点

在 RLHF 的 PPO 阶段，显存里同时存在四个同规模模型：

| 角色 | 作用 | 是否训练 | 典型初始化 | 输入 → 输出 |
|---|---|---|---|---|
| Actor（策略） | 生成 response，是被优化的对象 | ✅ 训练 | SFT 模型 | prompt → response（含每 token log 概率） |
| Critic（价值） | 预测「从当前 token 起的期望总收益」$V_t$，给优势做基线 | ✅ 训练 | 由 Reward 模型初始化（加 value head） | prompt+response → 每 token 一个标量 $V_t$ |
| Reward | 给整条 response 打分，代表「即时收益」 | ❄️ 冻结 | 阶段二训好的 RM | prompt+response → 一个标量 $r_\phi$ |
| Reference | 提供 $\pi_{\text{ref}}$，用于算 KL 惩罚 | ❄️ 冻结 | SFT 模型（与 Actor 同源） | prompt+response → 每 token log 概率 |

**关键对应关系**：在「NLP 即强化学习」的视角下，状态 $S_t$ 是「prompt + 已生成的前 $t-1$ 个 token」，动作 $A_t$ 是「第 $t$ 个 token」，动作空间是词表 $V$，而 Actor 是智能体本身。

| 强化学习概念 | 语言模型中的对应 |
|---|---|
| 状态 $S_t$ | 上文 $x_{<t}$（prompt + 已生成 token） |
| 动作 $A_t$ | 第 $t$ 个 token |
| 动作空间 $\mathcal{A}$ | 词表 $V$（几万到十几万维） |
| 策略 $\pi_\theta(A_t\mid S_t)$ | 模型输出的 softmax 概率 |
| 即时收益 $R_t$ | 只有最后一个 token 位置有 RM 分数，其余位置只体现 KL 约束 |
| 总收益 $V_t$ | Critic 预测的「从 $t$ 到结束」的期望收益 |
| 轨迹终止 | 生成结束符 EOS 或达到最大长度 |

> **补充解释**：为什么只有最后一个 token 位置拿到 RM 分数？因为 Reward 模型训练时就是用「整条 response 的最后一个有效 token 位置的输出」作为整条回答的分数。中间位置没有客观奖励可标，于是用「是否偏离 Reference」这种可计算的信号来填充，具体见 2.4 节。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/03-对齐与后训练/01-对齐概览与RLHF.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「RLHF 的四个模型」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/03-对齐与后训练/01-对齐概览与RLHF.md)
