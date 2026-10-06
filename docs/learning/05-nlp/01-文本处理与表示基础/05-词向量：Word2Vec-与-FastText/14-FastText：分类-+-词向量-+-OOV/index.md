---
article_id: kp-f2ce5b27e95d9213
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-5865c55f8aa7
learning_sourceId: 5865c55f8aa7
learning_order: 13
learning_objective: 理解并验证：FastText：分类 + 词向量 + OOV
---

# FastText：分类 + 词向量 + OOV

> **学习目标**：能够解释「FastText：分类 + 词向量 + OOV」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇的 one-hot 与词袋、softmax 与交叉熵、PyTorch `nn.Embedding` 的基本用法。
>
> **所属主题**：词向量：Word2Vec 与 FastText · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install fasttext （若不成功可尝试 pip install fasttext-wheel）
import os
import tempfile
import fasttext

workdir = tempfile.mkdtemp

# FastText 分类要求每行「__label__类别 文本」
train_path = os.path.join(workdir, "train.txt")
with open(train_path, "w", encoding="utf-8") as f:
    for text, label in [
    ("肾结石 一般 用 什么 药", "治疗"),
    ("胆结石 怎么 治疗 效果好", "治疗"),
    ("心肌梗死 症状 是 什么", "症状"),
    ("脑梗死 表现 有哪些", "症状"),
    ("如何 预防 糖尿病", "预防"),
    ("怎么 预防 高血压", "预防"),
    ] * 20:
        f.write(f"__label__{label} {text}\n")

        model = fasttext.train_supervised(
        input=train_path,
        lr=0.5,
        epoch=25,
        dim=100,
        wordNgrams=2, # 加 bi-gram，部分恢复词序
        loss="softmax", # 多分类用 softmax；类别极多时可用 'ova' 或 'hs'
        verbose=0,
        )
        model.save_model(os.path.join(workdir, "cls.bin"))

        # 测试集：故意用训练集里没出现过的词「尿结石」
        test_path = os.path.join(workdir, "test.txt")
        with open(test_path, "w", encoding="utf-8") as f:
            f.write("__label__治疗 尿结石 用 什么 药\n")
            f.write("__label__症状 心梗 的 表现\n")

            n, precision, recall = model.test(test_path)
            print(f"样本数={n} 准确率={precision:.4f} 召回率={recall:.4f}")

            labels, probs = model.predict("尿 结石 用 什么 药", k=2)
            print("预测标签:", labels, "概率:", probs)
            print("OOV 演示 —— '尿结石' 的向量（子词拼出来）:", model.get_word_vector("尿结石").shape)

            # 还可以用 FastText 无监督训练词向量（相当于原版 word2vec）
            unsup_path = os.path.join(workdir, "unsup.txt")
            with open(unsup_path, "w", encoding="utf-8") as f:
                for s in ["猫 喜欢 鱼", "狗 喜欢 骨头", "猫 和 狗 都 是 宠物"] * 50:
                    f.write(s + "\n")
                    vec_model = fasttext.train_unsupervised(unsup_path, model="skipgram", dim=50, epoch=20, verbose=0)
                    print("'猫' 的最近邻:", vec_model.get_nearest_neighbors("猫"))
```

`get_word_vector("尿结石")` 能正常返回向量，正是因为 FastText 用子词合成，而不是查一张固定的词表。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/04-词向量-Word2Vec与FastText.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「FastText：分类 + 词向量 + OOV」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/04-词向量-Word2Vec与FastText.md)
