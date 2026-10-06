---
article_id: kp-80afd32900b1933d
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-91e7f327ca9f
learning_sourceId: 91e7f327ca9f
learning_order: 7
learning_objective: 理解并验证：Actor loss 的完整形式与 RLHF 特有的奖励设计
---

# Actor loss 的完整形式与 RLHF 特有的奖励设计

> **学习目标**：能够解释「Actor loss 的完整形式与 RLHF 特有的奖励设计」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer 与自回归语言模型、交叉熵与最大似然、softmax 与对数概率、梯度的基本概念；了解「SFT 微调」是什么。有强化学习的策略（policy）与奖励（reward）概念更好，没有也能读，本文把需要的部分从头推导。
>
> **所属主题**：-对齐概览与RLHF · 数学推导

## 本次只学这一点

综合以上，RLHF 的 Actor loss 是

$$L^{Actor}(\theta)=-\,\mathbb{E}_{t}\left[\min\Big(w_t A_t,\ \operatorname{clip}(w_t,1-\epsilon,1+\epsilon) A_t\Big)\right],\qquad w_t=\frac{\pi_\theta(a_t\mid s_t)}{\pi_{\theta_{old}}(a_t\mid s_t)}$$

其中优势由 GAE 从后往前递推：

$$A_t=\delta_t+\gamma\lambda A_{t+1},\qquad \delta_t=R_t+\gamma V_{t+1}-V_t,\qquad A_{T+1}=0$$

**这里 $R_t$ 的设计是 RLHF 与普通 RL 最大的不同。** 由于只有最后一个 token 位置有 RM 分数，其余位置的即时奖励用「与 Reference 的 KL 惩罚」填充：

$$R_t=\begin{cases}-\beta_{KL}\Big(\log\pi_\theta(a_t\mid s_t)-\log\pi_{\text{ref}}(a_t\mid s_t)\Big), & t\ne T\\[4pt] -\beta_{KL}\Big(\log\pi_\theta(a_t\mid s_t)-\log\pi_{\text{ref}}(a_t\mid s_t)\Big)+r_\phi(x,y), & t=T\end{cases}$$

**逐步理解这个设计：**

1. $\log\pi_\theta-\log\pi_{\text{ref}}$ 是 KL 散度的单样本估计：$D_{KL}(\pi_\theta\|\pi_{\text{ref}})=\mathbb{E}_{a\sim\pi_\theta}\left[\log\frac{\pi_\theta(a\mid s)}{\pi_{\text{ref}}(a\mid s)}\right]$，所以每生成一个 token，就累积了一份「偏离惩罚」。
2. 写成 $-\beta_{KL}(\log\pi_\theta-\log\pi_{\text{ref}})$ 后，**模型越认同某个 token（$\pi_\theta$ 越大），惩罚越大**——这正是在说「不要离 Reference 太远」。
3. 只有 $t=T$ 才加上真正的任务奖励 $r_\phi(x,y)$，因为只有终点的分数才代表整条回答的质量。中间位置的收益信号完全来自 KL 约束。
4. 实践上 $r_\phi$ 还会被裁剪到 $[-c,c]$（如 $c=5$），避免个别极端打分把优势打爆。
5. $\beta_{KL}$（deepspeed-chat 里的 `kl_ctl`）默认约 $0.1$，是控制「奖励信号」与「不跑偏约束」相对权重的关键旋钮。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/03-对齐与后训练/01-对齐概览与RLHF.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Actor loss 的完整形式与 RLHF 特有的奖励设计」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/03-对齐与后训练/01-对齐概览与RLHF.md)
