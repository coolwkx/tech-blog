---
article_id: kp-8e29bf5de5bb7cb5
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-b5809cd6128d
learning_sourceId: b5809cd6128d
learning_order: 9
learning_objective: 理解并验证：Unigram LM：概率模型 + EM + Viterbi
---

# Unigram LM：概率模型 + EM + Viterbi

> **学习目标**：能够解释「Unigram LM：概率模型 + EM + Viterbi」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 字符串与 `re` 模块；正则表达式；神经网络需要整数 id（embedding 查表）；Transformer 的 `attention_mask` 概念。
>
> **所属主题**：文本预处理与分词全流程 · 深入机制

## 本次只学这一点

Kudo 2018 的 Subword Regularization 提出 Unigram 语言模型分词，也是 SentencePiece 的另一种工作模式。**模型假设**：每个子词独立，句子 `x = (x₁, x₂, …, xₘ)` 的概率是各子词概率之积 `P(x) = Π p(xᵢ)`，且 `Σ_{w ∈ V} p(w) = 1`。

**训练用 EM**：
1. **初始化**：用较大的种子词表（BPE 或后缀数组枚举高频子串），给每个子词初始概率；
2. **E 步**：对每句话用前向-后向（或 Viterbi 近似）枚举所有切分，算出每个子词的**期望出现次数**；
3. **M 步**：用期望次数重新归一化，得到新的 `p(w)`；
4. **剪枝**：每轮按「删掉它损失多少似然」排序，删掉最不划算的一批子词（论文用 α 控制裁剪比例），直到达到目标词表大小。

**推理用 Viterbi**：在所有切分中找概率最大的路径（取对数后即最大和问题）。**子词正则化**（subword regularization）：训练时不用最优切分，而是按 `P(x)` **采样**若干切分（forward-filtering backward-sampling），相当于对分词做数据增强，让模型不依赖某一种切分 —— 这也是「同一句话两次 tokenize 结果不同」的来源，推理时必须关掉采样。

```python
import math

def viterbi(text, logp, unk_logp):
    """在给定子词对数概率下，找概率最大的切分（DP + 回溯）。"""
    n = len(text)
    best = [(-math.inf, 0)] * (n + 1) # best[i] = (到位置 i 的最优对数概率, 前驱)
    best[0] = (0.0, 0)
    for end in range(1, n + 1):
        for start in range(end):
            score = best[start][0] + logp.get(text[start:end], unk_logp)
            if score > best[end][0]:
                best[end] = (score, start)
                tokens, cur = [], n
                while cur > 0: # 回溯出切分
                    prev = best[cur][1]
                    tokens.append(text[prev:cur])
                    cur = prev
                    return tokens[::-1]

                probs = {"low": 0.20, "lo": 0.10, "l": 0.05, "o": 0.05, "w": 0.05, "e": 0.05, "s": 0.05,
                "t": 0.05, "wes": 0.08, "est": 0.10, "west": 0.12, "lowest": 0.05}
                logp = {k: math.log(v) for k, v in probs.items()}
                unk = math.log(1e-6) # 未登录子词的兜底概率
                for w in ["lowest", "lowestest", "west"]:
                    pieces = viterbi(w, logp, unk)
                    print(f"{w:10} -> {pieces} score={sum(logp.get(p, unk) for p in pieces):.3f}")
                    # lowest -> ['lowest'] score=-2.996
                    # lowestest -> ['lowest', 'est'] score=-5.298
                    # west -> ['west'] score=-2.120
```

`lowest` 的多种切分（`lowest`、`low`+`est`、`l`+`o`+`west`）都在候选里，Viterbi 选概率乘积最大的那条；把 `lowest` 的概率调低一点，结果就会切换到 `['low', 'est']`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/01-文本预处理与分词全流程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Unigram LM：概率模型 + EM + Viterbi」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/01-文本预处理与分词全流程.md)
