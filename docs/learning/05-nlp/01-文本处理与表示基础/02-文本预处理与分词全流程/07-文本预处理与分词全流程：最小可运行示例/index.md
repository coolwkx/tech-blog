---
article_id: kp-afdbc8fc53adb49f
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-b5809cd6128d
learning_sourceId: b5809cd6128d
learning_order: 6
learning_objective: 理解并验证：文本预处理与分词全流程：最小可运行示例
---

# 文本预处理与分词全流程：最小可运行示例

> **学习目标**：能够解释「文本预处理与分词全流程：最小可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 字符串与 `re` 模块；正则表达式；神经网络需要整数 id（embedding 查表）；Transformer 的 `attention_mask` 概念。
>
> **所属主题**：文本预处理与分词全流程 · 最小可运行示例

## 本次只学这一点

以下是**只用标准库**的极简 BPE（byte-pair encoding）：训练 + 编码 + 解码，逻辑与 Sennrich 2016 的原始算法一致。

```python
from collections import Counter

END = "</w>" # 词尾标记：让 BPE 区分词内后缀与词尾后缀

def pretokenize(text):
    """按空白预分词，每个词拆成字符序列，词尾补 END。"""
    corpus = Counter
    for word in text.lower.split():
        corpus["".join(word) + "" + END] += 1
        return corpus

    def get_stats(corpus):
        """统计所有相邻符号对的频次（按词频加权）。"""
        stats = Counter
        for symbols, freq in corpus.items():
            syms = symbols.split()
            for a, b in zip(syms, syms[1:]):
                stats[(a, b)] += freq
                return stats

            def merge_pair(corpus, pair):
                """把语料中出现过的 pair 全部合并成新符号。"""
                pattern, repl = "".join(pair), "".join(pair)
                return {symbols.replace(pattern, repl): freq for symbols, freq in corpus.items()}

            def train_bpe(text, num_merges):
                """训练：反复选频次最高的相邻对合并，记录合并顺序。"""
                corpus, merges = pretokenize(text), []
                for _ in range(num_merges):
                    stats = get_stats(corpus)
                    if not stats: # 已合并成整词
                        break
                    pair = max(stats, key=lambda p: (stats[p], p)) # 同分按字典序，保证可复现
                    corpus = merge_pair(corpus, pair)
                    merges.append(pair)
                    return merges

                def encode(word, merges):
                    """编码：按训练顺序，对新词依次套用每条合并规则。"""
                    symbols = list(word.lower()) + [END]
                    for pair in merges:
                        out, i = [], 0
                        while i < len(symbols):
                            if i + 1 < len(symbols) and (symbols[i], symbols[i + 1]) == pair:
                                out.append("".join(pair))
                                i += 2 # 命中就吞掉两个符号
                            else:
                                out.append(symbols[i])
                                i += 1
                                symbols = out
                                return symbols

                            def decode(tokens):
                                return "".join(tokens).replace(END, "").strip()

                            if __name__ == "__main__":
                                corpus_text = "low " * 5 + "lower " * 2 + "newest " * 4 + "widest " * 3 + "new " * 3
                                merges = train_bpe(corpus_text, num_merges=8)
                                for step, (a, b) in enumerate(merges, 1):
                                    print(f"merge {step:2d}: {a!r} + {b!r} -> {a + b!r}")
                                    print("vocab size:", len({c for c in corpus_text.lower() if not c.isspace} | {END}
                                    | {"".join(m) for m in merges}))
                                    for word in ["lowest", "newest", "widest", "slow"]:
                                        toks = encode(word, merges)
                                        print(f"encode({word!r}) = {toks} decode -> {decode(toks)!r}")
```

实际运行输出（Python 3.12，纯标准库）：

```text
merge 1: 'w' + '</w>' -> 'w</w>'
merge 2: 't' + '</w>' -> 't</w>'
merge 3: 's' + 't</w>' -> 'st</w>'
merge 4: 'n' + 'e' -> 'ne'
merge 5: 'l' + 'o' -> 'lo'
merge 6: 'e' + 'st</w>' -> 'est</w>'
merge 7: 'lo' + 'w</w>' -> 'low</w>'
merge 8: 'w' + 'est</w>' -> 'west</w>'
vocab size: 19
encode('lowest') = ['lo', 'west</w>'] decode -> 'lowest'
encode('newest') = ['ne', 'west</w>'] decode -> 'newest'
encode('widest') = ['w', 'i', 'd', 'est</w>'] decode -> 'widest'
encode('slow') = ['s', 'low</w>'] decode -> 'slow'
```

**逐行说明**：

| 代码 | 作用 | 容易误解的点 |
| --- | --- | --- |
| `END = "</w>"` | 词尾标记 | 没有它 `est` 无法区分词尾（`newest`）与词中；GPT-2 用 `Ġ` 表示词首空格，思路相同 |
| `pretokenize` | 统计词频并把词拆成字符 | 生产环境要先归一化，否则 `Café` 与 `cafe\u0301` 会变成两条记录 |
| `get_stats` | 统计相邻符号对频次 | 频次要**按词频加权**，不是按出现次数 |
| `merge_pair` | 用 `str.replace` 全局替换 | 符号内部不含空格，所以 `"a b"` 只会匹配两个相邻的完整符号，不会误伤 |
| `max(stats, key=...)` | 取频次最高的对 | 频次为整数，同分时顺序不定；加 `(stats[p], p)` 做二级排序才可复现 |
| `merges.append(pair)` | 保存合并顺序 | **合并顺序既是词表 id 的生成顺序，也是编码时的套用顺序**，丢了就无法复现 |
| `encode` 外层 `for pair` | 按训练顺序套用规则 | 不是「重跑训练」，只用有序的 merges 列表；未登录字符自然退化为单字符 |
| `decode` | 拼回字符串 | `</w>` 换回空格即近似无损；真实 tokenizer 用 metaspiece `▁` 保证严格可逆 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/01-文本预处理与分词全流程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「文本预处理与分词全流程：最小可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/01-文本预处理与分词全流程.md)
