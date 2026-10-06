---
article_id: kp-1908e751f4bbc82a
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-272ce9acf0c8
learning_sourceId: 272ce9acf0c8
learning_order: 5
learning_objective: 理解并验证：Verbalizer 机制
---

# Verbalizer 机制

> **学习目标**：能够解释「Verbalizer 机制」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT/MLM 预训练目标、Tokenizer 与词表（vocab）、`[MASK]` token 与 MLM Head、交叉熵损失、基本的分类任务指标（acc / P / R / F1）。
>
> **所属主题**：-指令数据构造与清洗 · PET 详解：把分类任务改写成完形填空

## 本次只学这一点

Verbalizer 是「类别 ↔ 词」的双向字典。单类对单词（1 对 1）时它可以退化成一个简单的 dict，但在真实场景里通常是 1 对多：

```text
体育    足球,篮球,网球,棒球,乒乓,体育
水果    苹果,香蕉,橘子,水果
酒店    酒店
```

为什么要 1 对多？看这个例子：

```
"中国爆冷2-1战胜韩国"是一则[MASK][MASK]新闻。
```

如果强制让模型填出 `体育` 这个词，它需要同时学「这讲的是体育」和「要输出『体育』这两个字」。而填 `足球` 更自然——因为 `足球` 在这个上下文里语义更具体、更符合语言模型的先验。**子标签的作用是把「分类决策」降维成「语言直觉」，降低预测难度。**

推理时只可能出现「模型填出来的词既不在主标签里、也不在子标签里」的情况（比如填了 `网球拍`），所以工程上还需要一个兜底策略：按最长公共子串给一个「最像的类别」。

下面给出 Verbalizer 的核心逻辑（依赖：`transformers`）：

```python
# -*- coding: utf-8 -*-
"""标签词映射：类别 <-> 标签词。依赖：transformers"""
from typing import Dict, List, Union


class Verbalizer:
    def __init__(self, verbalizer_file: str, tokenizer, max_label_len: int = 2):
        self.tokenizer = tokenizer
        self.max_label_len = max_label_len
        self.label_dict: Dict[str, List[str]] = self._load(verbalizer_file)
        self.sub2main: Dict[str, str] = {sub: main for main, subs          # 反向索引
                                        in self.label_dict.items() for sub in subs}

    @staticmethod
    def _load(path: str) -> Dict[str, List[str]]:
        """按 '主标签\\t子标签1,子标签2' 的格式读取映射文件。"""
        label_dict: Dict[str, List[str]] = {}
        with open(path, "r", encoding="utf8") as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "\t" not in line:
                    raise ValueError(f"第 {lineno} 行缺少制表符：{line!r}")
                main, subs = line.split("\t", 1)
                label_dict[main] = list(dict.fromkeys(subs.split(",")))
        if not label_dict:
            raise ValueError("verbalizer 文件为空。")
        return label_dict

    def encode_label(self, label: str) -> List[int]:
        """把标签词编码成定长 id 序列（不足补 [PAD]，超出截断）。"""
        ids = self.tokenizer(label)["input_ids"][1:-1]          # 丢掉 [CLS]/[SEP]
        ids = ids[: self.max_label_len]
        return ids + [self.tokenizer.pad_token_id] * (self.max_label_len - len(ids))

    def sub_label_ids(self, label: str) -> List[List[int]]:
        """返回某类别下所有子标签的 id 序列，即「可接受的答案集合」。"""
        if label not in self.label_dict:
            raise ValueError(f"标签 {label!r} 不在映射表中：{list(self.label_dict)}")
        return [self.encode_label(s) for s in self.label_dict[label]]

    @staticmethod
    def _lcs_len(a: str, b: str) -> int:
        """最长公共子串长度，用于兜底匹配。"""
        dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
        best = 0
        for i in range(len(a)):
            for j in range(len(b)):
                if a[i] == b[j]:
                    dp[i + 1][j + 1] = dp[i][j] + 1
                    best = max(best, dp[i + 1][j + 1])
        return best

    def decode_to_main(self, sub_label: Union[str, List[int]],
                       hard_mapping: bool = True) -> str:
        """预测词 -> 主类别；无法精确命中时按最长公共子串兜底。"""
        if isinstance(sub_label, list):
            ids = [i for i in sub_label if i != self.tokenizer.pad_token_id]
            sub_label = "".join(self.tokenizer.convert_ids_to_tokens(ids))
        if sub_label in self.sub2main:
            return self.sub2main[sub_label]
        if not hard_mapping:
            return "未知"
        score = {m: sum(self._lcs_len(sub_label, s) for s in subs)
                 for m, subs in self.label_dict.items()}
        return max(score, key=score.get)
```

**Verbalizer 的三个易错点**：① 标签词可能被切成多个 token，`max_label_len` 必须按最长标签词设置，否则会被静默截断；② 标签词必须落在词表内，否则 `encode_label` 拿到的是 `unk` id；③ 推理时必须有兜底分支，因为模型的预测空间是整个词表，随时可能填出一个不在映射表里的词。

> **依赖说明**：`transformers`（含本地 `bert-base-chinese`）。本机无该依赖，代码经逐行逻辑核对，未实测运行。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/06-指令数据构造与清洗.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Verbalizer 机制」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/06-指令数据构造与清洗.md)
