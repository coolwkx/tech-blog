---
article_id: kp-b0fa10ba93d3c804
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-3a66bd7ad2f1
learning_sourceId: 3a66bd7ad2f1
learning_order: 12
learning_objective: 理解并验证：纯 Python 实现 mini-BPE
---

# 纯 Python 实现 mini-BPE

> **学习目标**：能够解释「纯 Python 实现 mini-BPE」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 01 篇的文本预处理流水线、序列标注的基本概念、Python 正则与字典操作。
>
> **所属主题**：中文分词与子词分词 · 可运行示例

## 本次只学这一点

```python
from collections import Counter

CORPUS = {"low": 5, "lower": 2, "newest": 6, "widest": 3}

def get_vocab(corpus):
    """把每个词拆成字符序列，词尾加 </w> 标记"""
    return {"".join(list(w)) + " </w>": c for w, c in corpus.items()}

def get_stats(vocab):
    """统计所有相邻符号对的频次（按词频加权）"""
    pairs = Counter
    for word, freq in vocab.items():
        symbols = word.split()
        for i in range(len(symbols) - 1):
            pairs[(symbols[i], symbols[i + 1])] += freq
            return pairs

        def merge_vocab(pair, vocab):
            """把 best pair 在所有词中合并成一个新符号"""
            merged, new_token = {}, "".join(pair)
            for word, freq in vocab.items():
                merged[word.replace("".join(pair), new_token)] = freq
                return merged

            def train_bpe(corpus, num_merges=8):
                vocab = get_vocab(corpus)
                merges = []
                for i in range(num_merges):
                    pairs = get_stats(vocab)
                    if not pairs:
                        break
                    best = max(pairs, key=pairs.get)
                    vocab = merge_vocab(best, vocab)
                    merges.append((best, pairs[best]))
                    print(f"第{i + 1}轮: 合并 {best} -> {''.join(best)!r} (频次 {pairs[best]})")
                    return merges, vocab

                def encode(word, merges):
                    """用学到的合并表编码新词：按轮次优先级反复合并"""
                    symbols = list(word) + ["</w>"]
                    for pair, _ in merges:
                        i = 0
                        while i < len(symbols) - 1:
                            if (symbols[i], symbols[i + 1]) == pair:
                                symbols[i:i + 2] = ["".join(pair)]
                            else:
                                i += 1
                                return symbols

                            merges, final_vocab = train_bpe(CORPUS, num_merges=8)
                            print("\n最终词表:", sorted(final_vocab))
                            for w in ["lowest", "newest", "slow"]:
                                print(f"编码 {w!r} -> {encode(w, merges)}")
```

预期现象：前几轮会依次合并 `('e','s')`、`('es','t')`、`('est','</w>')`、`('l','o')`、`('lo','w')` 等；`lowest` 能被切出已知子词，`slow` 这类未见词会退化成 `['s','low','</w>']` 之类的碎片组合——这正是子词方法「永不 OOV」的体现。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/02-中文分词与子词分词.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「纯 Python 实现 mini-BPE」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/02-中文分词与子词分词.md)
