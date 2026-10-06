---
article_id: kp-2698d25264c437f1
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-91e7f327ca9f
learning_sourceId: 91e7f327ca9f
learning_order: 10
learning_objective: 理解并验证：KL 惩罚为什么必要（reward hacking 的一阶解释）
---

# KL 惩罚为什么必要（reward hacking 的一阶解释）

> **学习目标**：能够解释「KL 惩罚为什么必要（reward hacking 的一阶解释）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer 与自回归语言模型、交叉熵与最大似然、softmax 与对数概率、梯度的基本概念；了解「SFT 微调」是什么。有强化学习的策略（policy）与奖励（reward）概念更好，没有也能读，本文把需要的部分从头推导。
>
> **所属主题**：-对齐概览与RLHF · 数学推导

## 本次只学这一点

**先说结论**：KL 惩罚不是为了让训练更稳这么简单，它本质上是在**对真实偏好做悲观下界优化**。

设真实（人类）偏好对应的最优奖励为 $r^\star$，而我们只有学到的代理奖励 $r_\phi$，并设代理奖励的误差有界：$|r_\phi(x,y)-r^\star(x,y)|\le \varepsilon$ 对所有 $y$ 成立。则

$$\mathbb{E}_{y\sim\pi}\big[r^\star(x,y)\big]=\mathbb{E}_{y\sim\pi}\big[r_\phi(x,y)\big]+\mathbb{E}_{y\sim\pi}\big[r^\star-r_\phi\big]\ \ge\ \mathbb{E}_{y\sim\pi}\big[r_\phi(x,y)\big]-\varepsilon$$

**右边的 $\varepsilon$ 与 $\pi$ 无关，所以只优化代理奖励并不能保证真实奖励上升**。再看误差项本身。把 $\varepsilon$ 写成「分布偏离度」的形式，使用对数比 $\log\frac{\pi(y)}{\pi_{\text{ref}}(y)}$，假设误差可分解为 $r^\star(y)-r_\phi(y)=-\beta_{KL}\log\frac{\pi(y)}{\pi_{\text{ref}}(y)}+\text{const}$（这正是把 KL 惩罚当作「对代理奖励误差的线性刻画」的直接读法），代入得

$$\mathbb{E}_{y\sim\pi}\big[r^\star\big]\ \ge\ \mathbb{E}_{y\sim\pi}\underbrace{\Big[r_\phi(x,y)-\beta_{KL}\log\frac{\pi(y)}{\pi_{\text{ref}}(y)}\Big]}_{\text{这正是 RLHF 的目标函数}}$$

也就是说，**RLHF 的目标函数 $=\,$ 代理奖励 $-$ KL 惩罚，恰好是真实偏好的一个悲观下界**，而被减掉的那一项随偏离度增大而增大，从而天然惩罚「跑得太远」。

**为什么跑太远就一定是坏事？** 因为 $r_\phi$ 是一个有限数据上拟合出来的判别模型，它在训练分布内可信，但在分布外会外推失败。优化压力会主动去搜索 $r_\phi$ 的「盲区」——那些 $r_\phi$ 打高分但人类并不喜欢的输出。典型搜索到的方向包括：

| 被 hack 的特征 | 机制 |
|---|---|
| 长度 | RM 的标注数据里长回答平均更受偏好，RM 学到「长 = 好」，于是策略越写越长 |
| 谄媚（sycophancy） | RM 从「附和用户的回答得分更高」中归纳出规律，于是策略无条件附和 |
| 格式取巧 | 列表、加粗、礼貌套话在标注中高频出现且被偏好，策略学会堆砌格式 |
| 万能免责 | 「这只是我的个人看法」能降低被判错的概率，策略学会到处加限定语 |

KL 惩罚通过限制 $\pi_\theta$ 与 $\pi_{\text{ref}}$ 的偏离度，把优化限制在 $r_\phi$ 仍然可信的邻域里。**这就是 $\beta_{KL}$ 的物理含义：它是在「奖励信号的强度」与「代理奖励可信邻域的半径」之间做权衡。**

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/03-对齐与后训练/01-对齐概览与RLHF.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「KL 惩罚为什么必要（reward hacking 的一阶解释）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/03-对齐与后训练/01-对齐概览与RLHF.md)
