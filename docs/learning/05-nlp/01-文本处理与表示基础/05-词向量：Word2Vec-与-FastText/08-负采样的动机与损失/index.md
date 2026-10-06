---
article_id: kp-f26be8c5f7c758ac
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-5865c55f8aa7
learning_sourceId: 5865c55f8aa7
learning_order: 7
learning_objective: 理解并验证：负采样的动机与损失
---

# 负采样的动机与损失

> **学习目标**：能够解释「负采样的动机与损失」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇的 one-hot 与词袋、softmax 与交叉熵、PyTorch `nn.Embedding` 的基本用法。
>
> **所属主题**：词向量：Word2Vec 与 FastText · 方法细节

## 本次只学这一点

对每个训练样本，原 softmax 需要对全部 $V$ 个词求指数并归一化，梯度计算量是 $O(V \cdot N)$。负采样把它替换成**二分类**：

- **正样本**：真实出现的 (中心词, 上下文词) 对，标签 1。
- **负样本**：从噪声分布 $P_n(w)$ 中随机抽 $k$ 个词与中心词配对，标签 0。

单个 (中心词 $w$, 上下文 $c$) 对的损失为

$$
\ell = -\log\sigma(u_o^\top v_c) - \sum_{i=1}^{k} \mathbb{E}_{w_i \sim P_n(w)}\Big[\log\sigma(-u_{w_i}^\top v_c)\Big]
$$

其中 $\sigma$ 是 sigmoid。复杂度从 $O(V)$ 降到 $O(k)$，$k$ 通常取 5–20。

噪声分布不用均匀分布，而用**词频的 3/4 次幂**：

$$
P_n(w) = \frac{\text{count}(w)^{3/4}}{\sum_{w'}\text{count}(w')^{3/4}}
$$

原因是均匀采样会让低频词被抽得太频繁（噪声太大），纯按词频又会让 the/of 这类高频词占满负样本（区分度太低）。3/4 次幂是一个经验上的折中：**抬高低频词的采样概率，同时压低高频词**。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/04-词向量-Word2Vec与FastText.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「负采样的动机与损失」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/04-词向量-Word2Vec与FastText.md)
