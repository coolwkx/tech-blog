---
article_id: kp-3856a0d118e4ced6
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-8f6e59312d25
learning_sourceId: 8f6e59312d25
learning_order: 7
learning_objective: 理解并验证：数据预处理：三条支线的关键代码
---

# 数据预处理：三条支线的关键代码

> **学习目标**：能够解释「数据预处理：三条支线的关键代码」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：TF-IDF 与词袋模型、jieba 分词、`sklearn` 的 `TfidfVectorizer` / `RandomForestClassifier`、PyTorch 训练循环、BERT 的 `[CLS]` 与 attention mask。
>
> **所属主题**：项目实战笔记 08：新闻文本分类三方案对比（随机森林 / FastText / BERT） · 核心实现

## 本次只学这一点

```python
# 线一：随机森林（analysis.py 精简）——统计 + jieba 分词 + 存 csv
content = pd.read_csv('./data/data/train.txt', sep='\t')
count = Counter(content.label.values())
content['sentence_len'] = content['sentence'].apply(len)
length_mean, length_std = np.mean(content['sentence_len']), np.std(content['sentence_len'])

def cut_sentence(s): return list(jieba.cut(s))
content['words'] = content['sentence'].apply(lambda s: ' '.join(cut_sentence(s)))
content['words'] = content['words'].apply(lambda s: ' '.join(s.split())[:30])
content.to_csv('./data/data/train_new.csv')
```

```python
# 线二：FastText（preprocess.py 精简）——转成 __label__ 格式
id_to_label = {}
with open('class.txt', 'r', encoding='utf-8') as f1:
    for idx, line in enumerate(f1.readlines()):
        id_to_label[idx] = line.strip()

        train_data = []
        with open('train.txt', 'r', encoding='utf-8') as f2:
            for line in f2.readlines():
                sentence, label = line.strip.split('\t')
                new_label = '__label__' + id_to_label[int(label)]
                sent_char = ' '.join(list(sentence)) # 按字（preprocess1.py 用 jieba.lcut 按词）
                train_data.append(new_label + ' ' + sent_char)
```

```python
# 线三：BERT（utils.build_dataset 精简）
def load_dataset(path, pad_size=32):
    contents = []
    with open(path, "r", encoding="UTF-8") as f:
        for line in tqdm(f):
            lin = line.strip()
            if not lin: continue
            content, label = lin.split("\t")
            token = config.tokenizer.tokenize(content) # ★ 用 BERT 自己的 tokenizer
            token = [CLS] + token
            seq_len = len(token)
            token_ids = config.tokenizer.convert_tokens_to_ids(token)
            if pad_size:
                if len(token) < pad_size:
                    mask = [1] * len(token_ids) + [0] * (pad_size - len(token))
                    token_ids += [0] * (pad_size - len(token))
                else:
                    mask = [1] * pad_size
                    token_ids, seq_len = token_ids[:pad_size], pad_size
                    contents.append((token_ids, int(label), seq_len, mask))
                    return contents
```

**三处值得单独指出的细节**：

1. **`' '.join(s.split())[:30]` 截的是字符不是词**。它先拼成字符串再 `[:30]`，实际约保留 10-15 个词。本项目平均 19 字、几乎不触发截断所以无害，但长文本场景下会截出半截词。**更明确的写法是 `words[:30]`。**
2. **FastText 的格式是硬要求**：每行一个文档、类别以 `__label__` 前缀放在最前、多标签用多个前缀空格分隔。**标签放在中间或末尾都不兼容**——FastText 会把非 `__label__` 开头的词全当文本内容。
3. **`mask` 和 `token_ids` 的长度各自计算，依赖"两者恰好人相等"的隐含假设**（`len(token_ids)` vs `len(token)`）。中文 BERT 是字级一对一映射所以没触发，但这是一个脆弱设计。**多个数组要 pad 到同一长度时，必须基于同一个长度变量推导**：

```python
seq_len = min(len(token_ids), pad_size)
mask = [1] * seq_len + [0] * (pad_size - seq_len)
token_ids = token_ids[:pad_size] + [0] * max(0, pad_size - len(token_ids))
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/03-文本分类系统/08-项目-新闻文本分类三方案对比（随机森林FastTextBERT）.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「数据预处理：三条支线的关键代码」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/03-文本分类系统/08-项目-新闻文本分类三方案对比（随机森林FastTextBERT）.md)
