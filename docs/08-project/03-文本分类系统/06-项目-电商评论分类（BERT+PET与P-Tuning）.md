# 项目实战笔记 06：电商评论分类（BERT+PET 与 BERT+P-Tuning）

> **一句话总结**：把"评论分类"这个判别任务**改写成完形填空**——PET 用人工硬模板 + 标签词映射（Verbalizer），P-Tuning 用可学习的软模板（伪 token），两者都在 63 条训练样本上把 BERT 的潜力榨出来。
> **前置知识**：BERT 与 MLM（掩码语言模型）预训练目标、`[MASK]` token 的语义、`AutoModelForMaskedLM` 与 `AutoTokenizer`、HuggingFace `datasets.map(batched=True)`、PyTorch 训练循环与 `CrossEntropyLoss`。

> 1. 说清 Prompt-Tuning 为什么能在小样本上打赢传统 Fine-tuning，以及它的适用边界；
> 2. 独立实现 PET 完整链路：模板解析 → 数据编码 → Verbalizer 映射 → MLM 损失 → 子标签反查主标签；
> 3. 实现 P-Tuning 的伪 token 插入、`mask_position` 记录与 `attention_mask` 修正，并解释每一处为什么必要。

## 1. 项目目标与业务背景

### 1.1 业务场景

电商平台的智能推荐系统里，用户评论是**语义信息丰富的隐式特征**。相比"打分"这种显式特征，文本评论有两个优势：**弥补评分稀疏性**（大部分用户不打分，但愿意写几个字）、**提升推荐可解释性**（"因为你买过的商品评论里都在夸'物流快'"比"因为你点了它"更有说服力）。

要利用它，第一步是把评论**自动归类**。本项目的 10 个类别来自电商真实货品评论：

```text
电脑 水果 平板 衣服 酒店 洗浴 书籍 蒙牛 手机 电器
```

| 评论 | 类别 |
| --- | --- |
| 衣服掉色掉的厉害，洗一次就花了 | 衣服 |
| 水果苹果有点小，不过好吃，还有几个烂的。估计是故意的放的。差评。 | 水果 |
| 平板华为机器肯定不错，但第一次碰上京东最糟糕的服务，以后不想到京东购物了。 | 平板 |
| 服务很用心，房型也很舒服…床铺柔软舒适，晚上休息很安逸，隔音效果不错赞 | 酒店 |

### 1.2 真正的难点：样本极少

```text
train.txt 63 条 ← 训练集只有 63 条！
dev.txt 590 条 ← 验证集
```

**63 条样本训 110M 参数的 BERT**，传统 Fine-tuning 必然过拟合。这就是引入 Prompt-Tuning 的根本原因：

> 在很多实际场景中，由于领域特殊性和标注成本高，导致标注训练数据缺乏，模型无法有效学习参数，从而易出现过拟合现象。因此，如何通过小样本数据训练得到一个性能较好的分类模型，是目前的研究热点。

### 1.3 两条路线

| | BERT + PET（硬模板） | BERT + P-Tuning（软模板） |
| --- | --- | --- |
| 模板来源 | **人工设计**自然语言模板 | **模型学习**连续向量（伪模板） |
| 模板形态 | `这是一条[MASK]评论：{textA}。` | `[unused1]..[unused6][CLS][MASK][MASK]文本[SEP]` |
| 需改模型结构吗 | 不需要，纯数据处理 | 不需要（用 `[unused]` 占位） |
| 优点 | 不引入随机初始化参数，过拟合风险低 | 模板可全局优化，能学到更优表示 |
| 缺点 | 稳定性差，不同模板准确率可差近 20 个百分点；无法全局优化 | 引入可学习参数；超多分类/蕴含类任务效果受限 |

## 2. 技术架构

### 2.1 PET 数据流（硬模板）

```text
data/train.txt (63 条，格式：标签\t评论) 例：衣服\t衣服掉色掉的厉害，洗一次就花了
 │
data/prompt.txt → "这是一条{MASK}评论：{textA}。"
data/verbalizer.txt → "衣服\t衣服"、"水果\t苹果,香蕉,橘子" ...
 │
 │ HardTemplate.prompt_analysis：逐字符扫描 prompt，遇 { } 提取自定义字段
 ▼
inputs_list = ['这','是','一','条','MASK','评','论','：','textA','。']
custom_tokens = {'MASK', 'textA'}
 │
 │ HardTemplate.__call__
 │ ① 用真实文本填充 {textA} ② {MASK} 展开成 mask_length 个 "[MASK]"(=2)
 ▼
str_formated = "这是一条[MASK][MASK]评论：衣服掉色掉的厉害，洗一次就花了。"
 │ tokenizer(truncation=True, max_length=256, padding='max_length')
 ▼
input_ids [1, 47, 10, 7, 304, 3, 3, 47, 27, ... 2] 定长 256
token_type_ids [0, 0, ..., 0]
attention_mask [1, 1, ..., 1, 0, 0, ..., 0]
mask_position [4, 5] ← np.where(input_ids == mask_token_id)
mask_labels [2372, 3442] ← label → tokenizer(label)，截断/pad 到 2（"衣服"）
```

### 2.2 PET 训练与评估流

```text
batch = {input_ids, token_type_ids, attention_mask, mask_positions, mask_labels}
 │
 ▼
model(input_ids, token_type_ids, attention_mask).logits → (batch, 256, 21128)
 │
 ├─▶ 训练：mask_labels → Verbalizer.batch_find_sub_labels
 │ '水果' → ['苹果'(2tok), '香蕉'(2tok), '橘子'(2tok)] ← 变长！
 │ ▼
 │ mlm_loss(logits, mask_positions, sub_mask_labels, criterion, device)
 │ 取出 mask 位置 logits → (mask_label_num, vocab)
 │ repeat → (sub_label_num, mask_label_num, vocab)
 │ reshape → (sub_label_num*mask_label_num, vocab)
 │ 与每个子标签 token 求 CE，按 token 数归一化后平均
 │
 └─▶ 评估：convert_logits_to_ids(logits, mask_positions)
 reshape(batch*seq_len, vocab)[batch*seq_len+pos] → argmax
 → predictions (batch, label_num) 的 token id
 ▼
 Verbalizer.batch_find_main_label(predictions)
 ① 命中 label_dict 子标签 → 直接返回主标签
 ② 未命中 → hard_mapping：与所有子标签求最长公共子串，取总长最大者
 ▼
 ClassEvaluator 累计 → accuracy / precision / recall / f1 / 每类指标
```

### 2.3 P-Tuning 数据流（软模板）

```text
convert_example(p_embedding_num=6, max_label_len=2, max_seq_len=512)
 ① tokenizer(content) → input_ids（含 [CLS]...[SEP]）
 ② 生成 2 个 [MASK]
 ③ 生成 6 个伪 token：["[unused1]".."[unused6]"] → ids
 ④ 裁剪正文：input_ids[: max_seq_len - len(mask_ids) - len(p_tokens_ids) - 1]
 ⑤ 在 [CLS] 之后（position=1）插入 [MASK][MASK]
 ⑥ 6 个伪 token 拼到最前面
 ▼
位置: 0 1 2 3 4 5 6 7 8 9 ... 509 510 511
内容: [u1] [u2] [u3] [u4] [u5] [u6][CLS][MASK][MASK] 正文... [SEP][PAD]
 └──── 伪 token（软模板）────┘ └─ 预测目标 ─┘
 │
 ⑦ mask_positions = [len(p_tokens)+1+i for i in range(2)] = [7, 8]
 ⑧ attention_mask = np.where(np.array(input_ids) > 0, 1, 0) ← ★ 必须重算
 ⑨ mask_labels = tokenizer(label)['input_ids'][1:-1]，截断/pad 到 2
 ▼
{input_ids, attention_mask, mask_positions, mask_labels}
```

### 2.4 一句话对比

```text
PET: [CLS] 这是一条[MASK][MASK]评论：{评论}。 [SEP] ← 模板是自然语言，写在数据里
P-Tuning: [u1]..[u6] [CLS] [MASK][MASK] {评论} [SEP] ← 模板是向量，写在输入最前面
```

**共同点**：两者都把分类任务转成"预测 `[MASK]` 位置是什么词"。区别只在模板是**人写的字**还是**模型学的向量**。

## 3. 关键技术选型与理由

| 方案 | 优点 | 代价 | 本项目为何选它 |
| --- | --- | --- | --- |
| **Prompt-Tuning（PET / P-Tuning）** | 小样本下远优于 Fine-tuning；不用改模型结构；不用重新预训练 | 模板设计/调参成本高；性能对模板敏感 | **训练集只有 63 条**，传统 Fine-tuning 必过拟合 |
| 传统 Fine-tuning（加分类头） | 实现最简单，`BertForSequenceClassification` 一行 | 63 条样本 ⇒ 分类头随机初始化 + 全量微调 ⇒ 严重过拟合 | 放弃。需数万条样本才能发挥 |
| **`AutoModelForMaskedLM`** 而非 `BertForSequenceClassification` | 直接复用 BERT 原生 MLM 头，**不引入任何随机初始化参数** | 需自己算 loss、自己做标签映射 | PET/P-Tuning 的核心思想就是"任务与预训练目标保持一致" |
| **硬模板（PET）** | 无新增参数；模板可读可解释 | 模板靠人写，不同模板准确率可差近 20 个百分点 | 先用最直观的方式实现，作为软模板的对照基线 |
| **软模板（P-Tuning）** | 模板可微调、可全局优化；缓解人工模板不稳定 | 引入 `p_embedding_num × hidden` 的可学习参数 | 在 PET 基础上改进"人工模板不稳"的问题 |
| **`[unused1]`~`[unused6]` 作伪 token** | BERT 中文词表自带空位，无需扩词表；改动最小 | 只有 99 个 `[unused]` 可用，数量与位置受限 | 不改 `vocab.txt`、不改模型结构就能加软模板，工程成本最低 |
| **Verbalizer（标签词映射）** | 把"类别名"换成"模型更容易预测的词" | 需为每个类别设计子标签；映射表要人工维护 | `"这件衣服掉色严重"是一则[MASK][MASK]评论。` 预测"衣服"很难，预测"掉色"容易得多 |
| **`max_label_len=2`** | 支持"衣服"这类双字标签 | 单字标签要 pad；3 字词被截断 | 中文类别名多为 2 字，恰好对齐 |
| **`hard_mapping`（最长公共子串兜底）** | 模型生成表外词时也能映射到主标签 | 可能映射错误；O(标签数×子标签数×串长²) | 保证推理**永远有输出**，不会因没见过一个词就崩 |
| **`datasets.map(batched=True)`** | 一次处理一批，速度快；与 HF 生态无缝 | 调试时看不到逐条过程 | 与 `partial` 固定超参配合，代码极简 |
| **`ClassEvaluator` 自算指标** | 同时得到 acc/P/R/F1 和每类细分指标 | 需要自己写 | 小样本必须看每类指标——10 类只有 63 条样本，平均准确率毫无意义 |

### 3.1 为什么 PET 能小样本奏效：三个理由

1. **不引入随机初始化参数。** `BertForSequenceClassification` 会新增 `Linear(768, 10)` 分类头，63 条样本根本训不好它；PET 直接用已在海量文本上训好的 MLM 头。
2. **把分类任务对齐到预训练目标（task alignment）。** BERT 预训练就是在"预测 `[MASK]`"，PET 让它继续做同一件事，只换了输入的位置。
3. **标签词映射提供了先验。** 告诉模型"要预测的是一个表示类别的词"，比让它从零学"第 3 号类是什么"信息量大得多。

## 4. 核心实现

### 4.1 PET：把自然语言模板解析成可填充的数据结构

```text
class HardTemplate(object):
 """硬模板，人工定义句子和 [MASK] 之间的位置关系。"""

 def __init__(self, prompt: str):
 self.prompt = prompt
 self.inputs_list = []
 self.custom_tokens = set(['MASK'])
 self.prompt_analysis

 def prompt_analysis(self):
 """'这是一条{MASK}评论：{textA}。'
 -> inputs_list = ['这','是','一','条','MASK','评','论','：','textA','。']
 custom_tokens = {'MASK', 'textA'}
 """
 idx = 0
 while idx < len(self.prompt):
 str_part = ''
 if self.prompt[idx] not in ['{', '}']:
 self.inputs_list.append(self.prompt[idx])
 if self.prompt[idx] == '{': # 进入自定义字段
 idx += 1
 while self.prompt[idx] != '}':
 str_part += self.prompt[idx]
 idx += 1
 elif self.prompt[idx] == '}':
 raise ValueError("Unmatched bracket '}', check your prompt.")
 if str_part:
 self.inputs_list.append(str_part)
 self.custom_tokens.add(str_part)
 idx += 1
```

**为什么不用正则**：模板里可能有任意多个自定义字段。手写字符级状态机行为完全可控，还能在遇到不匹配的 `}` 时立刻抛出明确错误。对"用户会自己改模板"的场景，**错误信息清晰**比代码简短更重要。

填充与编码：

```text
def __call__(self, inputs_dict, tokenizer, mask_length, max_seq_len=512):
 # ① 把模板里的占位符换成真实内容
 str_formated = ''
 for value in self.inputs_list:
 if value in self.custom_tokens:
 if value == 'MASK':
 str_formated += inputs_dict[value] * mask_length # 展开成 N 个 [MASK]
 else:
 str_formated += inputs_dict[value]
 else:
 str_formated += value

 # ② 编码成定长张量
 encoded = tokenizer(text=str_formated, truncation=True,
 max_length=max_seq_len, padding='max_length')
 outputs = {'text': ''.join(tokenizer.convert_ids_to_tokens(encoded['input_ids'])),
 'input_ids': encoded['input_ids'],
 'token_type_ids': encoded['token_type_ids'],
 'attention_mask': encoded['attention_mask']}

 # ③ 记录 [MASK] 位置——后续取 logits 的唯一依据
 mask_token_id = tokenizer.convert_tokens_to_ids(['[MASK]'])[0]
 outputs['mask_position'] = np.where(
 np.array(outputs['input_ids']) == mask_token_id)[0].tolist
 return outputs
```

**`mask_position` 是整个 PET 的枢纽**。用 `np.where` 从 `input_ids` **反查**，而不是假设"模板里第 5 个字符是 MASK"——因为 tokenizer 可能按字切分（位置刚好对上），也可能对英文/数字做合并（位置偏移）。**从编码结果反查，永远不会错位。**

### 4.2 Verbalizer：标签词映射与反查

```python
class Verbalizer(object):
    """将一个 Label 对应到其子 Label 的映射。"""

    def load_label_dict(self, verbalizer_file):
        """'水果\t苹果,香蕉,橘子' -> {'水果': ['苹果','香蕉','橘子'], ...}"""
        label_dict = {}
        with open(verbalizer_file, 'r', encoding='utf8') as f:
            for line in f.readlines:
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
            for label, s_labels in self.label_dict.items:
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
                    for main_label, sub_labels in self.label_dict.items:
                        overlap = sum(self.get_common_sub_str(sub_label, s)[1] for s in sub_labels)
                        if overlap >= max_overlap:
                            max_overlap, label = overlap, main_label
                            return label
```

`get_common_sub_str` 是最长公共子串的标准 DP（`record[i+1][j+1] = record[i][j] + 1`），实现从略。

**为什么必须要 `hard_mapping`**：模型的输出空间是整个 21128 词的词表。即使 Prompt 引导它输出"水果类"的词，也可能输出"苹果好吃""红色的"这种表里没有的东西。没有兜底就会 `KeyError` 或返回"无"。有了最长公共子串匹配，"苹果好吃"与"苹果"共享 2 个字符，从而正确归到"水果"。

**代价是它可能强行映射错误的东西**——这是双刃剑。生产环境应加**重合度阈值**，低于阈值返回"无法判定"，而不是硬猜。

### 4.3 PET 的 MLM 损失：变长子标签的处理

全项目最绕的一段，逐行拆解：

```python
def mlm_loss(logits, mask_positions, sub_mask_labels, cross_entropy_criterion, device):
    """
    logits: (batch, seq_len, vocab_size) = (8, 256, 21128)
    mask_positions: (batch, mask_label_num) = (8, 2)
    sub_mask_labels: 变长 list，e.g. [[[2398,3352]], [[2398,3352], [3819,3861]]]
    """
    batch_size, seq_len, vocab_size = logits.size
    loss = None

    for single_logits, single_sub_mask_labels, single_mask_positions in \
    zip(logits, sub_mask_labels, mask_positions):

        # ① 取出 mask 位置的 logits：(mask_label_num, vocab_size)
        single_mask_logits = single_logits[single_mask_positions]
        # ② 复制 sub_label_num 份：(sub_label_num, mask_label_num, vocab_size)
        single_mask_logits = single_mask_logits.repeat(len(single_sub_mask_labels), 1, 1)
        # ③ 拉平：(sub_label_num * mask_label_num, vocab_size)
        single_mask_logits = single_mask_logits.reshape(-1, vocab_size)

        # ④ 标签同样拉平
        single_sub_mask_labels = torch.LongTensor(single_sub_mask_labels).to(device)
        single_sub_mask_labels = single_sub_mask_labels.reshape(-1, 1).squeeze

        # ⑤ 交叉熵，按 token 数归一化（消除子标签个数差异带来的量纲差）
        cur_loss = cross_entropy_criterion(single_mask_logits, single_sub_mask_labels)
        cur_loss = cur_loss / len(single_sub_mask_labels)

        loss = cur_loss if loss is None else loss + cur_loss

        return loss / batch_size
```

**核心思想**：一个主标签可能对应多个子标签（"水果" → 苹果/香蕉/橘子）。模型的 2 个 `[MASK]` 位置应该**同时倾向于所有这些子标签**，而不是只倾向某一个。实现手法是把 mask 位置的 logits **复制 N 份**（N = 子标签个数），与所有子标签 token 一起算交叉熵——**只要预测的是任一合法子标签，loss 都低**。

**`cur_loss / len(single_sub_mask_labels)` 这一步容易漏**：不归一化的话，子标签多的类别（"水果"有 3 个）算出的 loss 天然是子标签少的类别的 3 倍，相当于给类别加了隐式权重。除以 token 数把量纲拉平，batch 平均才有意义。

### 4.4 从 logits 取出预测：索引展平

```python
def convert_logits_to_ids(logits, mask_positions):
    """logits: (8, 512, 21128); mask_positions: (8, 2) -> 返回 (8, 2)"""
    label_length = mask_positions.size[1]
    batch_size, seq_len, vocab_size = logits.size

    # 把二维坐标 (batch, pos) 展平成一维索引 batch * seq_len + pos
    mask_positions_after_reshaped = []
    for batch, mask_pos in enumerate(mask_positions.detach.cpu.numpy.tolist):
        for pos in mask_pos:
            mask_positions_after_reshaped.append(batch * seq_len + pos)

            logits = logits.reshape(batch_size * seq_len, -1) # 二维化
            mask_logits = logits[mask_positions_after_reshaped] # 取出 mask 位置
            predict_tokens = mask_logits.argmax(dim=-1)
            return predict_tokens.reshape(-1, label_length)
```

**为什么要手算 `batch * seq_len + pos`**：`logits[batch_idx, pos]` 这种高级索引对多维张量（尤其 pos 变长时）支持有限。展平成一维后用 Python 列表索引最稳妥、最不会出错。

代价是经过 `.cpu.numpy.tolist`，意味着一次 GPU→CPU 同步拷贝。追求性能时应用 `torch.gather` 或 `logits.gather(1, mask_positions.unsqueeze(-1).expand(...))` 全程留在 GPU。对 63 条样本的项目，损耗可忽略。

### 4.5 P-Tuning：把软模板插进输入序列

```python
def convert_example(examples, tokenizer, max_seq_len, max_label_len,
p_embedding_num=6, train_mode=True):
    tokenized_output = {'input_ids': [], 'attention_mask': [],
    'mask_positions': [], 'mask_labels': []}

    for example in examples['text']:
        start_mask_position = 1 # 将 prompt token(s) 插在 [CLS] 之后

        label, content = example.strip.split('\t', 1) # ★ 限制只切一刀
        encoded_inputs = tokenizer(text=content, truncation=True,
        max_length=max_seq_len, padding='max_length')
        input_ids = encoded_inputs['input_ids']

        # ① 生成 MASK tokens（个数 = 标签长度）
        mask_ids = tokenizer.convert_tokens_to_ids(['[MASK]'] * max_label_len)
        # ② 构建伪 token
        p_tokens_ids = tokenizer.convert_tokens_to_ids(
        ["[unused{}]".format(i + 1) for i in range(p_embedding_num)])

        # ③ 按预算裁剪正文长度：[CLS] + MASK + 正文 + [SEP] + 伪 token
        tmp_input_ids = input_ids[:-1] # 先去 [SEP]
        tmp_input_ids = tmp_input_ids[:max_seq_len - len(mask_ids) - len(p_tokens_ids) - 1]
        # ④ 在 [CLS] 之后插入 [MASK]
        tmp_input_ids = (tmp_input_ids[:start_mask_position] + mask_ids
        + tmp_input_ids[start_mask_position:])
        input_ids = tmp_input_ids + [input_ids[-1]] # 补回 [SEP]
        input_ids = p_tokens_ids + input_ids # 伪 token 拼到最前

        # ⑤ 记录 MASK 位置（伪 token 占位导致整体右移）
        mask_positions = [len(p_tokens_ids) + start_mask_position + i
        for i in range(max_label_len)]

        tokenized_output['input_ids'].append(input_ids)
        tokenized_output['attention_mask'].append(get_attention_mask(input_ids)) # ★
        tokenized_output['mask_positions'].append(mask_positions)

        if train_mode:
            mask_labels = tokenizer(text=label)['input_ids'][1:-1] # 剥 [CLS]/[SEP]
            mask_labels = mask_labels[:max_label_len]
            mask_labels += [tokenizer.pad_token_id] * (max_label_len - len(mask_labels))
            tokenized_output['mask_labels'].append(mask_labels)
```

**（1）为什么 `attention_mask` 要重新算？**

```python
def get_attention_mask(alist):
 return np.where(np.array(alist) > 0, 1, 0).tolist
```

伪 token `[unused1]`~`[unused6]` 在中文 BERT 词表里是 id 1~99（`> 0`），它们是**真实存在、需要参与注意力**的位置；尾部补的 `[PAD]` 才是 id 0。而 `tokenizer` 返回的 `attention_mask` **不知道你手工往前面塞了 token**，直接用会把伪 token 当 padding 忽略掉，**软模板就完全失效了**。

代码注释里留了痕迹，这本身就是一条踩坑记录：

```python
# 不修改位置（结果指标较低）
# tokenized_output['attention_mask'].append(encoded_inputs['attention_mask'])
```

**静默失效是最难查的 bug 类型**——它不报错、只是掉点。更稳的写法是**不依赖"id > 0"这个隐式约定**，而是显式基于长度构造：

```python
seq_len = len(input_ids)
attention_mask = [1] * seq_len + [0] * (max_seq_len - seq_len)
```

**（2）为什么 `split('\t', 1)` 要限制切分次数？** 评论内容里完全可能出现制表符（从网页复制粘贴的文本常带）。不限次数的话 `split('\t')` 会返回 3 个以上元素，直接 `ValueError: too many values to unpack`。加 `maxsplit=1` 只按第一个制表符切成"标签"和"其余全部"，天然健壮。

**对照 PET 的 `data_preprocess.py` 写的是 `split('\t')`（不限次数）——这是一处真实存在的健壮性差距。**

### 4.6 训练循环与评估

```text
def model2train:
 model = AutoModelForMaskedLM.from_pretrained(pc.pre_model) # ★ 用 MLM 头，不换分类头
 tokenizer = AutoTokenizer.from_pretrained(pc.pre_model)
 verbalizer = Verbalizer(verbalizer_file=pc.verbalizer, tokenizer=tokenizer,
 max_label_len=pc.max_label_len)

 # 分层权重衰减：bias 和 LayerNorm 不衰减
 no_decay = ["bias", "LayerNorm.weight"]
 optimizer_grouped_parameters = [
 {"params": [p for n, p in model.named_parameters if not any(nd in n for nd in no_decay)],
 "weight_decay": pc.weight_decay},
 {"params": [p for n, p in model.named_parameters if any(nd in n for nd in no_decay)],
 "weight_decay": 0.0}]
 optimizer = torch.optim.AdamW(optimizer_grouped_parameters, lr=pc.learning_rate)

 train_dataloader, dev_dataloader = get_data
 max_train_steps = pc.epochs * len(train_dataloader)
 warm_steps = int(pc.warmup_ratio * max_train_steps)
 lr_scheduler = get_scheduler(name='linear', optimizer=optimizer,
 num_warmup_steps=warm_steps,
 num_training_steps=max_train_steps)

 criterion = torch.nn.CrossEntropyLoss
 global_step, best_f1 = 0, 0
 for epoch in range(pc.epochs):
 for batch in tqdm(train_dataloader):
 logits = model(input_ids=batch['input_ids'].to(pc.device),
 token_type_ids=batch['token_type_ids'].to(pc.device),
 attention_mask=batch['attention_mask'].to(pc.device)).logits

 # ★ 训练目标是"子标签"（软目标），不是原始标签
 mask_labels = batch['mask_labels'].numpy.tolist
 sub_labels = [e['token_ids'] for e in verbalizer.batch_find_sub_labels(mask_labels)]

 loss = mlm_loss(logits, batch['mask_positions'].to(pc.device),
 sub_labels, criterion, pc.device)
 optimizer.zero_grad; loss.backward; optimizer.step; lr_scheduler.step

 global_step += 1
 if global_step % pc.valid_steps == 0:
 acc, precision, recall, f1, class_metrics = evaluate_model(
 model, metric, dev_dataloader, tokenizer, verbalizer)
 # 保存 F1 最优的模型（而不是最后一个）
 if f1 > best_f1:
 best_f1 = f1
 model.save_pretrained(os.path.join(pc.save_dir, "model_best"))
```

评估环节的关键是把预测出的 token **翻译回主标签**：

```python
def evaluate_model(model, metric, data_loader, tokenizer, verbalizer):
    model.eval
    with torch.no_grad:
        for batch in data_loader:
            logits = model(input_ids=..., attention_mask=..., token_type_ids=...).logits

            # ① mask_labels 去掉 [PAD]、转回文字作为 gold
            mask_labels = batch['mask_labels'].numpy.tolist
            for i in range(len(mask_labels)):
                while tokenizer.pad_token_id in mask_labels[i]:
                    mask_labels[i].remove(tokenizer.pad_token_id)
                    mask_labels = [''.join(tokenizer.convert_ids_to_tokens(t)) for t in mask_labels]

                    # ② 预测 token → 子标签 → 主标签
                    predictions = convert_logits_to_ids(logits, batch['mask_positions']).cpu.numpy.tolist
                    predictions = [e['label'] for e in verbalizer.batch_find_main_label(predictions)]

                    metric.add_batch(pred_batch=predictions, gold_batch=mask_labels)
                    return metric.compute['accuracy'], ..., metric.compute['class_metrics']
```

**这里有一个隐蔽的必要约束**：`gold` 用的是 `mask_labels`（原始标签词，如"衣服"），而 `pred` 是经 Verbalizer 反查的主标签。所以映射表必须保证**主标签词本身也是自己的子标签**——看 `verbalizer.txt`：

```text
电脑	电脑
水果	水果
衣服	衣服
```

每个主标签都把自己列为子标签之一，就是为了让 `find_main_label('水果')` 正确返回"水果"而不是走 `hard_mapping` 兜底。**自己实现时极容易忽略这一点。**

### 4.7 训练结果

```text
global step 40, epoch: 4, loss: 0.62105, speed: 1.27 step/s
global step 60, epoch: 7, loss: 0.41744, speed: 1.23 step/s
global step 390, epoch: 48, loss: 0.06674, speed: 1.20 step/s
global step 400, epoch: 49, loss: 0.06507, speed: 1.21 step/s

Evaluation precision: 0.78000, recall: 0.76000, F1: 0.75000
```

**仅用 63 条训练样本，在 590 条验证集上精确率约 78%**，而传统 Fine-tuning 在 63 条样本上通常拿不到这个水平。想再提升，最直接的手段是**扩增样本**。

## 5. 踩坑与解决

| 现象 | 根因 | 解决 | 如何预防 |
| --- | --- | --- | --- |
| P-Tuning 指标明显偏低但训练不报错 | `attention_mask` 沿用了 tokenizer 的返回值，伪 token `[unused*]` 被当成 `[PAD]` 忽略，软模板失效 | `get_attention_mask` 按 `id > 0` 重新生成 | **只要手工往序列插了 token，就必须重算 attention_mask**；这类 bug 不报错、只掉点，最耗时间 |
| `mask_position` 全部偏移，预测全错 | 伪 token 插在前面后 `[MASK]` 实际位置整体右移 | `mask_positions = [len(p_tokens_ids) + start_mask_position + i ...]` | 位置一律**从最终 input_ids 反查**（像 PET 用 `np.where`），不要手算偏移 |
| 报 `Lable Error: "xxx" not in label_dict` | 模型的预测词不在 verbalizer 表里 | 传 `hard_mapping=True` 走最长公共子串兜底 | 映射表要覆盖"主标签 + 常见子标签 + 主标签自身" |
| 推理结果总是返回"无" | `hard_mapping=False`，或主标签没把自己列进子标签 | 打开 `hard_mapping`；确保 `主标签\t主标签,子标签1,...` | 建表时自查：`find_main_label(主标签)` 是否等于主标签本身 |
| `ValueError: too many values to unpack` | 评论内容含制表符，`split('\t')` 切出 3 段以上 | `split('\t', 1)` 限制只切一刀 | 解析"标签 + 自由文本"格式时**永远限制 split 次数** |
| 训练 loss 不降，或某些类别 loss 天然偏高 | `mlm_loss` 里没除以 `len(sub_mask_labels)`，子标签多的类别 loss 被放大 | `cur_loss = cur_loss / len(single_sub_mask_labels)` | 变长目标做加权平均前一律先按个数归一化 |
| 换了模板后准确率掉 20 个百分点 | PET 的硬模板本身不稳定 | 尝试多个模板取最优；或改用 P-Tuning 软模板 | 硬模板的效果对写法极度敏感，**必须当超参数来调** |
| 标签是 3 个字时被截断，永远预测不对 | `max_label_len=2` 只留 2 个 `[MASK]` | 按数据集里最长的标签词设置 `max_label_len` | 设值前先统计所有子标签的长度分布 |
| 伪 token 数量改大后报错 | `[unused]` 只有 99 个，且必须与 `p_embedding_num` 匹配 | `p_embedding_num ≤ 99`，且 `[unused1]`..`[unusedN]` 要连续 | 用 `[unused]` 做软模板前先确认词表有多少可用空位 |
| 训到最后一个 checkpoint 效果反而变差 | 小样本训练波动大，最后一步未必最好 | 每个 `valid_steps` 评估，保存 **F1 最优**的 `model_best` | 小样本场景**必须按验证指标选模型**，不能默认用最后一个 |
| `datasets` 映射时异常样本被静默跳过 | 代码里用了裸 `except: continue` | 至少打印被跳过的样本 | 静默跳数据会让"训练集 63 条"实际只有 50 条参与，且你毫无感知 |

## 6. 可复用经验

1. **Prompt-Tuning 的本质是"任务对齐"。** 分类任务和 BERT 预训练的 MLM 目标本来不同，PET/P-Tuning 通过改写输入把两者统一起来，从而复用预训练学到的全部知识，不引入随机初始化参数。**任何"下游任务和预训练目标差距大"的场景，都值得想一想能不能用 prompt 把它拉回来。**
2. **小样本场景的评估要看"每类指标"，不能只看平均准确率。** 10 个类别、63 条训练样本，一个类别错 30 条对平均准确率影响可能只有 0.5%，但对那个类别的业务可能是灾难。
3. **手工往序列里插 token 时，`attention_mask` 和位置索引都必须重算。** 这是 P-Tuning 实现里最容易错的两处，且错了不报错、只掉点。判断原则：**只要你对 `input_ids` 做了任何编辑，就要重新推导所有依赖它的量。**
4. **Verbalizer 的映射表有最小完备性要求。** 主标签必须在自己的子标签列表里（否则反查会走兜底），子标签要覆盖模型可能输出的同义词，还要有 `hard_mapping` 兜底保证永不崩溃。
5. **变长目标求 loss 一定要归一化。** 子标签个数不同、标签长度不同、padding 不同——任何"变长"都可能引入隐式权重。除以个数、除以 token 数，是消除这类偏差的通用手段。
6. **"硬模板 vs 软模板"的取舍可以推广到很多地方。** 硬模板（人工规则）可读、可解释、无新增参数，但不稳定、无法全局优化；软模板（可学习参数）灵活、可优化，但引入新参数、需要更多数据和算力，还损失可解释性。这个权衡在规则引擎 vs 模型、特征工程 vs 端到端学习里反复出现。
7. **用 `[unused]` token 做软模板，是最省事的"不改模型结构"方案。** 不用扩词表、不用改 config、不用重载权重，代价是受限于词表空位数量——工程上足够，但有边界。
8. **注释里"这行不修改位置（结果指标较低）"这类记录，价值高于代码本身。** 它把"为什么这么写"和"改成别的会怎样"一起留下来了。

## 7. 面试问答

<details>
<summary><b>Q1：PET 和 P-Tuning 的区别是什么？为什么它们在少样本上比传统 Fine-tuning 好？</b></summary>

**共同点**：两者都把分类任务转成"预测 `[MASK]` 位置该填什么词"，用 `AutoModelForMaskedLM`，不引入随机初始化的分类头。区别只在模板：

- **PET（硬模板）**：人工写自然语言模板 `这是一条[MASK][MASK]评论：{textA}。`，模板是**真实的 token**，进模型前的序列你能一眼读出来。
- **P-Tuning（软模板）**：模板是**可学习的连续向量**。实现上先用 `[unused1]`~`[unused6]` 占位，插在 `[CLS]` 前面，这些位置的 embedding 在训练中被更新，最终学到一个人看不懂、但机器觉得更好的"伪模板"。

**为什么少样本更好，三个原因**：

1. **不引入新的随机初始化参数。** `BertForSequenceClassification` 会加一个 `Linear(768, num_labels)` 分类头，63 条样本训 768×10 个新参数，梯度信号严重不足。PET/P-Tuning 全程只用已有的 MLM 头，参数已在海量语料上训好。
2. **任务对齐（task alignment）。** BERT 预训练目标就是"补 `[MASK]`"，PET 让它继续做同一件事。传统 Fine-tuning 则要求模型从"语言建模"切换到"分类判别"，中间隔着一次表征空间适配，小样本下适配不过来。
3. **标签词映射引入了先验知识。** 传统分类里"第 3 类"对模型毫无语义；PET 里它对应"掉色、起球、衣服"这些真实词汇，模型已有丰富语义理解。`"这件衣服掉色严重"是一则[MASK][MASK]评论。` 预测"衣服"很难，预测"掉色"就容易得多。

**各自的代价**：PET 的硬模板**极度依赖写法**（文档明说不同模板准确率可差近 20 个百分点），且无法全局优化；P-Tuning 引入可学习参数、需要更多训练步数（本项目 50 epoch），而且在**超多分类任务**和**句子蕴含任务**上效果不理想——模板能表达的信息量有限，任务越复杂越难靠几个伪 token 承载。

**什么时候不用它们**：样本量充足（几万条以上）时，传统 Fine-tuning 更简单、更稳定、推理更快（PET 推理时也要构造模板 + Verbalizer 反查，工程复杂度更高）。**Prompt-Tuning 是"小样本"场景的特效药，不是通用替代品。**

</details>

<details>
<summary><b>Q2：Verbalizer 是做什么的？为什么不能直接用类别名做标签？</b></summary>

**Verbalizer 做的是"真实标签 → 标签预测词"的映射**，在训练和推理两端各用一次：

- **训练时**把主标签展开成一组子标签的 token ids，作为 MLM 的软目标。"水果" → `['苹果','香蕉','橘子']`，`mlm_loss` 把 `[MASK]` 位置的 logits 复制 3 份分别算交叉熵——**只要预测中其中任何一个，loss 都低**。
- **推理时**通过 `find_main_label` 把模型输出的 token 反查回主标签。命中子标签直接返回；没命中就走 `hard_mapping`（最长公共子串）兜底。

**为什么不能直接用类别名**，三个层面：

1. **语义通顺性。** 模板是 `这是一条[MASK][MASK]评论：...`。"这是一条**水果**评论"读起来别扭，"这是一条**苹果**评论"就通顺得多。MLM 是在自然语言上下文里预测，**上下文越通顺，预测越准**。电商评论的例子更清楚：`"这件衣服掉色严重"是一则[MASK][MASK]评论。` 填"掉色"远比填"衣服"自然。
2. **预测难度。** 有些类别名本身在预训练语料里出现频率低、语义模糊（如"洗浴""蒙牛"），模型很难把它当作"从上下文推断出来的词"；子标签可以选更常见、更具体的词。
3. **一对多的表达能力。** 一个类别往往有多种表达。用类别名只能对应一个词；有了 Verbalizer，"水果"可同时对应"苹果/香蕉/橘子"，**大幅提高命中的容错率**——模型只要预测出任一个就能正确归类。这是小样本下很实用的"标签平滑"效果。

**实现上的一个坑**：`verbalizer.txt` 里必须把主标签自己也写进子标签列表（`水果\t水果`）。因为评估时的 gold 是原始标签词"水果"，如果反查表里没有它，`find_main_label('水果')` 会走到 `hard_mapping` 兜底，结果可能碰巧对也可能错——莫名其妙且不稳定。

**更进阶的做法**：Verbalizer 的构建本身可以自动化。用 LLM 为每个类别生成候选标签词，再用验证集表现筛选最优的那一个（**Automatic Verbalizer Search**）。手工构建的 Verbalizer 是最优解的前提，实践中往往不是。

</details>

<details>
<summary><b>Q3：P-Tuning 里为什么 attention_mask 要重新计算？手工插入伪 token 有什么风险？</b></summary>

**直接原因**：`tokenizer` 返回的 `attention_mask` 是它根据自己的逻辑生成的——**它不知道你后面手工往序列前面塞了几个 token**。当你在 `input_ids` 前面插入伪 token 后：

```text
tokenizer 给的 mask: [ ... ] ← 只覆盖它自己生成的 token
实际 input_ids: [1,2,3,4,5,6, 101, 103, 103, ...正文..., 102, 0,0,0]
 └─ 伪token ─┘
```

如果直接沿用 tokenizer 的 mask，伪 token 位置会被标成 0，模型在自注意力里**直接忽略它们**——软模板等于没插，而且**不会报任何错**。

代码里的做法是按 `id > 0` 重新生成：

```python
def get_attention_mask(alist):
 return np.where(np.array(alist) > 0, 1, 0).tolist
```

**这里有个必须说清的细节**：中文 BERT 里 `[PAD]` 是 id 0，而 `[unused1]`~`[unused6]` 是 id 1~99，所以 `> 0` 能把伪 token 保留下来、只把真 padding 排除掉。**但这是依赖了"`[unused*]` 的 id 不为 0"这个隐式约定**——如果哪个模型的 `[unused*]` 恰好是 0，这套逻辑就会失效。更稳的写法是**显式基于序列长度构造 mask**：

```python
seq_len = len(input_ids)
attention_mask = [1] * seq_len + [0] * (max_seq_len - seq_len)
```

**手工插入 token 的风险清单**（这是这类操作的共性）：

1. **mask 错**：伪 token 被当 padding 忽略。表现是"能训、不报错、效果差"——最难查的一类。
2. **位置错**：`[MASK]` 位置因整体右移而算错，取 logits 时取到了别的位置。表现是"loss 完全不降"。
3. **长度溢出**：插入的 token 挤掉正文，或超过 `max_seq_len` 被截断，导致 `[SEP]` 或 `[MASK]` 丢失。表现是"标签预测永远错"。
4. **类型 id 错**：`token_type_ids` 没跟着补长度，与 `input_ids` 长度不一致，直接报形状错误（这个反而最好查）。

**通用防错原则**：**任何对 `input_ids` 的编辑，都必须同步重新推导 mask、position、length 三个量。** 而且优先用"从最终 `input_ids` 反查"（如 PET 用 `np.where(input_ids == mask_token_id)`）而不是"手算偏移量"——反查天然正确，手算一定会随代码改动而失配。

</details>

## 8. 延伸阅读

- 《Exploiting Cloze Questions for Few Shot Text Classification and Natural Language Inference》（PET 原始论文，Schick & Schütze, 2021）
- 《GPT Understands, Too》（P-Tuning 原始论文，Liu et al., 2021）
- 《How Can We Know What Language Models Know?》（LAMA / Automatic Verbalizer Search）
- HuggingFace 文档：`AutoModelForMaskedLM`、`AutoTokenizer`、`get_scheduler`、`datasets.map(batched=True)`
- 本仓库同目录：[08-项目-新闻文本分类三方案对比](08-项目-新闻文本分类三方案对比（随机森林FastTextBERT）.md)（大样本下的传统方案对比）
- 配套代码：`PET/data_handle/template.py`、`PET/utils/verbalizer.py`、`PET/utils/common_utils.py`、`P-Tuning/data_handle/data_preprocess.py`、`P-Tuning/train.py`

---
[⬅️ 返回本目录索引](README.md)
