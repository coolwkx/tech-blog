---
article_id: kp-78bf35b82696f9a2
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-b5809cd6128d
learning_sourceId: b5809cd6128d
learning_order: 8
learning_objective: 理解并验证：WordPiece：用似然替代频次
---

# WordPiece：用似然替代频次

> **学习目标**：能够解释「WordPiece：用似然替代频次」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 字符串与 `re` 模块；正则表达式；神经网络需要整数 id（embedding 查表）；Transformer 的 `attention_mask` 概念。
>
> **所属主题**：文本预处理与分词全流程 · 深入机制

## 本次只学这一点

WordPiece 由 Google 在 NMT 中提出（Wu et al. 2016），BERT 用的就是它。与 BPE 有两点差异。

**差异一：合并准则不是频次，而是似然提升**，实现上为打分函数 `score(a, b) = freq(ab) / (freq(a) * freq(b))`，选得分最高的一对合并。直觉：`freq(ab)` 大说明常见，`freq(a) * freq(b)` 大说明 a、b 各自本来就常见（合并收益低）。这个比值接近互信息，所以 WordPiece 更愿意合并「共同出现但各自并不常见」的片段（如 `qu`、`##ing`），而 BPE 会先把 `e`、`s` 这种高频字符组掉。

**差异二：词内前缀 `##`** 标记「该子词不是词首」。**推理时是贪心最长匹配**（不是 BPE 的按序合并）：从词首开始找词表里存在的最长子串；一个都匹配不上就整个词输出 `[UNK]`。

```python
def wordpiece(word, vocab, max_len=20):
    """vocab 里的续接子词自带 '##' 前缀，查表时必须补上前缀。"""
    tokens, start = [], 0
    while start < len(word):
        end, hit = min(len(word), start + max_len), None
        while start < end: # 从最长往最短试
            piece = word[start:end]
            key = piece if start == 0 else "##" + piece
            if key in vocab:
                hit, break_end = key, end
                break
            end -= 1
        else:
            tokens.append("[UNK]") # 一个子词都匹配不上
            break
        tokens.append(hit)
        start = break_end
        return tokens

    vocab = {"un", "##want", "##ed", "play", "##ing", "low", "##est", "##er", "new"}
    for w in ["unwanted", "playing", "lowest", "lower", "xyzzy"]:
        print(f"{w:10} -> {wordpiece(w, vocab)}")
        # unwanted -> ['un', '##want', '##ed'] playing -> ['play', '##ing']
        # lowest -> ['low', '##est'] lower -> ['low', '##er']
        # xyzzy -> ['[UNK]'] 词表外整词兜底
```

坑点：**查表要带 `##` 前缀**。只比较 `word[start:end]` 而不补前缀，`lowest` 会被切成 `low` + `[UNK]` —— 这个 bug 极其常见，且只在小的玩具词表上才会暴露。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/01-文本预处理与分词全流程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「WordPiece：用似然替代频次」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/01-文本预处理与分词全流程.md)
