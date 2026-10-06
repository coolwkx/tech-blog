---
article_id: kp-3ca1f857e3edcf88
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-8b0a9bea9dde
learning_sourceId: 8b0a9bea9dde
learning_order: 4
learning_objective: 理解并验证：三档模型与超参
---

# 三档模型与超参

> **学习目标**：能够解释「三档模型与超参」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇 TF-IDF、第 05 篇文本分类流水线与评估指标、第 09 篇 BERT 微调、第 11 篇情感分析项目的工程范式。
>
> **所属主题**：NLP 项目实战：医疗文本分类 · 方法细节

## 本次只学这一点

**第 1 档：TF-IDF + 随机森林**

```python
self.vectorizer = TfidfVectorizer(
max_features=5000, # 只保留最重要的 5000 个词
token_pattern=r'(?u)\b\w+\b', # 匹配任意词语（中文单字也能保留）
lowercase=False # 中文不需要转小写
)
self.classifier = RandomForestClassifier(
n_estimators=200, # 200 棵树
max_depth=20,
random_state=42,
n_jobs=-1, # 用满 CPU 核心
verbose=1
)
```

随机森林原理：训练时从训练集**有放回抽样** 200 次，每次训一棵树；每棵树学习不同的特征子集。预测时 200 棵树投票，票数最多者胜出。它的最大价值是**可解释性**——`feature_importances_` 直接给出每个词对分类的贡献：

| 排名 | 词语 | 重要性 | 对应类别 |
|------|------|--------|----------|
| 1 | 治疗 | 0.023 | 治疗方法 |
| 2 | 症状 | 0.019 | 临床表现 |
| 3 | 原因 | 0.017 | 病因 |
| 4 | 预防 | 0.015 | 预防 |
| 5 | 检查 | 0.014 | 化验/体检 |
| 6 | 传染 | 0.012 | 传染性 |
| 7 | 手术 | 0.011 | 治疗方法 |
| 8 | 药物 | 0.010 | 治疗方法 |
| 9 | 多久 | 0.009 | 治疗时间 |
| 10 | 科室 | 0.008 | 所属科室 |

这张表极具业务价值：它**验证了模型学到的是「提问方式」而不是「疾病名称」**，与 1.2 节的洞察完全一致。如果排名靠前的词是各种疾病名，反而说明模型走错了方向（可能在利用类别间的病种分布偏差）。

**第 2 档：FastText**

```python
self.model = fasttext.train_supervised(
input=train_file, # 格式: __label__5 肾结石 输尿管 结石 一般 用 药
lr=0.25,
epoch=30,
dim=200,
wordNgrams=2, # bi-gram，部分恢复词序
verbose=2
)
```

超参速查：

| 参数 | 默认值 | 作用 | 调优建议 |
|------|--------|------|----------|
| `lr` | 0.1（分类）/0.05（词向量） | 学习率 | 0.1–1.0，越大越快但可能不稳定 |
| `epoch` | 5 | 训练轮数 | 5–50，越多越好但耗时 |
| `dim` | 100 | 词向量维度 | 100–300 |
| `wordNgrams` | 1 | n-gram 大小 | **1–3，本项目用 2，捕捉局部词序** |
| `loss` | `softmax` | 损失函数 | 类别多时可用 `ova` 或 `hs`（层次 softmax） |
| `minCount` | 1 | 词频阈值 | 医疗小语料建议 2–3，过滤噪声词 |

FastText 的预测流程：

```
文本 → 查找每个词的词向量（子词合成，OOV 也有向量）
 → 求平均得到句子向量
 → logits = softmax(W · sentence_vec + b)
 → argmax 得到类别
```

**第 3 档：BERT 微调**

```python
self.tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
self.model = BertForSequenceClassification.from_pretrained(
'bert-base-chinese',
num_labels=13, # 13 类
output_attentions=False,
output_hidden_states=False
)
```

| 参数 | 值 | 说明 |
|------|-----|------|
| `learning_rate` | 2e-5 ~ 5e-5 | 非常小，微调而非重新训练。项目源码中用的是 5e-5 |
| `weight_decay` | 0.01 | L2 正则，防过拟合 |
| `batch_size` | 16（项目源码用 128） | 显存受限时用 16；数据量小、序列短时可用大 batch |
| `epochs` | 3 | 遍历训练集 3 次（项目源码用 2） |
| `pad_size` / `max_length` | 32 | 医疗问句很短，`pad_size=32` 已足够；BERT 上限为 512 |
| `evaluation_strategy` | `epoch` | 每轮评估一次 |
| `load_best_model_at_end` | `True` | 加载验证集最优的 checkpoint |

> 项目源码（`04-bert/src/models/bert.py` 的 `Config` 类）中实际配置为 `pad_size=32`、`batch_size=128`、`num_epochs=2`、`learning_rate=5e-5`，并用 `_, pooled = self.bert(context, attention_mask=mask, return_dict=False)` 取 `pooled`（即 `[CLS]` 的表示）后接 `nn.Linear(768, num_classes)`——这与上面表格的推荐值属同一量级，差异来自数据规模与显存条件。

`bert-base-chinese` 规格：12 层、12 个注意力头、768 维隐藏层、约 1.1 亿参数。输入格式：

```
[CLS] 肾 结 石 怎 么 治 疗 [SEP] [PAD] [PAD] ...
 ↓
input_ids = [101, 2345, ..., 102, 0, 0, ..., 0] (128 个)
attention_mask = [1, 1, ..., 1, 0, 0, ..., 0] (真实=1, PAD=0)
token_type_ids = [0, 0, ..., 0] (单句任务全为 0)
 ↓
取 [CLS] 位置的向量（768 维）→ 分类层 → Softmax → 13 类概率
```

**为什么必须填充和掩码**：① GPU 并行要求 batch 内所有样本长度一致；② `attention_mask` 告诉模型忽略 PAD，否则填充的 0 会参与注意力计算、污染表示。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/12-NLP项目实战-医疗文本分类.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「三档模型与超参」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/12-NLP项目实战-医疗文本分类.md)
