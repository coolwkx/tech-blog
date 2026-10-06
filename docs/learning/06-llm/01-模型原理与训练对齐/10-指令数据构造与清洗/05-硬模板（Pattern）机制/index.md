---
article_id: kp-a1bd7e684616a4ce
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-272ce9acf0c8
learning_sourceId: 272ce9acf0c8
learning_order: 4
learning_objective: 理解并验证：硬模板（Pattern）机制
---

# 硬模板（Pattern）机制

> **学习目标**：能够解释「硬模板（Pattern）机制」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT/MLM 预训练目标、Tokenizer 与词表（vocab）、`[MASK]` token 与 MLM Head、交叉熵损失、基本的分类任务指标（acc / P / R / F1）。
>
> **所属主题**：-指令数据构造与清洗 · PET 详解：把分类任务改写成完形填空

## 本次只学这一点

硬模板是**人工写的自然语言字符串**，用大括号标记「插槽」：

```text
这是一条{MASK}评论：{textA}。
```

- `{textA}` 是数据插槽，会被替换为真实评论；
- `{MASK}` 是掩码插槽，会被替换为 `[MASK]`，替换的份数等于标签词的最大 token 长度（中文 BERT 下约 2）。

模板解析的本质是把字符串拆成「字面量片段」与「插槽」两类元素：

```
"这是一条{MASK}评论：{textA}。"
  → inputs_list   = ['这','是','一','条','MASK','评','论','：','textA','。']
  → custom_tokens = {'MASK', 'textA'}
```

拼装时按顺序遍历：是插槽就替换，是字面量就原样拼接。**注意这里有一个容易踩的坑**：解析是按「字符」逐个走的（中文按字，英文按字母），所以模板中不要出现未配对的 `{` 或 `}`。

下面是一个精简但可运行的 `HardTemplate`（依赖：`transformers`、`numpy`，需下载 `bert-base-chinese`）：

```python
# -*- coding: utf-8 -*-
"""硬模板：把分类样本改写成完形填空。依赖：transformers, numpy"""
from typing import Dict, List

import numpy as np


class HardTemplate:
    """人工定义句子与 [MASK] 之间的位置关系。prompt 形如 "这是一条{MASK}评论：{textA}。" """

    def __init__(self, prompt: str):
        self.prompt = prompt
        self.inputs_list: List[str] = []          # 拆解后的片段序列
        self.custom_tokens: set = {"MASK"}        # 解析出的插槽集合
        self._parse()

    def _parse(self) -> None:
        """把模板文字拆成 字面量 / 插槽 交替的片段列表。"""
        idx, n = 0, len(self.prompt)
        while idx < n:
            ch = self.prompt[idx]
            if ch not in "{}":
                self.inputs_list.append(ch)
            if ch == "{":
                idx += 1
                buf = ""
                while idx < n and self.prompt[idx] != "}":
                    buf += self.prompt[idx]
                    idx += 1
                if idx >= n:
                    raise ValueError("缺少与 '{' 配对的 '}'，请检查模板。")
                self.inputs_list.append(buf)
                self.custom_tokens.add(buf)
            elif ch == "}":
                raise ValueError("出现未配对的 '}'，请检查模板。")
            idx += 1

    def __call__(self, inputs_dict: Dict[str, str], tokenizer, mask_length: int,
                 max_seq_len: int = 256) -> Dict[str, list]:
        """把一条样本渲染成 BERT 输入，返回 input_ids 等字段与 mask_position。"""
        pieces = []
        for v in self.inputs_list:
            if v in self.custom_tokens:
                pieces.append(inputs_dict[v] * mask_length if v == "MASK"
                              else inputs_dict[v])
            else:
                pieces.append(v)
        encoded = tokenizer(text="".join(pieces), truncation=True,
                            max_length=max_seq_len, padding="max_length")
        input_ids = encoded["input_ids"]
        mask_id = tokenizer.convert_tokens_to_ids(["[MASK]"])[0]
        return {
            "text": "".join(tokenizer.convert_ids_to_tokens(input_ids)),
            "input_ids": input_ids,
            "token_type_ids": encoded.get("token_type_ids", [0] * len(input_ids)),
            "attention_mask": encoded["attention_mask"],
            "mask_position": np.where(np.array(input_ids) == mask_id)[0].tolist(),
        }
```

> **依赖说明**：`transformers` + `numpy`，模型与分词器需本地已有 `bert-base-chinese` 或可联网下载。本机未安装 `transformers`、无 GPU，因此上述代码只做了语法与逻辑核对，**未实测运行**。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/06-指令数据构造与清洗.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「硬模板（Pattern）机制」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/06-指令数据构造与清洗.md)
