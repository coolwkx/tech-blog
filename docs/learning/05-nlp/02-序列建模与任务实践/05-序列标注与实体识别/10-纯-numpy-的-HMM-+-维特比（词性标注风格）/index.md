---
article_id: kp-3c83badff5032760
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-00dabbf9e8f9
learning_sourceId: 00dabbf9e8f9
learning_order: 9
learning_objective: 理解并验证：纯 numpy 的 HMM + 维特比（词性标注风格）
---

# 纯 numpy 的 HMM + 维特比（词性标注风格）

> **学习目标**：能够解释「纯 numpy 的 HMM + 维特比（词性标注风格）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 01 篇的词性标注与 NER 两阶段拆解、概率论基础（条件概率、贝叶斯）、softmax 与交叉熵。
>
> **所属主题**：序列标注与实体识别 · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install numpy
import numpy as np

# 状态（隐状态）与观测（词）词表
states = ["n", "v", "r"]
observations = ["人生", "该", "如何", "起头", "猫", "吃", "鱼"]

# 初始概率 pi
pi = np.array([0.6, 0.3, 0.1])

# 转移概率 A[i][j] = P(y_t = j | y_{t-1} = i)
A = np.array([
[0.3, 0.4, 0.3], # n -> n/v/r
[0.4, 0.3, 0.3], # v -> n/v/r
[0.5, 0.4, 0.1], # r -> n/v/r
])

# 发射概率 B[j][k] = P(观测 k | 状态 j)，加平滑避免 0 概率
B = np.array([
[0.30, 0.10, 0.10, 0.20, 0.10, 0.05, 0.05], # n
[0.10, 0.05, 0.05, 0.10, 0.05, 0.40, 0.25], # v
[0.20, 0.30, 0.20, 0.05, 0.10, 0.05, 0.10], # r
])

def viterbi(obs_seq, states, pi, A, B):
    """观测序列 -> 最优隐状态序列（对数域实现，避免下溢）"""
    obs_idx = [observations.index(o) for o in obs_seq]
    n, K = len(obs_idx), len(states)
    log_pi, log_A, log_B = np.log(pi), np.log(A), np.log(B)

    delta = np.zeros((n, K)) # 到达每个位置每个状态的最大对数概率
    psi = np.zeros((n, K), dtype=int) # 最优前驱状态

    delta[0] = log_pi + log_B[:, obs_idx[0]]
    for t in range(1, n):
        for j in range(K):
            scores = delta[t - 1] + log_A[:, j]
            psi[t, j] = int(np.argmax(scores))
            delta[t, j] = scores[psi[t, j]] + log_B[j, obs_idx[t]]

            # 回溯
            path = [int(np.argmax(delta[n - 1]))]
            for t in range(n - 1, 0, -1):
                path.append(int(psi[t, path[-1]]))
                path.reverse()
                return [states[i] for i in path], delta

            for sent in [["人生", "该", "如何", "起头"], ["猫", "吃", "鱼"], ["鱼", "吃", "猫"]]:
                tags, delta = viterbi(sent, states, pi, A, B)
                print(f"{' '.join(sent):<20} -> {' '.join(tags)} (log P = {delta[len(sent)-1].max:.4f})")
```

预期现象：`猫 吃 鱼` 会得到 `n / v / n`，而把语序换成 `鱼 吃 猫` 仍得到 `n / v / n` —— HMM 只建模相邻依赖，看不出「谁是施事」。把它和后面 BiLSTM 能区分的例子对照，就能直观体会**齐次马尔可夫假设的代价**。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/06-序列标注与实体识别.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「纯 numpy 的 HMM + 维特比（词性标注风格）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/06-序列标注与实体识别.md)
