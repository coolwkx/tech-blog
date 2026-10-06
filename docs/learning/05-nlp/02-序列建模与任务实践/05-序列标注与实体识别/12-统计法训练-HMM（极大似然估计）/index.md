---
article_id: kp-e6e335594ff72627
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-00dabbf9e8f9
learning_sourceId: 00dabbf9e8f9
learning_order: 11
learning_objective: 理解并验证：统计法训练 HMM（极大似然估计）
---

# 统计法训练 HMM（极大似然估计）

> **学习目标**：能够解释「统计法训练 HMM（极大似然估计）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 01 篇的词性标注与 NER 两阶段拆解、概率论基础（条件概率、贝叶斯）、softmax 与交叉熵。
>
> **所属主题**：序列标注与实体识别 · 可运行示例

## 本次只学这一点

```python
from collections import defaultdict

# 内联小训练集：(观测序列, 隐状态序列)
train = [
(["人生", "该", "如何", "起头"], ["n", "r", "r", "v"]),
(["猫", "吃", "鱼"], ["n", "v", "n"]),
(["我", "爱", "北京"], ["r", "v", "n"]),
]

states = sorted({s for _, ys in train for s in ys})
pi_c, A_c, B_c = defaultdict(float), defaultdict(float), defaultdict(float)

for xs, ys in train:
    pi_c[ys[0]] += 1
    for t, (x, y) in enumerate(zip(xs, ys)):
        B_c[(y, x)] += 1
        if t > 0:
            A_c[(ys[t - 1], y)] += 1

            # 归一化（加 1 平滑，避免未见转移概率为 0）
            K = len(states)

            def norm(counts, cond_key, denom_key):
                return {
            k: (v + 1.0) / (sum(vv for kk, vv in counts.items() if cond_key(kk) == cond_key(k)) + K)
            for k, v in counts.items()
            }

            pi = {s: (pi_c[s] + 1.0) / (len(train) + K) for s in states}
            A = {(i, j): (A_c[(i, j)] + 1.0) / (sum(A_c[(i, jj)] for jj in states) + K)
            for i in states for j in states}
            B = {(j, x): (B_c[(j, x)] + 1.0) / (sum(B_c[(j, xx)] for xx in {xx for _, xs in train for xx in xs}) + 1)
            for j in states for x in {xx for _, xs in train for xx in xs}}

            print("初始概率 pi:", {k: round(v, 3) for k, v in pi.items()})
            print("转移概率示例 A[n->v] =", round(A[("n", "v")], 3))
            print("发射概率示例 B[v][吃] =", round(B[("v", "吃")], 3))
```

关键点：**有标注的 HMM 训练就是数频次**，不需要梯度下降，这也是它当年流行的原因——训练成本几乎为零。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/06-序列标注与实体识别.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「统计法训练 HMM（极大似然估计）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/06-序列标注与实体识别.md)
