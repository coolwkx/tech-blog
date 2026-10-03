# BERT 与预训练模型

> **一句话总结**：BERT 用「双向 Transformer Encoder + MLM/NSP 自监督预训练」学到了通用语言表示，下游任务只需加一个轻量头再微调。
> **前置知识**：第 08 篇的 Transformer Encoder 与 self-attention、第 04 篇的静态词向量局限、Python 类与 PyTorch 训练循环。

> 1. 说清 Encoder-Only / Decoder-Only / Encoder-Decoder 三条技术路线的差别与代表模型。
> 2. 解释 BERT 的三个 Embedding、两大预训练任务，以及 MLM 为什么用 80%/10%/10%。
> 3. 用 `pipeline` / `AutoModel` / 自定义下游模型三种方式调用中文 BERT 完成分类任务。

## 1. 核心概念

### 1.1 迁移学习与预训练模型

**预训练模型**：别人在大规模语料上训练好的模型。它通常具备复杂的网络结构，并且已经在海量数据上学到了通用的语言规律。

**微调（fine-tuning）**：在预训练模型后面接一个自定义网络，用垂直领域数据继续训练。参数更新有三种策略：

| 策略 | 做法 | 适用 |
|------|------|------|
| 全部微调 | 预训练模型 + 自定义网络的参数都更新 | 下游数据充足、领域差异大 |
| 部分微调 | 冻结底层、只训练高层 + 自定义头 | 数据中等，兼顾效果与成本 |
| 不微调（冻结） | 把预训练模型当特征提取器，`requires_grad=False` | 数据很少（几百条），避免过拟合 |

**迁移学习的两种方式**：

| 方式 | 说明 | 例子 |
|------|------|------|
| 开箱即用 | 预训练任务与目标任务相似时直接调用 | 用情感分析模型直接判评论正负 |
| 微调 | 加自定义网络，用领域数据继续训练 | 用 `bert-base-chinese` 做医疗 13 分类 |

### 1.2 三条技术路线

现在主流的预训练语言模型基本都是基于 Transformer 迭代而来，按用了 Transformer 的哪一部分来划分：

| 路线 | 结构 | 代表模型 | 语言模型方向 | 擅长 |
|------|------|----------|-------------|------|
| Encoder-Only | 只用编码器 | BERT、RoBERTa、ALBERT、MacBERT | 双向（同时看左右上下文） | 理解类任务：分类、NER、抽取式问答 |
| Decoder-Only | 只用解码器 | GPT、GPT-2、GPT-3 | 单向（只看左侧上下文） | 生成类任务：续写、对话、代码生成 |
| Encoder-Decoder | 完整 Transformer | T5、BART | 编码双向 + 解码单向 | 序列到序列：翻译、摘要、生成式问答 |

一句话判断路线：**看它擅长理解还是生成**。理解类任务用 Encoder-Only，生成类任务用 Decoder-Only，输入输出都是序列且不等长用 Encoder-Decoder。

### 1.3 BERT 的宏观结构

BERT（Bidirectional Encoder Representations from Transformers）是 2018 年 10 月 Google AI 提出的预训练模型，全称即「来自 Transformer 的双向编码器表示」。它在 SQuAD 1.1 上两个指标全面超越人类，把 GLUE 基准推高到 80.4%（绝对提升 7.6%），是 NLP 发展史上的里程碑。

BERT 宏观上分三个模块：

| 模块 | 内容 | 作用 |
|------|------|------|
| Embedding 模块 | Token + Segment + Position 三种 Embedding **直接相加** | 把 token 变成含位置与句段信息的向量 |
| 双向 Transformer 模块 | 只保留 Transformer 的 Encoder，完全舍弃 Decoder | 提取双向上下文特征 |
| 预微调模块 | 按任务加不同的输出头 | 分类取 `[CLS]`、NER 取每个 token、问答取 span |

三种 Embedding 的细节：

| Embedding | 作用 | 与经典 Transformer 的差异 |
|-----------|------|--------------------------|
| Token Embeddings | 词嵌入，第一个 token 是 `[CLS]` | 中文 BERT 是**字级** |
| Segment Embeddings | 区分句子 A / 句子 B | 服务 NSP 这类句对任务；单句任务全为 0 |
| Position Embeddings | 位置信息 | **不是三角函数固定编码，而是学习出来的** |

> 最后一个差异常被忽略：经典 Transformer 用 sin/cos 公式算位置编码，BERT 把位置编码当成可学习参数。代价是最大长度被固定（512），好处是位置表示更贴合数据。

### 1.4 常见 BERT 变体规格

| 模型 | 层数 | 隐藏维度 | 注意力头 | 参数量 | 说明 |
|------|------|----------|----------|--------|------|
| `bert-base-uncased` | 12 | 768 | 12 | 110M | 小写英文 |
| `bert-large-uncased` | 24 | 1024 | 16 | 340M | 小写英文 |
| `bert-base-cased` | 12 | 768 | 12 | 110M | 区分大小写 |
| `bert-base-multilingual-uncased` | 12 | 768 | 12 | 110M | 102 种语言 |
| `bert-base-chinese` | 12 | 768 | 12 | 110M | 简体 + 繁体中文（字级） |

出现的其他主流模型：GPT、GPT-2、Transformer-XL、XLNet、XLM、RoBERTa、DistilBERT、ALBERT、T5、XLM-RoBERTa。

### 1.5 BERT 的优缺点

| 优点 | 缺点 |
|------|------|
| 预训练 + 微调在 11 项 NLP 任务上取得最优结果 | 模型庞大（110M 起），不利于资源紧张场景与实时上线 |
| 基于 Transformer，比 RNN 高效，可并行且能捕捉长距离依赖 | 中文模型是**字级** token，很多需要词向量的应用无法直接使用；生僻词只能以 `UNK` 代替 |
| 真正的双向上下文，为下游微调留出足够空间 | MLM 的 `[MASK]` 只在训练出现，预测时不出现，存在信息偏差（exposure bias） |
| — | 每个 batch 只有 15% 的 token 参与训练，**收敛比 left-to-right 模型慢很多** |

## 2. 方法细节

### 2.1 预训练任务一：Masked LM（MLM）

传统语言模型是 left-to-right（或左右拼接），提取特征能力有限。BERT 提出深度双向表示，用 MASK 任务训练：

1. 在原始文本中**随机抽取 15% 的 token** 作为预测对象；
2. 在这些被选中的 token 中，按三种方式生成输入：
 - **80%** 概率替换为 `[MASK]`：`my dog is hairy` → `my dog is [MASK]`
 - **10%** 概率替换为一个随机词：`my dog is hairy` → `my dog is apple`
 - **10%** 概率保持不变：`my dog is hairy` → `my dog is hairy`
3. 模型在**不知道哪些位置被改过、哪些是原词**的情况下预测原词，被迫学习分布式上下文语义。

**为什么是 80/10/10**（三条理由要能背）：

| 比例 | 作用 |
|------|------|
| 若 100% 用 `[MASK]` | 微调时不存在 `[MASK]`，模型从未接触过这些 token 本身的信息，整个语义空间损失部分信息 |
| 10% 随机词 | 防止模型「偷懒」直接照抄当前 token；逼它学习周边语义与远距离依赖 |
| 10% 保留原词 | 保留语言本来的面貌，让信息不至于被完全遮掩，模型能「看清」真实语言 |

同时因为原文本中只有 15% 的 token 参与 MASK，并不会破坏原语言的表达能力和语言规则。

### 2.2 预训练任务二：Next Sentence Prediction（NSP）

QA、NLI 这类任务需要理解**两个句子之间的关系**，因此 BERT 引入 NSP：输入句子对 (A, B)，预测 B 是否是 A 的真实下一句。

- 所有语句都被选作句子 A；
- 50% 的 B 是原文中真实跟随 A 的下一句（`IsNext`，正样本）；
- 50% 的 B 是从原文随机抽取的一句（`NotNext`，负样本）；
- 该任务在上测试集能取得 97%–98% 的准确率。

**后续反思**（重要，面试常问）：NSP 后来被广泛质疑「太简单」。RoBERTa 直接取消 NSP；ALBERT 用 SOP（Sentence Order Prediction，把 `[A,B]` 作为正样本、`[B,A]` 作为负样本）替代。原因是「随机句 vs 下一句」往往主题就完全不同，模型靠主题匹配就能答对，学不到真正的语序/连贯性知识。

### 2.3 BERT 处理长文本

BERT 预训练时接收的最大序列长度是 **512**。超长文本需要特殊截断策略：

| 策略 | 做法 | 适用 |
|------|------|------|
| head-only | 只保留前 510 个 token（留 2 个位置给 `[CLS]` 和 `[SEP]`） | 关键信息在开头（新闻导语） |
| tail-only | 只保留最后 510 个 token | 关键信息在结尾（结论、判决书尾部） |
| head+tail | 文本 ≤ 800 时取前 128 + 后 382；> 800 时取前 256 + 后 254 | 关键信息两端都有（长评论、病历） |

工程上还有两条路：**分块（chunking）** 后对多块结果聚合（投票/求平均），或改用 Longformer / BigBird 这类支持长序列的稀疏注意力模型。

### 2.4 BERT 家族的主要改进

| 模型 | 改进点 | 关键细节 |
|------|--------|----------|
| **ALBERT** | ① 词嵌入参数因式分解 ② 隐藏层参数共享 ③ 去掉 NSP 换 SOP ④ 去掉 dropout ⑤ MLM 任务优化 | 嵌入参数量从 $30000\times768\approx2300$ 万降到 $30000\times128+128\times768\approx48$ 万；Block 参数量降至 BERT 的 1/12 或 1/24；90% 的 steps 用长度 512 的长句（BERT 是 90% 用 128 短句）；预测 N-gram 片段而非单个 token。`albert-tiny` 仅 4 层、1.8M 参数，训练与推理提速约 10 倍，LCQMC 相似度测试达 85.4%（比 bert-base 仅低 1.5%） |
| **RoBERTa** | 六点训练细节优化 | ① More data：16GB → 160GB ② Larger batch：256 → 最大 8000 ③ Training longer ④ **No NSP** ⑤ **Dynamic masking**（每个 epoch 重新生成 mask，而非预处理时固定）⑥ **Byte-level BPE**（词表从 3 万增到 5 万） |
| **MacBERT** | 面向中文的改进 | ① MLM 用**近义词替换**代替 `[MASK]`：全词 mask + n-gram mask，1–4 字遮掩比例 40%/30%/20%/10%；用 Word2Vec 找近义词替换，避免 exposure bias ② 删除 NSP 换成 SOP。在阅读理解等中文任务上表现优秀 |
| **SpanBERT** | Span 级掩码 + SBO 目标 | ① **Span Masking**：按几何分布随机选 span 长度（平均约 3.8）、再均匀分布选起始位置；② **Span Boundary Objective (SBO)**：用 span 前后边界两个词的向量 + span 内位置向量预测原词，与 MLM 损失相加共同训练 |

WWM（Whole Word Masking）的思路也值得记住：中文场景下原版 BERT 是字级 MASK，会把本该强相关的连续字词割裂；WWM 改为**整词遮掩**：

```
原始输入: 使用语言模型来预测下一个词的概率
原始 BERT: 使用语言[MASK]型来[MASK]测下一个词的[MASK]率
BERT-WWM: 使用语言[MASK][MASK]来[MASK][MASK]下一个词的[MASK][MASK]
```

延伸：百度的 ERNIE 直接引入命名实体等外部知识，做**整个实体**的遮掩训练。

### 2.5 ELMo 与 GPT（对比视角）

| 模型 | 结构 | 语言模型 | 特点与局限 |
|------|------|----------|-----------|
| ELMo（2018.3，华盛顿大学） | 双向**双层 LSTM** + 特征融合 | 表面双向，实际是左右两个单向 LSTM 分别提特征后简单拼接 | 根据上下文动态调整词向量，能更好解决多义词；但特征提取器没选用更强大的 Transformer |
| GPT（OpenAI） | Transformer 的 **Decoder** | 单向（Masked Multi-Head Attention，未来信息不可见） | 把 3 层 Decoder Block 改为 2 层（删除 encoder-decoder attention），共 12 个 Block；两阶段：无监督预训练 + 有监督微调 |
| BERT | Transformer 的 **Encoder** | 最彻底的双向 | 同时关注 context before 与 context after |

三者对比的核心结论：**特征提取器不同**（BERT=Encoder，GPT=Decoder，ELMo=双层双向 LSTM），**单向/双向不同**（BERT 真双向，GPT 单向，ELMo 伪双向）。

### 2.6 Transformers 库的三层应用结构

Hugging Face 的 Transformers 库提供三个抽象层次，从简到繁：

| 层次 | API | 特点 | 何时用 |
|------|-----|------|--------|
| 管道（Pipeline） | `pipeline(task=..., model=...)` | 高度集成，几行代码完成一个任务 | 快速验证、Demo、推理服务 |
| 自动模型（AutoModel） | `AutoTokenizer` + `AutoModelForXxx` | 可载入并使用 BERTology 系列模型，自动匹配结构 | 需要自定义前向逻辑（如取特定层输出） |
| 具体模型（SpecificModel） | `BertModel` / `BertForSequenceClassification` 等 | 显式指定模型类与参数 | 需要精细控制（改结构、改初始化、接自定义头） |

`pipeline` 支持的任务与对应中文模型示例（用的本地路径）：

| task | 任务 | 说明 |
|------|------|------|
| `text-classification` / `sentiment-analysis` | 文本分类 / 情感分析 | 输出 `{'label': ..., 'score': ...}` |
| `feature-extraction` | 特征抽取 | 输出每个 token 的向量，需与其他模型配合 |
| `fill-mask` | 完形填空（遮蔽语言建模） | 输入必须含 `[MASK]`（大写），**一次只能预测一个 MASK** |
| `question-answering` | 抽取式问答 | 输入 `context` + `question`，输出 `answer` 与 `start/end` |
| `summarization` | 文本摘要 | 输入长文输出短摘要 |
| `ner` | 命名实体识别 | 输出实体片段与类型 |

## 3. 可运行示例

### 3.1 三种调用方式（Pipeline / AutoModel / 自定义下游模型）

```python
# 依赖: pip install transformers torch datasets
import torch
import torch.nn as nn
from transformers import (pipeline, AutoTokenizer,
 AutoModelForSequenceClassification, BertModel)

MODEL_NAME = "bert-base-chinese" # 首次运行会联网下载；也可换成本地路径

# ---------- 方式一：Pipeline，三行搞定 ----------
clf = pipeline(task="text-classification", model=MODEL_NAME)
print(clf("这个产品非常好用，性价比很高"))

# 完形填空：注意 [MASK] 必须大写，且一次只能有一个 MASK
fill = pipeline(task="fill-mask", model=MODEL_NAME)
print([d["token_str"] for d in fill("我想明天去[MASK]家吃饭")][:5])

# 特征抽取：得到每个 token 的向量
feat = pipeline(task="feature-extraction", model=MODEL_NAME)
out = feat("人生该如何起头")
print("特征形状:", torch.tensor(out).shape) # [1, seq_len, 768]

# ---------- 方式二：AutoModel，手动编码与前向 ----------
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
model.eval

encoded = tokenizer(
 ["这段文本很长，需要截断和补齐。" * 30],
 padding="max_length", # 不足补齐
 truncation=True, # 超长截断
 max_length=32,
 return_tensors="pt", # 返回 PyTorch 张量（二维）
)
print("input_ids :", encoded["input_ids"].shape)
print("token_type_ids :", encoded["token_type_ids"].shape)
print("attention_mask :", encoded["attention_mask"].shape)

with torch.no_grad:
 logits = model(**encoded).logits
print("logits:", logits.shape, "预测:", logits.argmax(-1).tolist())
```

对着打印出的形状理解三件输入：`input_ids` 是 token 的 ID，`token_type_ids`（也叫 segment ids）区分句子 A/B，`attention_mask` 标记哪些位置是真实 token（1）哪些是 PAD（0）。

### 3.2 冻结 BERT + 自定义分类头（的核心范式）

```python
# 依赖: pip install transformers torch
import torch
import torch.nn as nn
from torch.optim import AdamW
from transformers import AutoTokenizer, AutoModel

MODEL_NAME = "bert-base-chinese"
device = torch.device("cuda" if torch.cuda.is_available else "cpu")

my_pre_model = AutoModel.from_pretrained(MODEL_NAME).to(device)
my_pre_tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

class AiModel(nn.Module):
    """预训练模型提特征 + 自定义分类头"""

    def __init__(self, num_labels=2, hidden=768):
        super.__init__
        self.linear = nn.Linear(hidden, num_labels)

        def forward(self, input_ids, token_type_ids, attention_mask):
            # 关键：不更新预训练模型参数，把它当特征提取器
            with torch.no_grad:
                bert_output = my_pre_model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                token_type_ids=token_type_ids,
                )
                # last_hidden_state: [B, L, 768]；pooler_output: [B, 768]（[CLS] 位置的表示）
                return self.linear(bert_output.pooler_output)

            def collate_fn(batch):
                """DataLoader 的批处理函数：把文本张量化"""
                sents = [item["text"] for item in batch]
                labels = [item["label"] for item in batch]
                inputs = my_pre_tokenizer.batch_encode_plus(
                sents, truncation=True, max_length=64,
                padding="max_length", return_tensors="pt",
                )
                return (inputs["input_ids"], inputs["token_type_ids"],
            inputs["attention_mask"], torch.LongTensor(labels))

            if __name__ == "__main__":
                # 内联小数据集
                dataset = [{"text": "这个酒店位置好，服务热情", "label": 1},
                {"text": "位置很好，房间干净", "label": 1},
                {"text": "早餐很差，服务不到位", "label": 0},
                {"text": "隔音太差，体验不好", "label": 0}] * 8

                model = AiModel.to(device)
                for p in my_pre_model.parameters():
                    p.requires_grad_(False) # 冻结

                    criterion = nn.CrossEntropyLoss(reduction="mean")
                    # 只优化自定义头，学习率可以比全量微调大
                    optimizer = AdamW(model.parameters(), lr=5e-4)

                    model.train
                    for epoch in range(5):
                        total_loss = 0.0
                        for i in range(0, len(dataset), 8):
                            inputs_ids, token_type_ids, attention_mask, labels = collate_fn(dataset[i:i + 8])
                            inputs_ids = inputs_ids.to(device)
                            token_type_ids = token_type_ids.to(device)
                            attention_mask = attention_mask.to(device)
                            labels = labels.to(device)

                            output = model(inputs_ids, token_type_ids, attention_mask)
                            loss = criterion(output, labels)
                            optimizer.zero_grad()
                            loss.backward()
                            optimizer.step
                            total_loss += loss.item
                            print(f"epoch {epoch + 1} loss={total_loss:.4f}")
```

**全部微调**只需三处改动：把 `with torch.no_grad` 去掉、`requires_grad_(True)`、学习率降到 2e-5~5e-5，并把 `my_pre_model.parameters()` 一起加进优化器。

### 3.3 训练配置与常用超参

```python
# 依赖: pip install transformers torch
# BERT 微调的标准超参（Hugging Face 官方与的建议）
config = {
"learning_rate": 2e-5, # 或 3e-5 / 5e-5，必须很小
"batch_size": 16, # 16 或 32
"num_train_epochs": 3, # 3 或 4
"warmup_ratio": 0.1, # 前 10% steps 线性预热
"weight_decay": 0.01, # L2 正则
"max_grad_norm": 1.0, # 梯度裁剪
"max_length": 128, # 按句子长度分布定（头条项目用 32，医疗项目用 128）
}
print(config)
```

**为什么学习率必须这么小**：BERT 已经在大规模语料上预训练好了，学习率太大（如 0.01）会一步把预训练学到的知识冲垮，性能反而比随机初始化的模型更差。小学习率（2e-5）的作用是「只做微调」，保留预训练语义，同时适配新领域。

更精细的做法是**分层学习率**：底层用更小的学习率（1e-5），顶层和分类头用较大的学习率（1e-3~5e-5），因为底层学到的是通用语言特征，不该被小数据改动太多。

## 4. 常见坑

| 现象 | 原因 | 解决 |
|------|------|------|
| `fill-mask` 输入小写 `[mask]` 报错或无结果 | 特殊 token 必须大写 | 写 `[MASK]` |
| 一次写了多个 `[MASK]`，结果只预测了一个 | Pipeline 的 `fill-mask` 一次只处理一个 MASK | 循环多次调用，每次替换一个位置 |
| 微调后效果比直接推理还差 | 学习率太大，破坏了预训练权重 | 降到 2e-5~5e-5，加 `warmup` 与梯度裁剪 |
| 只训练自定义头，但显存仍然爆炸 | 冻结了参数但没停掉梯度计算 | 前向时套 `with torch.no_grad` |
| 显存溢出（OOM） | `max_length` 太大（attention 是 $O(L^2)$） | 按长度分布定 `max_length`（如 32/128）；减小 batch；用梯度累积 |
| 报错 "size mismatch for bert.embeddings.word_embeddings" | 自定义了词表但没同步调整模型 embedding 大小 | `model.resize_token_embeddings(len(tokenizer))` |
| 训练/推理都跑在 CPU 且极慢 | 忘记把模型与输入放到同一设备 | 模型 `.to(device)`，`input_ids`/`attention_mask`/`labels` 也都要 `.to(device)` |
| GPU 训练后 CPU 上加载失败 | 设备不一致 | `torch.load(path, map_location="cpu")` |
| 中文用 `bert-base-uncased`（英文模型）效果极差 | 英文词表把中文全部映射为 `[UNK]` | 用 `bert-base-chinese` / `hfl/chinese-bert-wwm` 等中文模型 |
| 分类任务自己取 `last_hidden_state` 求平均，效果不如预期 | BERT 分类任务的惯例是取 `[CLS]`（即 `pooler_output`） | 优先用 `pooler_output`，或改用 `AutoModelForSequenceClassification` |
| `model.eval` 忘记调用，推理结果不稳定 | dropout / LayerNorm 仍在训练模式 | 推理前 `model.eval`，并套 `torch.no_grad` |
| 只跑 1 个 epoch 就下结论 | BERT 收敛慢：每个 batch 只有 15% token 参与 MLM | 至少 3–4 个 epoch，观察验证集曲线 |

## 5. 面试问答

**Q1. BERT 的 MLM 为什么用 80%/10%/10% 的比例？**

<details>
<summary>参考答案</summary>

三个比例分别解决三个不同的问题：

**为什么不能 100% 用 `[MASK]`**：`[MASK]` 只出现在预训练阶段，微调/推理时输入里没有它。如果训练时所有被预测的位置都是 `[MASK]`，模型就从未见过这些位置的真实 token，等于整个语义空间损失了这部分信息，还会造成训练-推理不一致（exposure bias）。留 20% 不用 `[MASK]` 就是为了让模型接触真实词形。

**为什么 10% 换成随机词**：如果保留的那部分信息全是原始 token，模型在预训练时可能「偷懒」——直接照抄当前位置的词来预测，而不去学上下文。随机替换会让「照抄」不可靠，逼迫模型去学习周边的语义表达和远距离依赖。

**为什么 10% 保持原词**：以一定概率保留原始 token，意味着「预测目标可能就等于输入」。这保留了语言本来的面貌，让信息不被完全遮掩，模型能「看清」真实语言。同时它也让模型必须对每个位置都真正做判断，而不能靠「看到 `[MASK]` 才预测」的捷径。

补充两点：① 只有 15% 的 token 被选中参与 MASK，不会破坏原语言的表达能力和语法规则；② 代价是收敛慢——left-to-right 模型每个 token 都参与训练，而 BERT 每轮只有 15% 参与。

</details>

**Q2. Encoder-Only、Decoder-Only、Encoder-Decoder 该怎么选？**

<details>
<summary>参考答案</summary>

按任务形态选：

| 任务形态 | 选择 | 代表 | 理由 |
|----------|------|------|------|
| 理解类（分类、NER、抽取式问答、句子相似度） | Encoder-Only | BERT、RoBERTa、MacBERT | 需要**双向**上下文；每个位置都能看到左右信息，表示质量最高 |
| 生成类（续写、对话、代码生成、开放问答） | Decoder-Only | GPT 系列、LLaMA | 生成要求**因果**（只能看左侧），且 Decoder 的结构天然支持自回归推理；参数规模可无限扩展 |
| 序列到序列且输入输出结构差异大（翻译、摘要、生成式问答） | Encoder-Decoder | T5、BART | 编码端双向理解源文本，解码端单向生成目标文本，分工明确 |

几个容易忽略的点：

1. **生成任务不能用 Encoder-Only**：BERT 的双向注意力在自回归推理时会「看到未来」，训练与推理不一致。
2. **理解任务也可以用 Decoder-Only**，只要把输入拼成 prompt（如「这句话的情感是：」）。近年的大模型证明了 Decoder-Only + 大规模参数 + 指令微调可以统一处理理解与生成，这也是当前主流路线。
3. **Encoder-Decoder 在纯理解任务上没有优势**：多了一个解码器却不用于生成，白白增加参数与推理成本。
4. **选型的现实约束是算力与延迟**：Encoder-Only 的 base 模型（110M）能在 CPU 上跑到几十毫秒；Decoder-Only 的 LLM 通常需要 GPU 与量化才能上线。

</details>

**Q3. 什么是「微调」？为什么 BERT 微调的学习率要设得这么小？**

<details>
<summary>参考答案</summary>

**微调（fine-tuning）**：在预训练模型后面接一个自定义网络（如一层 `nn.Linear(768, num_labels)`），然后用垂直领域数据继续训练。参数更新策略有三档——全部微调、部分微调（冻结底层）、不微调（只用预训练模型当特征提取器，`requires_grad=False` + `torch.no_grad`）。

**学习率必须很小（2e-5~5e-5）的原因**：BERT 的权重已经在海量语料上收敛到一个很好的解，这些权重编码的是通用语言知识（词法、句法、常识共现）。如果用小任务的数据、配一个大学习率（如 0.01）去更新，会有两个后果：

1. **破坏预训练知识**：少数几个 batch 的梯度就会把权重推离预训练解，模型「忘掉」通用语言能力（灾难性遗忘）。极端情况下微调后的效果比直接拿预训练模型当特征提取器还差。
2. **小数据下过拟合极快**：下游数据通常只有几千到几万条，相对 110M 参数而言极少，大学习率会让模型迅速记住训练集。

配套的三个技巧一起用：

- **Warmup**（`warmup_ratio=0.1`）：前 10% 的 step 从 0 线性升到目标学习率，避免一开始的大梯度冲击。
- **梯度裁剪**（`max_grad_norm=1.0`）：防止个别 batch 的梯度爆炸。
- **权重衰减**（`weight_decay=0.01`）：抑制过拟合。

区分两个层次：**全量微调**用 2e-5~5e-5；**只训练自定义头**时，因为预训练权重被冻结、只有少量新参数，可以用更大的学习率（如 5e-4）。

</details>

## 6. 自测题

**1. BERT 的三种 Embedding 分别是什么？它们在经典 Transformer 中对应什么？**

<details>
<summary>参考答案</summary>

| Embedding | 作用 | 经典 Transformer 中的对应 |
|-----------|------|---------------------------|
| Token Embeddings | 把 token 映射为向量；第一个 token 是 `[CLS]`（用于分类） | Token Embedding |
| Segment Embeddings | 区分句子 A 与句子 B（句对任务需要） | 无（原版 Transformer 靠位置和 mask 区分，没有显式句段标记） |
| Position Embeddings | 提供位置信息 | Positional Encoding（但 BERT 的**是可学习参数**，原版是 sin/cos 公式） |

三者的输出**直接相加**（不是拼接），得到 $[B, L, 768]$ 的输入张量。

关键差异要能指出：**BERT 的位置编码是学习出来的**，不是三角函数。这带来两个后果：① 位置表示更贴合数据；② 最大长度被硬性限制在预训练时的 512，无法像 sin/cos 那样外推到更长序列。

</details>

**2. 计算：`bert-base-chinese` 有 12 层、768 维、12 个注意力头。请算出每个头的维度、前馈层的中间维度，以及一个 Encoder Block 里多头注意力的参数量（忽略偏置）。**

<details>
<summary>参考答案</summary>

- **每个头的维度**：$d_k = d_{model} / h = 768 / 12 = 64$
- **前馈层中间维度**：按 4 倍关系，$d_{ff} = 4 \times 768 = 3072$
- **多头注意力的参数量（忽略偏置）**：$Q,K,V$ 三个投影各 $768\times768$，输出投影 $W^O$ 也是 $768\times768$，共 $4 \times 768^2 = 4 \times 589824 = 2{,}359{,}296 \approx 2.36\text{M}$

作为对照，前馈层参数量是 $2 \times (768 \times 3072) = 4{,}718{,}592 \approx 4.72\text{M}$ —— **每层前馈层的参数是多头注意力的两倍**，这是 Transformer 参数分布的一个反直觉特点（注意力负责建模关系，前馈层负责储存知识）。

整层约 7.08M，12 层约 85M，加上 embedding（$21128 \times 768 \approx 16.2\text{M}$）与 pooler，总量约 110M —— 与官方公布的参数量吻合。

</details>

**3. 「BERT 是双向的，GPT 是单向的，ELMo 也是双向的」这句话哪里不严谨？**

<details>
<summary>参考答案</summary>

不严谨在 **ELMo 的「双向」是伪双向**。

| 模型 | 方向性 | 真实机制 |
|------|--------|----------|
| BERT | **真双向** | 用 MLM 任务，每一层的每个位置在 self-attention 里都能同时看到左侧和右侧的 token |
| GPT | 单向 | 用 Masked Multi-Head Attention（下三角 mask），未来信息 `context after` 不可见 |
| ELMo | **伪双向** | 结构上是**两个独立的单向 LSTM**（一个从左到右、一个从右到左），各自提完特征后简单拼接/融合。左右两向之间没有交互，因此不是真正的双向编码 |

差异的实践含义：ELMo 的每个方向在编码时都不知道另一个方向的存在，两向信息的融合只发生在最后的加权求和；BERT 从第一层开始每个位置的表示就同时包含左右上下文，因此表示质量更高。这也解释了为什么「用 LSTM 做双向」无论怎么设计都很难达到 BERT 的效果——根本区别不在结构层数，而在**是否真正联合建模上下文**。

另外一个常考的对比点：三者选用的**特征提取器**不同——BERT 用 Transformer Encoder，GPT 用 Transformer Decoder，ELMo 用双层双向 LSTM。ELMo 的已知局限就是没选用更强大的 Transformer。

</details>

**4. 中文 BERT 是「字级」的，这会带来什么问题？有什么解决办法？**

<details>
<summary>参考答案</summary>

**问题一：与词向量相关的应用不兼容。** 很多传统 NLP 应用（关键词抽取、词相似度、词级别的 TF-IDF 融合）需要**词**向量，而字级模型只给每个字一个向量。要得到词向量得自己对字向量做池化，效果不如原生词向量。

**问题二：生僻词只能以 `[UNK]` 代替。** 字级词表覆盖的是常用汉字（约 2.1 万），遇到 GBK 之外的生僻字、异体字、emoji、特殊符号时直接变成 `[UNK]`，信息完全丢失。相比之下英文的 WordPiece 子词能通过 `##` 碎片兜住未登录词。

**问题三：序列变长。** 同样一段文本，字级 token 数比词级多 1.5–2 倍，而 attention 是 $O(L^2)$，导致计算量与显存上升、`max_length=512` 能覆盖的文本更短。

**解决办法**：

1. **换用 WWM / MacBERT 等改进中文模型**：`hfl/chinese-bert-wwm`、`hfl/chinese-macbert-base` 在 MLM 阶段用整词 mask 与近义词替换，学到的表示更接近词级语义。
2. **扩充 tokenizer 词表**：用领域语料训练一个子词词表，合并进原词表（`tokenizer.add_tokens(...)`），再 `model.resize_token_embeddings(len(tokenizer))`，然后继续预训练（continue pretraining）。这对医疗、法律等领域专名效果显著。
3. **先分词再用词级模型**：对必须在词级操作的任务（如基于词向量的检索），回到 jieba + word2vec/FastText 的路线（第 04 篇），或把词向量作为额外特征与 BERT 表示拼接。
4. **处理生僻字**：在预处理阶段做字符规范化（繁简统一、异体字映射），或改用字节级 BPE 的模型（如 RoBERTa 的中文版本、部分多语言模型）。
5. **长文本**：按第 2.3 节的 head+tail 截断，或分块后聚合结果。

</details>

## 7. 延伸阅读

- BERT 原始论文《BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding》：https://arxiv.org/abs/1810.04805
- Hugging Face Transformers 官方文档（Pipeline / AutoModel / Trainer 全部 API）：https://huggingface.co/docs/transformers/index
- Hugging Face 模型库（可直接搜索中文模型，如 `bert-base-chinese`、`hfl/chinese-macbert-base`）：https://huggingface.co/models
- ALBERT 论文《A Lite BERT for Self-supervised Learning of Language Representations》：https://arxiv.org/abs/1909.11942
- RoBERTa 论文《RoBERTa: A Robustly Optimized BERT Pretraining Approach》：https://arxiv.org/abs/1907.11692
- MacBERT 论文《Revisiting Pre-trained Models for Chinese Natural Language Processing》：https://arxiv.org/abs/2004.13922
- SpanBERT 论文《SpanBERT: Improving Pre-training by Representing and Predicting Spans》：https://arxiv.org/abs/1907.10529

---

[⬅️ 返回 NLP 目录](README.md)
