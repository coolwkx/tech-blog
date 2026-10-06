---
article_id: kp-3a67f9591e60abdf
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-5865c55f8aa7
learning_sourceId: 5865c55f8aa7
learning_order: 11
learning_objective: 理解并验证：用 gensim 训练并在小语料上评估
---

# 用 gensim 训练并在小语料上评估

> **学习目标**：能够解释「用 gensim 训练并在小语料上评估」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇的 one-hot 与词袋、softmax 与交叉熵、PyTorch `nn.Embedding` 的基本用法。
>
> **所属主题**：词向量：Word2Vec 与 FastText · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install gensim
from gensim.models import Word2Vec

# 内联小语料（实际项目里换成分词后的大规模句子列表）
sentences = [
 "我 喜欢 自然语言处理".split(),
 "自然语言处理 是 人工智能 的 分支".split(),
 "机器学习 和 深度学习 是 人工智能 的 技术".split(),
 "深度学习 需要 大量 数据 和 算力".split(),
 "词向量 是 自然语言处理 的 基础".split(),
 "我喜欢 机器翻译 和 文本分类".split(),
] * 20 # 小语料重复几次，保证词频足够

model = Word2Vec(
 sentences,
 vector_size=50, # 词向量维度
 window=3, # 上下文窗口
 min_count=1, # 小语料演示用 1；实际项目一般 5
 sg=1, # 1 = Skip-gram，0 = CBOW
 negative=5, # 负采样个数
 epochs=30,
 seed=42,
)

print("词表大小:", len(model.wv))
print("词向量维度:", model.wv["自然语言处理"].shape)
print("与'深度学习'最相近:", [w for w, _ in model.wv.most_similar("深度学习", topn=3)])

# 类比实验：a - b + c，看最近邻
try:
 res = model.wv.most_similar(positive=["人工智能", "数据"], negative=["深度学习"], topn=3)
 print("类比结果:", res)
except KeyError as e:
 print("词表中缺少词:", e)
```

注意 `min_count=1` 只适用于这种演示；真实语料若用 1，会保留大量只出现一次的词，既拖慢训练又几乎学不到有意义的向量。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/04-词向量-Word2Vec与FastText.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「用 gensim 训练并在小语料上评估」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/04-词向量-Word2Vec与FastText.md)
