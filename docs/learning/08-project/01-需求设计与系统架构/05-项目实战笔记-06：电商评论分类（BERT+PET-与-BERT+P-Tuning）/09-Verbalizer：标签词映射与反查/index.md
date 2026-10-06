---
article_id: kp-58da100aa1e3c085
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-314d719df758
learning_sourceId: 314d719df758
learning_order: 9
learning_objective: 理解并验证：Verbalizer：标签词映射与反查
---

# Verbalizer：标签词映射与反查

> **学习目标**：能够解释「Verbalizer：标签词映射与反查」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT 与 MLM（掩码语言模型）预训练目标、`[MASK]` token 的语义、`AutoModelForMaskedLM` 与 `AutoTokenizer`、HuggingFace `datasets.map(batched=True)`、PyTorch 训练循环与 `CrossEntropyLoss`。
>
> **所属主题**：项目实战笔记 06：电商评论分类（BERT+PET 与 BERT+P-Tuning） · 核心实现

## 本次只学这一点

```python
class Verbalizer(object):
    """将一个 Label 对应到其子 Label 的映射。"""

    def load_label_dict(self, verbalizer_file):
        """'水果\t苹果,香蕉,橘子' -> {'水果': ['苹果','香蕉','橘子'], ...}"""
        label_dict = {}
        with open(verbalizer_file, 'r', encoding='utf8') as f:
            for line in f.readlines():
                label, sub_labels = line.strip.split('\t')
                label_dict[label] = list(set(sub_labels.split(',')))
                return label_dict

            def find_sub_labels(self, label):
                """主标签 -> 所有子标签的 token_ids（训练时构造软目标）"""
                if type(label) == list: # 传入是 id 列表，先转文字
                    while self.tokenizer.pad_token_id in label:
                        label.remove(self.tokenizer.pad_token_id)
                        label = ''.join(self.tokenizer.convert_ids_to_tokens(label))
                        if label not in self.label_dict:
                            raise ValueError(f'Label Error: "{label}" not in label_dict.')

                        sub_labels = self.label_dict[label]
                        # tokenizer(sub_labels) 会给每个词加 [CLS]/[SEP]，用 [1:-1] 剥掉
                        token_ids = [_id[1:-1] for _id in self.tokenizer(sub_labels)['input_ids']]
                        for i in range(len(token_ids)):
                            token_ids[i] = token_ids[i][:self.max_label_len] # 截断
                            if len(token_ids[i]) < self.max_label_len: # 补齐
                                token_ids[i] += [self.tokenizer.pad_token_id] * (self.max_label_len - len(token_ids[i]))
                                return {'sub_labels': sub_labels, 'token_ids': token_ids}
```

反查主标签（先精确命中，未命中则走 `hard_mapping` 兜底）：

```python
def find_main_label(self, sub_label, hard_mapping=True):
    """'苹果' -> {'label': '水果', 'token_ids': [3717, 3362]}"""
    if type(sub_label) == list: # 传入是 id 列表：去 [PAD] 后转文字
        while self.tokenizer.pad_token_id in sub_label:
            sub_label.remove(self.tokenizer.pad_token_id)
            sub_label = ''.join(self.tokenizer.convert_ids_to_tokens(sub_label))

            main_label = '无'
            for label, s_labels in self.label_dict.items():
                if sub_label in s_labels: # ① 精确命中子标签
                    main_label = label
                    break
                if main_label == '无' and hard_mapping: # ② 兜底：最长公共子串模糊匹配
                    main_label = self.hard_mapping(sub_label)
                    return {'label': main_label,
                'token_ids': self.tokenizer(main_label)['input_ids'][1:-1]}

                def hard_mapping(self, sub_label):
                    """DP 求最长公共子串长度，累加与全部子标签的重合度，取总分最大的主标签"""
                    label, max_overlap = '', 0
                    for main_label, sub_labels in self.label_dict.items():
                        overlap = sum(self.get_common_sub_str(sub_label, s)[1] for s in sub_labels)
                        if overlap >= max_overlap:
                            max_overlap, label = overlap, main_label
                            return label
```

`get_common_sub_str` 是最长公共子串的标准 DP（`record[i+1][j+1] = record[i][j] + 1`），实现从略。

**为什么必须要 `hard_mapping`**：模型的输出空间是整个 21128 词的词表。即使 Prompt 引导它输出"水果类"的词，也可能输出"苹果好吃""红色的"这种表里没有的东西。没有兜底就会 `KeyError` 或返回"无"。有了最长公共子串匹配，"苹果好吃"与"苹果"共享 2 个字符，从而正确归到"水果"。

**代价是它可能强行映射错误的东西**——这是双刃剑。生产环境应加**重合度阈值**，低于阈值返回"无法判定"，而不是硬猜。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/03-文本分类系统/06-项目-电商评论分类（BERT+PET与P-Tuning）.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Verbalizer：标签词映射与反查」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/03-文本分类系统/06-项目-电商评论分类（BERT+PET与P-Tuning）.md)
