---
article_id: kp-dce681ca65fa94b4
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-5865c55f8aa7
learning_sourceId: 5865c55f8aa7
learning_order: 12
learning_objective: 理解并验证：纯 numpy 实现负采样损失与梯度（看清数学）
---

# 纯 numpy 实现负采样损失与梯度（看清数学）

> **学习目标**：能够解释「纯 numpy 实现负采样损失与梯度（看清数学）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇的 one-hot 与词袋、softmax 与交叉熵、PyTorch `nn.Embedding` 的基本用法。
>
> **所属主题**：词向量：Word2Vec 与 FastText · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install numpy
import numpy as np

np.random.seed(0)

V, N, k = 8, 4, 3 # 词表大小、向量维度、负样本数
W_in = np.random.randn(V, N) * 0.1 # 输入矩阵（词向量表）
W_out = np.random.randn(N, V) * 0.1 # 输出矩阵

center, context = 0, 1
negatives = [3, 5, 6] # 简化：直接给定负样本

def sigmoid(x):
 return 1.0 / (1.0 + np.exp(-x))

v_c = W_in[center] # 中心词向量
loss, grads = 0.0, {}

def step(target, label):
 """对单个 (中心词, 目标词) 对做一次二分类的前向与梯度"""
 global loss
 u = W_out[:, target]
 score = float(v_c @ u)
 p = sigmoid(score)
 # 交叉熵: label=1 -> -log(p); label=0 -> -log(1-p)
 loss += -(np.log(p) if label == 1 else np.log(1 - p))
 grads[target] = ((p - label) * u, (p - label) * v_c) # (dv_c 的贡献, dW_out[:, target])

step(context, 1) # 正样本
for n in negatives:
 step(n, 0) # k 个负样本

# 汇总梯度并做一次梯度下降
dv_c = sum(g[0] for g in grads.values())
lr = 0.1
W_in[center] -= lr * dv_c
for target, (_, dwo) in grads.items():
 W_out[:, target] -= lr * dwo

print(f"负采样总损失: {loss:.4f}")
print(f"中心词向量更新量范数: {np.linalg.norm(lr * dv_c):.4f}")
print(f"复现检查: 复杂度 = O(k+1) = {k + 1} 次点积，而非 O(V) = {V}")
```

这个例子把「$V$ 分类 → $k+1$ 个二分类」的等价性摊开：正样本把中心词向量往上下文词方向拉，负样本把它推离噪声词。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/04-词向量-Word2Vec与FastText.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「纯 numpy 实现负采样损失与梯度（看清数学）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/04-词向量-Word2Vec与FastText.md)
