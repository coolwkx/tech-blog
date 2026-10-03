# 12 NLP 项目实战：医疗文本分类

> **一句话总结**：把「随机森林 → FastText → BERT」三档模型跑在同一份医疗问句数据上，用指标对比回答「这个业务到底该用哪个模型」。
> **前置知识**：第 03 篇 TF-IDF、第 05 篇文本分类流水线与评估指标、第 09 篇 BERT 微调、第 11 篇情感分析项目的工程范式。

> 1. 独立完成一个 13 类医疗问句分类项目：领域预处理 → 三档模型 → 多指标对比 → 混淆矩阵分析 → 改进方案。
> 2. 针对医疗文本设计领域适配的清洗、分词与词典策略，并说清每次改动为什么可能有效。
> 3. 用「精度/延迟/模型体积」三维度给出模型选型结论，并写出可上线的服务封装。

## 1. 核心概念

### 1.1 业务场景与为什么值得做

智慧医疗领域每天产生海量医疗咨询文本：患者在线问诊、医生病历记录、医学文献、药品说明书。核心需求有四类：

| 需求 | 说明 | 技术形态 |
|------|------|----------|
| 自动分类 | 把问题归到「病因 / 治疗方法 / 临床表现」等类别 | 文本多分类 |
| 智能分诊 | 按问题类型分配给对应科室医生 | 分类 + 路由 |
| 知识检索 | 找到相似病例与治疗方案 | 语义检索（第 10 篇） |
| 辅助诊断 | 基于历史数据给建议 | 分类 + 检索 + 生成 |

以项目中的真实样本为例：

```
患者提问：「睡一觉醒睡不着咋搞的？现在怀孕7个月了」
 ↓
模型预测：病因（label_id = 1）
 ↓
系统动作：1) 推送给妇产科医生 2) 检索「孕期失眠」相关案例
 3) 提供常见原因：激素变化、尿频、焦虑等
```

这个例子也说明了任务的价值：**分类结果直接驱动下游动作**（路由、检索、回复模板），因此分类错误的代价不是「一个数字掉点」，而是「患者被推给错误科室」。

### 1.2 数据集：13 类标签体系

| ID | 类别名称 | 示例问题 |
|----|----------|----------|
| 0 | 定义 | 什么是骨纤维瘤 |
| 1 | 病因 | 新生儿恶心的原因 |
| 2 | 预防 | 如何预防丘脑胶质瘤 |
| 3 | 临床表现（病症表现） | 请问出血性脑梗死症状是什么 |
| 4 | 相关病症 | 心脏病会引发癫痫吗 |
| 5 | 治疗方法 | 肾结石一般用什么药 |
| 6 | 所属科室 | 肢端纤维角化瘤应该看啥医生 |
| 7 | 传染性 | 甲真菌病容易感染不 |
| 8 | 治愈率 | 先天性外展性髋挛缩治愈比例 |
| 9 | 禁忌 | 阿立哌唑片对人有哪些危害 |
| 10 | 化验/体检方案 | 距骨骨折脱位做啥检查 |
| 11 | 治疗时间 | 艾滋病神经系统损害治好要多少天 |
| 12 | 其他 | 婴儿会有痔疮吗 |

| 数据集 | 样本数 | 用途 |
|--------|--------|------|
| 训练集 | 7273 条 | 模型训练 |
| 测试集 | 809 条 | 性能评估 |

**这份标签体系的本质是「问句意图分类」**：13 个类别对应患者提问的 13 种意图。这一点对建模很关键——区分类别的信号主要来自**疑问词与句式**，而不是疾病名称：

| 样本 | 关键特征词 | 对应类别 |
|------|-----------|----------|
| 肾结石，输尿管结石一般用什么药呢而且效果较好？ | 「什么药」「效果较好」 | 治疗方法 |
| 睡一觉醒睡不着咋搞的？现在怀孕7个月了 | 「咋搞的」「睡不着」 | 病因 |
| 请问出血性脑梗死症状是什么 | 「症状是什么」 | 临床表现 |

三类样本都含疾病名（「肾结石」「睡不着」「脑梗死」），但**疾病名对区分意图几乎无用**——同一个病名可以问病因、问治疗、问症状。真正起作用的是「什么药 / 咋搞的 / 症状是什么」这些**提问方式**。这是本项目最重要的建模洞察。

### 1.3 直观的困难点

| 困难 | 例子 | 影响 |
|------|------|------|
| 类别间语义重叠 | 「病因」与「相关病症」；「治疗方法」与「治疗时间」 | 混淆矩阵会出现明显热点 |
| 口语化、错别字多 | 「咋搞的」「睡不着咋办」「看啥医生」 | 通用分词器与词表覆盖不足 |
| 问句极短 | 平均长度只有十几个字 | 特征稀疏，模型容易欠拟合 |
| 专业术语多 | 「肢端纤维角化瘤」「先天性外展性髋挛缩」 | 分词被切碎，OOV 严重 |
| 多意图混杂 | 「肾结石用什么药，多久能好」 | 单标签分类无法表达，应考虑多标签 |
| 类别不均衡 | 各类样本数不同 | accuracy 会失真，需看 macro-F1 |

## 2. 方法细节

### 2.1 领域预处理四步流水线

实现里封装了一个 `MedicalTextPreprocessor` 类，流程是「清洗 → 分词 → 去停用词 → 拼接」：

```
原始文本 → 清洗 → jieba 分词 → 去停用词 → 空格拼接
```

**第 1 步：清洗**

```python
def clean_text(self, text):
    """只保留中文字符（\u4e00-\u9fa5），其余替换为空格"""
    if not isinstance(text, str):
        return ""
    text = re.sub(r'[^\u4e00-\u9fa5]', ' ', text) # 非中文 -> 空格
    return re.sub(r'\s+', ' ', text).strip() # 合并多余空格
```

清洗效果：

```
输入: "肾结石，输尿管结石一般用什么药呢？而且效果较好！123"
步骤1: "肾结石 输尿管结石一般用什么药呢 而且效果较好 "
输出: "肾结石 输尿管结石一般用什么药呢 而且效果较好"
```

| 去除内容 | 原因 | 示例 |
|----------|------|------|
| 标点符号 | 对语义影响小 | ，。！？ |
| 数字 | 医疗文本中数字多为剂量，需特殊处理 | 123、5mg |
| 英文字母 | 中文分类任务通常不需要 | ABC、CT |
| 特殊符号 | 无意义噪声 | @#$% |

> **必须指出这个清洗方式的风险**：`[^\u4e00-\u9fa5]` 会**丢掉所有英文缩写**，而医疗领域大量关键信息正是英文缩写——「CT检查」「MRI」「DNA」「B超」「ICU」。把「CT」删掉后，「距骨骨折脱位做啥检查」和「做CT检查」的特征会趋同，伤害「化验/体检方案」这一类的判别。改进写法：

```python
# 保留中文 + 英文 + 数字（去掉纯标点与特殊符号）
text = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', ' ', text)
# 或只保留常见的医学缩写白名单：CT / MRI / B超 / DNA / ICU / X线 ...
```

**第 2 步：jieba 分词**

```python
def segment_text(self, text):
 return jieba.lcut(text)
```

jieba 基于统计分词：构建词典 → 计算词概率 → 选概率最大的切分组合。它能正确识别「肾结石」（而不是切成「肾」+「结石」）和「输尿管」，**但医学长术语仍常被切碎**。改进手段是加载医学自定义词典：

```
# medical_dict.txt 格式：词语 词频 词性
肾结石 100 n
输尿管 100 n
心肌梗死 100 n
肢端纤维角化瘤 100 n
出血性脑梗死 100 n
```

```python
jieba.load_userdict('medical_dict.txt')
```

**第 3 步：去停用词**

```python
def remove_stopwords(self, words):
 return [w for w in words if w.strip() and w not in self.stopwords]
```

停用词表前 20 个示例：的、了、在、是、我、有、和、就、不、人、都、一、一个、上、也、很、到、说、要、去。

过滤效果：

```
输入: ["肾结石", "的", "治疗", "方法", "是", "什么", "呢"]
输出: ["肾结石", "治疗", "方法"] （的 / 是 / 什么 / 呢 被过滤）
```

> **停用词表对本项目有一个严重风险**：「什么」「怎么」「如何」「为啥」这类**疑问词**在通用停用词表里往往被当作高频无意义词删掉，但它们恰恰是判断意图的核心信号！「什么药」→ 治疗方法，「什么症状」→ 临床表现，「怎么预防」→ 预防。如果「什么」被删了，「什么药」和「什么症状」就只剩「药」和「症状」——虽然还能区分，但信号被削弱了。正确做法是**把疑问词从停用词表中移出**，或加入白名单。

**第 4 步：拼接**

```python
def preprocess(self, text):
 cleaned = self.clean_text(text) # 清洗
 segmented = self.segment_text(cleaned) # 分词
 filtered = self.remove_stopwords(segmented) # 去停用词
 return ' '.join(filtered) # 空格拼接，供给向量化器
```

完整流程实例：

```
"肾结石，输尿管结石一般用什么药呢？"
 → 清洗: "肾结石 输尿管结石一般用什么药呢"
 → 分词: ["肾结石", "输尿管", "结石", "一般", "用", "什么", "药", "呢"]
 → 去停用词: ["肾结石", "输尿管", "结石", "一般", "用", "药"]
 → 拼接: "肾结石 输尿管 结石 一般 用 药"
```

### 2.2 三档模型与超参

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

### 2.3 训练与预测的关键实现

```python
class MedicalTextDataset(Dataset):
    def __getitem__(self, idx):
        encoding = self.tokenizer(
        str(self.texts[idx]),
        add_special_tokens=True, # 自动加 [CLS] 与 [SEP]
        max_length=self.max_length, # 128
        padding='max_length',
        truncation=True,
        return_tensors='pt',
    )
    return {
'input_ids': encoding['input_ids'].flatten,
'attention_mask': encoding['attention_mask'].flatten,
'labels': torch.tensor(self.labels[idx], dtype=torch.long),
}
```

预测时两个必须动作：

```python
self.model.eval # 切换到评估模式，关闭 dropout
with torch.no_grad: # 不计算梯度，省显存
 outputs = self.model(**inputs)
 probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
 pred = torch.argmax(probs, dim=-1).item
```

### 2.4 评估：四大指标与多分类平均方式

| 指标 | 公式 | 含义 |
|------|------|------|
| Accuracy | $(TP+TN)/N$ | 预测正确的比例 |
| Precision | $TP/(TP+FP)$ | 预测为某类的样本里，真正属于该类的比例 |
| Recall | $TP/(TP+FN)$ | 真实为某类的样本里，被正确预测的比例 |
| F1 | $2PR/(P+R)$ | 精确率与召回率的调和平均 |

以「治疗方法」类为例：真实有 100 条该类问题；模型预测为「治疗方法」的 90 条中有 80 条正确（TP=80, FP=10），漏掉了 20 条（FN=20）。则

$$P=\frac{80}{90}=0.89,\qquad R=\frac{80}{100}=0.80,\qquad F_1=\frac{2\times0.89\times0.80}{0.89+0.80}=0.84$$

多分类的平均方式：

| 方式 | 做法 | 什么时候用 |
|------|------|-----------|
| `macro` | 各类指标**先算再简单平均** | 各类同等重要；类别不均衡时最能暴露小类问题 |
| `weighted` | 按**该类样本数**加权平均 | 关心整体但考虑类别占比 |
| `micro` | 先把 TP/FP/FN 加总再算 | 单标签多分类下 micro-F1 ≡ accuracy |

**混淆矩阵**是错误分析的核心工具。某项目的混淆矩阵片段（行 = 真实，列 = 预测）：

```
 病因 治疗 其他
真实 病因 [ 85 10 5 ]
 治疗 [ 8 90 2 ]
 其他 [ 3 5 92 ]
```

读法：对角线是正确预测；非对角线是错误。"病因」有 10 条被误判为「治疗」，可能是因为问题同时包含病因与治疗（如「为什么用这个药」）。由此可以得出三个动作：① 找出哪些类别容易混；② 定位模型弱点；③ 判断是否需要合并类别或改成多标签。

### 2.5 三档模型的预期性能对比

| 模型 | 准确率 | 精确率 | 召回率 | F1 | 训练时间 | 是否需要 GPU |
|------|--------|--------|--------|-----|----------|-------------|
| Random Forest | 0.82–0.85 | 0.83 | 0.82 | 0.82 | ~5 分钟 | 否 |
| FastText | 0.86–0.89 | 0.87 | 0.86 | 0.86 | ~10 分钟 | 否 |
| BERT | 0.90–0.93 | 0.91 | 0.90 | 0.90 | ~30 分钟 | 强烈推荐 |

各模型的优缺点：

| 模型 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| 随机森林 | 训练快、可解释（特征重要性）、不需 GPU、适合小数据 | 无法理解语义、特征维度受限、对同义词不敏感 | 快速原型、资源受限、需要解释性 |
| FastText | 训练效率高、支持 n-gram 与子词、模型小、推理快 | 上下文理解有限、不如 BERT 精度高 | 大规模数据、实时性要求高、平衡效率与精度 |
| BERT | 精度最高、上下文理解强、泛化好 | 训练慢、需 GPU、体积大、推理慢 | 追求最高精度、资源充足、医疗等专业领域 |

### 2.6 延伸：模型压缩三件套

如果业务要求「BERT 的精度 + FastText 的速度」，就需要压缩。参考项目本主题覆盖了三种手段：

| 手段 | 核心思想 | 关键 API / 公式 |
|------|----------|----------------|
| 知识蒸馏 | 让学生模型（TextCNN）学教师模型（BERT）的**软标签** | $\text{loss}=\alpha\cdot\text{hard}+\beta\cdot\text{soft}$，软标签用 KL 散度 + 温度 $T$ |
| 模型量化 | 把 FP32 权重压成 INT8 | 动态量化 `torch.quantization.quantize_dynamic` |
| 模型剪枝 | 把绝对值小的权重置 0 | `prune.l1_unstructured` / `prune.ln_structured` / `prune.remove` |

**知识蒸馏的直觉**（为什么软标签比硬标签有信息量）：

```
传统训练（只用硬标签）：真实标签 = 治疗方法(1)
 学生只学到「这是治疗方法」

蒸馏训练（用软标签）：教师输出 = 治疗方法(0.75), 病因(0.08), 临床表现(0.05)...
 学生额外学到：① 治疗方法与病因有一定相似性（可能在问「为什么用这个药」）
 ② 类别之间的关系结构
 → 泛化更好
```

蒸馏的收益量化举例：1 亿次分类请求下，纯 BERT（50ms/次）需要约 58 天，纯 TextCNN（5ms/次）只需约 5.8 天但准确率只有 90%；蒸馏后的 TextCNN 达到 92.5% 且保持 5ms——**同时兼顾性能与效率**。

剪枝的 API 要点：

```python
import torch.nn.utils.prune as prune

prune.l1_unstructured(module, name="weight", amount=0.3) # 去掉绝对值最小的 30%
prune.ln_structured(module, name="weight", amount=0.4, n=2, dim=0) # 结构化剪枝
prune.remove(module, "weight") # 永久化：把 weight_orig × weight_mask 写回 weight
```

项目源码还演示了两种更进一步的用法：

```python
# 全局剪枝：在所有层之间统一按重要性排名剪掉 20%（各层被剪比例不同）
parameters_to_prune = (
(model.conv1, 'weight'), (model.conv2, 'weight'),
(model.fc1, 'weight'), (model.fc2, 'weight'), (model.fc3, 'weight'),
)
prune.global_unstructured(parameters_to_prune,
pruning_method=prune.L1Unstructured, amount=0.2)
# 随后可逐层统计稀疏度并与全局比例核对

# 自定义剪枝规则：继承 prune.BasePruningMethod 并实现 compute_mask
class MyPruningMethod(prune.BasePruningMethod):
    PRUNING_TYPE = "unstructured"

    def compute_mask(self, t, default_mask):
        mask = default_mask.clone
        mask.view(-1)[::3] = 0 # 每 3 个参数遮掉 1 个
        return mask
```

剪枝后模块会新增 `weight_orig`（原始权重）与 `weight_mask`（0/1 掩码），实际使用的是两者相乘的结果。**不调用 `prune.remove` 就不会真正减小模型**——这是最常见的误解。

## 3. 可运行示例

### 3.1 领域预处理流水线（自包含）

```python
# 依赖: pip install jieba pandas numpy
import re
import numpy as np
import pandas as pd
import jieba

# 加载医学自定义词典（实际项目从文件加载）
for term in ["肾结石", "输尿管", "心肌梗死", "出血性脑梗死", "肢端纤维角化瘤"]:
    jieba.add_word(term)

    # 通用停用词表
    STOPWORDS = set("的 了 在 是 我 有 和 就 都 也 很 只 要 一个 上 到 说".split())
    # 关键修正：疑问词必须保留！它们是判断意图的核心信号
    QUESTION_WORDS = {"什么", "怎么", "如何", "为啥", "咋", "为什么", "哪", "多久", "多少"}

    class MedicalTextPreprocessor:
        def __init__(self, stopwords=None, keep_english=True):
            self.stopwords = set(stopwords) if stopwords else STOPWORDS
            self.keep_english = keep_english

            def clean_text(self, text):
                if not isinstance(text, str):
                    return ""
                if self.keep_english:
                    # 保留中文 + 英文 + 数字（避免丢掉 CT / MRI / B超 等关键缩写）
                    text = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', ' ', text)
                else:
                    text = re.sub(r'[^\u4e00-\u9fa5]', ' ', text)
                    return re.sub(r'\s+', ' ', text).strip()

                def remove_stopwords(self, words):
                    return [w for w in words
                if w.strip() and (w in QUESTION_WORDS or w not in self.stopwords)]

                def preprocess(self, text):
                    cleaned = self.clean_text(text)
                    segmented = jieba.lcut(cleaned)
                    filtered = self.remove_stopwords(segmented)
                    return ' '.join(filtered)

                def preprocess_dataframe(self, df, text_column='text'):
                    df = df.copy
                    df['cleaned_text'] = [self.preprocess(t) for t in df[text_column]]
                    lengths = [len(t.split()) for t in df['cleaned_text'] if t]
                    if lengths:
                        print("预处理完成，平均长度 {:.1f} 个词，最长 {}，最短 {}".format(
                        float(np.mean(lengths)), max(lengths), min(lengths)))
                        return df

                    if __name__ == "__main__":
                        pre = MedicalTextPreprocessor

                        samples = [
                        "肾结石，输尿管结石一般用什么药呢？而且效果较好！123",
                        "请问出血性脑梗死症状是什么",
                        "睡一觉醒睡不着咋搞的？现在怀孕7个月了",
                        "距骨骨折脱位做啥检查，需要做CT吗",
                        "肢端纤维角化瘤应该看啥医生",
                        ]
                        for s in samples:
                            print(f"原文: {s}")
                            print(f"清洗: {pre.clean_text(s)}")
                            print(f"最终: {pre.preprocess(s)}\n")

                            df = pd.DataFrame({"text": samples, "label_class": ["治疗方法", "临床表现", "病因", "化验/体检方案", "所属科室"]})
                            df = pre.preprocess_dataframe(df)
                            print(df[["cleaned_text", "label_class"]].to_string(index=False))
```

注意输出中「CT」被保留、疑问词「什么 / 咋 / 多久」也被保留——这两点正是对原始实现的两处修正。

### 3.2 三档模型端到端对比（自包含小样本）

```python
# 依赖: pip install scikit-learn jieba numpy
import re
import jieba
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

# ---------- 内联构造 13 类医疗问句语料（实际项目换成 train.csv / test.csv） ----------
DATA = [
 ("什么是骨纤维瘤", 0), ("什么是心肌梗死", 0), ("什么叫高血压", 0),
 ("新生儿恶心的原因", 1), ("睡一觉醒睡不着咋搞的", 1), ("小儿发烧是什么引起的", 1),
 ("如何预防丘脑胶质瘤", 2), ("怎么预防糖尿病", 2), ("怎样预防高血压", 2),
 ("请问出血性脑梗死症状是什么", 3), ("心脏病有哪些表现", 3), ("肺炎的症状表现", 3),
 ("心脏病会引发癫痫吗", 4), ("高血压会引起头晕吗", 4),
 ("肾结石一般用什么药", 5), ("输尿管结石怎么治疗效果好", 5), ("脑梗死如何治疗", 5),
 ("肢端纤维角化瘤应该看啥医生", 6), ("失眠挂哪个科室", 6),
 ("甲真菌病容易感染不", 7), ("肺结核传染性强吗", 7),
 ("先天性外展性髋挛缩治愈比例", 8), ("肺癌的治愈率有多高", 8),
 ("阿立哌唑片对人有哪些危害", 9), ("孕期能不能吃这个药", 9),
 ("距骨骨折脱位做啥检查", 10), ("需要做CT还是核磁", 10), ("化验血糖要空腹吗", 10),
 ("艾滋病神经系统损害治好要多少天", 11), ("骨折要多久能恢复", 11),
 ("婴儿会有痔疮吗", 12), ("小孩打呼噜正常吗", 12),
] * 4 # 每条重复 4 次，共 128 条

STOPWORDS = set("的 了 在 是 我 有 和 就 也 很 只 要 一个 上 到 说".split())
QUESTION_WORDS = {"什么", "怎么", "如何", "咋", "多久", "多少", "哪"}

def preprocess(text):
 text = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', ' ', text)
 words = jieba.lcut(text)
 return ' '.join(w for w in words
 if w.strip() and (w in QUESTION_WORDS or w not in STOPWORDS))

df = pd.DataFrame(DATA, columns=["text", "label"])
df["words"] = df["text"].apply(preprocess)

X_train, X_test, y_train, y_test = train_test_split(
 df["words"], df["label"], test_size=0.25, random_state=42, stratify=df["label"]
)

results = []

# ---------- 第 1 档：TF-IDF + 随机森林 ----------
vec = TfidfVectorizer(max_features=5000, token_pattern=r'(?u)\b\w+\b',
 lowercase=False, ngram_range=(1, 2))
Xtr, Xte = vec.fit_transform(X_train), vec.transform(X_test)

rf = RandomForestClassifier(n_estimators=200, max_depth=20, random_state=42, n_jobs=-1)
rf.fit(Xtr, y_train)
pred_rf = rf.predict(Xte)
results.append(("RandomForest + TF-IDF",
 accuracy_score(y_test, pred_rf),
 f1_score(y_test, pred_rf, average="macro")))

# ---------- 第 1 档的对照：线性模型（医疗小数据上常优于 RF） ----------
lr = LogisticRegression(max_iter=1000, C=5.0, multi_class="multinomial")
lr.fit(Xtr, y_train)
pred_lr = lr.predict(Xte)
results.append(("LogisticRegression + TF-IDF",
 accuracy_score(y_test, pred_lr),
 f1_score(y_test, pred_lr, average="macro")))

# ---------- 特征重要性（解释「模型学到了什么」） ----------
names = np.array(vec.get_feature_names_out)
top = names[np.argsort(rf.feature_importances_)[-10:]][::-1]
print("随机森林 Top-10 重要特征:", list(top))

# ---------- 混淆矩阵 ----------
from sklearn.metrics import confusion_matrix, classification_report
print("\n逐类报告（随机森林）:")
print(classification_report(y_test, pred_rf, digits=3, zero_division=0))

# ---------- 结果汇总 ----------
print("\n模型对比:")
print(f"{'模型':<32}{'accuracy':>10}{'macro-F1':>10}")
for name, acc, f1 in results:
 print(f"{name:<32}{acc:>10.4f}{f1:>10.4f}")
```

把内联数据换成项目真实数据（`pd.read_csv("train.csv")`，列名为 `text` / `label_id` / `label_class`）即可得到与 2.5 节一致的对比结论。

### 3.3 BERT 微调与推理（含保存/加载）

```python
# 依赖: pip install transformers torch
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from transformers import (AutoTokenizer, AutoModelForSequenceClassification,
AdamW, get_linear_schedule_with_warmup)

MODEL_NAME = "bert-base-chinese"
MAX_LEN = 128
NUM_LABELS = 13
device = torch.device("cuda" if torch.cuda.is_available else "cpu")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

class MedicalTextDataset(Dataset):
    def __init__(self, texts, labels):
        self.texts, self.labels = texts, labels

        def __len__(self):
            return len(self.texts)

        def __getitem__(self, idx):
            enc = tokenizer(str(self.texts[idx]), add_special_tokens=True,
            max_length=MAX_LEN, padding="max_length",
            truncation=True, return_tensors="pt")
            return {
        "input_ids": enc["input_ids"].flatten,
        "attention_mask": enc["attention_mask"].flatten,
        "labels": torch.tensor(self.labels[idx], dtype=torch.long),
        }

        def train_model(texts, labels, epochs=3, batch_size=8, lr=2e-5):
            model = AutoModelForSequenceClassification.from_pretrained(
            MODEL_NAME, num_labels=NUM_LABELS).to(device)
            loader = DataLoader(MedicalTextDataset(texts, labels), batch_size=batch_size, shuffle=True)

            optimizer = AdamW(model.parameters(), lr=lr, weight_decay=0.01)
            total_steps = len(loader) * epochs
            scheduler = get_linear_schedule_with_warmup(
            optimizer, num_warmup_steps=int(0.1 * total_steps), num_training_steps=total_steps)
            criterion = nn.CrossEntropyLoss

            for epoch in range(epochs):
                model.train
                total_loss = 0.0
                for batch in loader:
                    batch = {k: v.to(device) for k, v in batch.items()}
                    outputs = model(input_ids=batch["input_ids"],
                    attention_mask=batch["attention_mask"])
                    loss = criterion(outputs.logits, batch["labels"])
                    optimizer.zero_grad()
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0) # 梯度裁剪
                    optimizer.step
                    scheduler.step
                    total_loss += loss.item
                    print(f"epoch {epoch + 1} loss={total_loss / len(loader):.4f}")

                    # 保存与加载：只存 state_dict，换机器时用 map_location 处理设备
                    torch.save(model.state_dict, "medical_bert.bin")
                    return model

                def predict(model, text, id_to_name=None):
                    model.eval
                    enc = tokenizer(text, add_special_tokens=True, max_length=MAX_LEN,
                    padding="max_length", truncation=True, return_tensors="pt")
                    enc = {k: v.to(device) for k, v in enc.items()}
                    with torch.no_grad:
                        logits = model(**enc).logits
                        probs = torch.softmax(logits, dim=-1)[0]
                        pred_id = int(probs.argmax)
                        return (id_to_name[pred_id] if id_to_name else pred_id), float(probs[pred_id])

                    if __name__ == "__main__":
                        texts = ["什么是骨纤维瘤", "肾结石一般用什么药", "睡一觉醒睡不着咋搞的",
                        "请问出血性脑梗死症状是什么", "距骨骨折脱位做啥检查"] * 8
                        labels = [0, 5, 1, 3, 10] * 8

                        id_to_name = {0: "定义", 1: "病因", 2: "预防", 3: "临床表现", 4: "相关病症",
                        5: "治疗方法", 6: "所属科室", 7: "传染性", 8: "治愈率",
                        9: "禁忌", 10: "化验/体检方案", 11: "治疗时间", 12: "其他"}

                        model = train_model(texts, labels, epochs=1) # 演示只跑 1 轮
                        for t in ["肾结石一般用什么药", "婴儿会有痔疮吗"]:
                            print(t, "->", predict(model, t, id_to_name))
```

### 3.4 服务封装（Flask，含标签映射与耗时统计）

```text
# 依赖: pip install flask torch transformers
import json
import time

import torch
from flask import Flask, Response, request
from transformers import AutoModelForSequenceClassification, AutoTokenizer

CLS = "[CLS]"
id_to_name = {0: "finance", 1: "realty", 2: "stocks", 3: "education", 4: "science",
 5: "society", 6: "politics", 7: "sports", 8: "game", 9: "entertainment"}
# 医疗 13 类的映射同理，务必从 class.txt 统一读取，训练/推理共用同一份

MODEL_DIR = "./medical_bert"
device = torch.device("cuda" if torch.cuda.is_available else "cpu")
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR).to(device)
model.eval

app = Flask(__name__)

def inference(text, pad_size=128):
 enc = tokenizer(text, add_special_tokens=True, max_length=pad_size,
 padding="max_length", truncation=True, return_tensors="pt")
 enc = {k: v.to(device) for k, v in enc.items()}
 with torch.no_grad:
 logits = model(**enc).logits
 probs = torch.softmax(logits, dim=-1)[0]
 pred_id = int(probs.argmax)
 return id_to_name[pred_id], float(probs[pred_id])

@app.route("/v1/medical/", methods=["POST"])
def main_server:
 request_json = request.get_json
 content = request_json["content"]

 t1 = time.time
 label, confidence = inference(content)
 t2 = time.time

 return Response(
 status=200,
 response=json.dumps({
 "Status": "success",
 "Result": label,
 "Confidence": round(confidence, 4),
 "Time": "{:.4f}s".format(t2 - t1),
 }, ensure_ascii=False),
 mimetype="application/json",
 )

if __name__ == "__main__":
 app.run(host="127.0.0.1", port=5000)
```

三个工程要点：① **标签映射必须从 `class.txt` 统一读取**，训练与推理共用一份，否则会出现「静默的标签错位」（预测结果全部偏移一位）；② **返回置信度**，低置信度样本转人工，避免错误分诊直接触达患者；③ **推理必须 `model.eval` + `torch.no_grad`**，前者关闭 dropout 保证结果稳定，后者省显存。

## 4. 常见坑

| 现象 | 原因 | 解决 |
|------|------|------|
| 「CT检查」类问题被误分类 | `clean_text` 用 `[^\u4e00-\u9fa5]` 把 CT / MRI 全删了 | 改为保留字母数字 `[^\u4e00-\u9fa5A-Za-z0-9]`，或建医学缩写白名单 |
| 「化验/体检方案」类 F1 明显偏低 | 疑问词「什么/咋」被停用词表删掉，丢掉了意图信号 | 把疑问词加入白名单（`QUESTION_WORDS`），不参与过滤 |
| 医学长术语被切碎 | jieba 通用词典不含专业术语 | `jieba.load_userdict("medical_dict.txt")`，格式 `词 词频 词性` |
| 测试集准确率虚高 | 训练/测试划分前就做了分词与 TF-IDF | 先划分，再在训练集上 `fit`，测试集只 `transform` |
| 预测结果整体偏移一位 | 标签映射用了 `sorted(set(labels))` 重新排序，与 `class.txt` 不一致 | 统一从 `class.txt` 读映射，训练/推理/保存共用一份 |
| BERT 训练 loss 正常但准确率不涨 | 学习率太大（用了 1e-3 之类）破坏了预训练知识 | 降到 2e-5，加 warmup 与梯度裁剪 |
| BERT 微调第 1 轮最好，之后变差 | 7273 条小数据上过拟合 | 减少 epoch、加 weight_decay、`load_best_model_at_end=True` 早停 |
| GPU 显存溢出 | `max_length=128` + batch 16 + 13 类；或未用 `no_grad` 推理 | 减 batch、用梯度累积；推理套 `torch.no_grad` |
| FastText 报「模型没学到词」 | 输入未分词，整句被当成一个 token | 先用 jieba 分词空格连接，再加 `wordNgrams=2` |
| FastText 标签解析出错 | 忘了 `__label__` 前缀，或标签与文本之间不是空格 | 严格写 `__label__5 肾结石 输尿管 结石 一般 用 药` |
| 混淆矩阵显示「病因 ↔ 相关病症」互相误判严重 | 两类语义本身重叠（都在问「为什么会这样」） | 抽读错例确认；考虑合并类别或改多标签 |
| 剪枝后模型文件大小没变 | 只做了剪枝没调用 `prune.remove`，权重还是 `weight_orig × mask` 动态计算 | 剪枝后遍历模块调用 `prune.remove(module, "weight")` |
| 蒸馏后学生模型效果不如直接训练 | 温度 $T$ 或 $\alpha/\beta$ 权重设置不当；软标签未做 KL 散度 | 调 $T$（常用 2–5）与 $\beta$（教师知识权重），并对比消融 |
| 加载模型报设备不匹配 | GPU 上训练、CPU 上加载 | `torch.load(path, map_location="cpu")` |

## 5. 面试问答

**Q1. 医疗文本分类的预处理里，只用 `[^\u4e00-\u9fa5]` 清洗有什么问题？你会怎么改？**

<details><summary>参考答案</summary>

**问题：丢掉了所有非中文字符，而医疗领域的关键信息大量存在于英文缩写与数字中。**

具体损失：

1. **医学缩写全丢**：CT、MRI、B超、DNA、ICU、X线、血常规里的「WBC」「RBC」。这些恰恰是「化验/体检方案」类别的判别特征——「距骨骨折脱位做啥检查」和「需要做CT还是核磁」在清洗后特征高度趋同。
2. **数字与剂量丢失**：虽然没有明确影响意图分类，但「一天吃几次」「用多少毫克」这类问句里数字有信息量。
3. **符号丢失可能影响程度**：「？」能提示疑问句，「！」可能提示情绪强度。

**改法**：

```python
# 方案 A：保留中英文数字（推荐作为默认）
text = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', ' ', text)

# 方案 B：只保留「有意义」的非中文字符——医学缩写白名单
ABBR = {"CT", "MRI", "B超", "DNA", "ICU", "X线", "血常规", "心电图"}
# 先抽取白名单里的缩写做特殊处理（如统一大小写、加前缀保护），其余按方案 A

# 方案 C：对缩写做规范化，避免大小写与变体问题
text = text.replace("ct", "CT").replace("Ct", "CT").replace("核磁", "MRI")
```

**但要注意一个关键点**：改完之后**必须做对照实验验证**。语义上「保留更多信息」几乎总是好事，但工程上可能因为引入噪声特征（如各种无关的英文串）而掉点。正确做法是固定其他条件，只改清洗规则，比较验证集 macro-F1，重复 3–5 个随机种子看是否稳定提升。

同时要检查**训练与推理使用同一套清洗规则**——如果训练时保留英文、推理时删除英文，会造成训练-推理不一致，离线好线上差。

</details>

**Q2. 随机森林在医疗文本上能到 0.82–0.85，FastText 到 0.86–0.89，BERT 到 0.90–0.93。业务上怎么选？**

<details><summary>参考答案</summary>

按「精度需求 × 延迟要求 × 部署成本 × 数据量」四维决策，并且**一定要用真实业务指标而不是论文指标**来定。

| 场景 | 推荐 | 理由 |
|------|------|------|
| 快速验证、要做特征归因、无 GPU | 随机森林 + TF-IDF | 5 分钟出结果；`feature_importances_` 直接告诉你「什么药→治疗方法」，可解释性在医疗场景尤其重要（需要向医生解释为什么这么分） |
| 大规模请求、要求毫秒级响应、CPU 部署 | FastText | 训练 10 分钟、模型几十 MB、单条推理亚毫秒；子词机制对医学新词有兜底 |
| 追求最高精度、有 GPU、延迟可放宽到几十毫秒 | BERT 微调 | 上下文表示能力最强；医疗问句的意图常由句式与否定决定，上下文模型优势明显 |
| 既要 BERT 的精度又要 FastText 的速度 | **BERT 蒸馏到 TextCNN** | 教师软标签把类别间关系传给学生，实测可做到「92.5% 精度 + 5ms 延迟」 |
| 类别极多（上百类）或长文本 | FastText / 线性 + 层次 softmax | BERT 的 softmax 层参数随类别数线性增长；长文本受 512 限制 |

**决策前必须算的三笔账**：

1. **精度账**：BERT 比 FastText 高 3–4 个点，这些点对应多少业务价值？如果分类结果只用于「推送给医生参考」，3 个点可能不值得翻 10 倍的推理成本；如果用于「自动分诊」，3 个点可能意味着大量患者被推错科室。
2. **延迟账**：BERT-base 在 GPU 上单条约 10–50ms，CPU 上可能 200ms+。若 QPS 是 1000，纯 BERT 需要多张 GPU。用 2.6 节的数据算：1 亿次请求下 BERT 需要约 58 天算力，FastText 只需约 5.8 天。
3. **成本账**：GPU 租用成本 vs 精度提升收益；模型体积对部署（Docker 镜像大小、冷启动时间）的影响。

**最务实的三步路径**：① 用随机森林快速跑通并验证数据与评估流程正确；② 用 FastText 建立「性价比基线」，确认精度缺口有多大；③ 只有当缺口确实影响业务时才上 BERT，并同时规划蒸馏压缩方案。**不要跳过前两步直接上 BERT**——如果数据本身有标注问题，换模型是解决不了的。

</details>

**Q3. 混淆矩阵显示「病因」和「相关病症」互判严重（各占该类错误的 40%）。你怎么处理？**

<details><summary>参考答案</summary>

先判断是「模型能力不足」还是「类别体系本身重叠」——这个错例模式强烈提示后者。

**第一步：抽读错例，人工判断可分辨性**

从两类互相误判的样本中各抽 30 条，人工标注「这条是否真的只能属于某一类」。

- 若人工也判断不了（如「心脏病会引发癫痫吗」既可算「相关病症」也可算「病因」）→ **体系问题**，进入第二步。
- 若人工能明确区分，只是模型没学到 → **模型问题**，进入第三步。

**第二步：如果是体系问题**

| 方案 | 做法 | 代价 |
|------|------|------|
| 合并类别 | 把「病因」与「相关病症」合成「原因类」 | 损失细粒度，但指标会明显上升且更真实 |
| 改多标签 | 允许一条样本带多个标签（用 sigmoid + BCE 损失） | 需要重新标注（或从单标签转换），评估指标换成 micro/macro-F1 |
| 明确标注规范 | 定义清晰边界（如「问 A 会不会引起 B → 相关病症；问 B 为什么发生 → 病因」），重新审核边界样本 | 需要标注人力，但是根治手段 |

**第三步：如果是模型问题**

1. **补充判别性特征**：
 - 加 `ngram_range=(1,2)`，让「会引发」「引起」「原因」这类短语成为独立特征；
 - 保留疑问词（「为什么」→ 病因，「会不会」→ 相关病症），确保它们没被停用词删掉；
 - 医疗领域里这一类区分高度依赖**句式模板**，模板特征比疾病名有用得多。
2. **定向数据增强**：对这两类做回译或模板生成，构造更多边界样本（注意抽检语义是否漂移）。
3. **代价敏感学习**：在损失里对这两类的混淆样本加大惩罚；或加一个二阶段分类器专门区分这两类。
4. **换更强表示**：BERT 能捕捉「会不会」「是不是」这类句式与否定，通常对这类区分提升明显。

**第四步：验证与落地**
无论采用哪个方案，都要**用数据验证**：改完后重新算这两类的 F1 与混淆矩阵，确认热点消失；同时检查其他类别是否被牵连掉点。如果选择了合并类别，必须在报告里说明「类别体系发生变化，指标不可与之前直接比较」——这是很容易被忽略的诚实性问题。

**最后一点经验**：医疗意图分类里，「类别体系设计」对最终效果的影响往往大于模型选择。一套边界清晰的 10 类体系，用一个逻辑回归就能到 0.90；而一套互相重叠的 13 类体系，用 BERT 也可能卡在 0.88。**先修体系，再修模型**。

</details>

## 6. 自测题

**1. 预处理流水线是「清洗 → 分词 → 去停用词 → 拼接」。如果把「分词」和「去停用词」的顺序调换，会发生什么？**

<details><summary>参考答案</summary>

调换后变成「对原始文本去停用词 → 分词」，实际上**无法执行或效果错乱**，原因是去停用词的操作前提是「已经有词列表」。

- 「去停用词」的本质是列表过滤：`[w for w in words if w not in stopwords]`。它作用在**分词结果**上，因为停用词表里存的是词（如「的」「什么」），而不是句子片段。
- 如果在分词前做「去停用词」，只能退化为**字符串删除**（`text.replace("的", "")`），这会造成严重后果：把「目的」删成「目」，把「的确」删成「确」，把「什么」以外含「么」的词也破坏掉。中文没有词边界，字符串级替换会误伤大量包含停用词字串的正常词。

正确的顺序及其必要性：

| 步骤 | 为什么必须在这个位置 |
|------|---------------------|
| 清洗 | 先去标点/特殊符号，避免它们被 jieba 切成独立 token 混入后续流程 |
| 分词 | 只有切出词，才能知道「哪些是停用词」 |
| 去停用词 | 在词级别过滤，安全且可控 |
| 拼接 | 把词列表还原成空格分隔的字符串，供 TF-IDF / FastText 使用 |

补充一个相关坑：如果**先拼接再去停用词**（即对空格串做字符串替换），同样会误伤——因为「的」可能出现在「目的」「的确」内部。所以顺序是**不能变**的。

</details>

**2. 「什么」「怎么」「为什么」这类疑问词在通用停用词表里通常被过滤掉。为什么在医疗意图分类里它们反而是关键特征？**

<details><summary>参考答案</summary>

**根本原因：本项目的 13 个类别是「问句意图」，而不是「主题」。** 区分意图的主要信号就是疑问词与句式，而不是疾病名称。

| 疑问标记 | 指向的类别 |
|----------|-----------|
| 什么是 / 什么叫 | 定义（0） |
| 原因 / 为什么 / 咋搞的 | 病因（1） |
| 怎么预防 / 如何避免 | 预防（2） |
| 症状是什么 / 有什么表现 | 临床表现（3） |
| 会不会 / 能不能引起 | 相关病症（4） |
| 用什么药 / 怎么治 | 治疗方法（5） |
| 看什么科 / 挂哪个科 | 所属科室（6） |
| 传染吗 / 容易感染不 | 传染性（7） |
| 治愈率 / 能治好吗 | 治愈率（8） |
| 有什么危害 / 能不能吃 | 禁忌（9） |
| 做啥检查 / 化验什么 | 化验/体检方案（10） |
| 多久 / 多少天 | 治疗时间（11） |

如果按通用停用词表把「什么」删掉：
- 「什么药」→ 只剩「药」
- 「什么症状」→ 只剩「症状」
- 「什么是骨纤维瘤」→ 只剩「骨纤维瘤」（完全丢失「这是问定义」的信号！）
- 「做啥检查」→ 只剩「检查」

最后一条尤其致命：**「什么是X」和「X怎么治」在删除疑问词后可能都只剩疾病名**，模型完全无法区分「定义」和「治疗方法」。

**处理方案**：

1. **建白名单机制**：`if w in QUESTION_WORDS or w not in stopwords`，让疑问词豁免过滤（本文 3.1 节的做法）。
2. **不要用通用停用词表**：医疗领域的停用词表应从数据里统计高频但无判别力的词（如「请问」「一下」「可能」），而不是套用通用表。
3. **把疑问词作为显式特征**：除了作为 token 保留，还可以额外统计「疑问词类别」（what/why/how/howlong）作为独热特征喂给树模型，通常有直接收益。
4. **验证**：做一次消融实验——「过滤疑问词」vs「保留疑问词」的 macro-F1 对比。在有疑问词的情况下，差距通常在 2–5 个点，是一个必须验证的高价值改动。

一个通用的教训：**停用词表是任务特定的，不是通用的**。情感分析要保留否定词与转折词，医疗意图分类要保留疑问词，检索任务不能删任何可能成为查询词的内容。任何"通用停用词表"的使用都必须经过验证。

</details>

**3. 为什么说「疾病名称对区分 13 个类别几乎无用」？这对建模有什么指导意义？**

<details><summary>参考答案</summary>

**因为同一个疾病名可以出现在多种意图里**：

| 样本 | 疾病 | 意图类别 |
|------|------|----------|
| 什么是骨纤维瘤 | 骨纤维瘤 | 定义 |
| 骨纤维瘤的原因是什么 | 骨纤维瘤 | 病因 |
| 骨纤维瘤有什么症状 | 骨纤维瘤 | 临床表现 |
| 骨纤维瘤怎么治疗 | 骨纤维瘤 | 治疗方法 |
| 骨纤维瘤看什么科 | 骨纤维瘤 | 所属科室 |

疾病名是**常量**，意图由**问法**决定。从信息论角度：疾病名在各类别间的分布几乎是均匀的（每类都可能提到任何疾病），因此它的**互信息（与标签的相关性）接近 0**；而「什么药」「怎么回事」「做啥检查」与标签的互信息很高。

**对建模的指导意义**：

1. **特征工程方向**：应该重点提取**句式/疑问词/n-gram 模板**特征，而不是疾病名词典特征。具体做法：加 `ngram_range=(1,2)` 或 `(1,3)` 让「用什么药」「做啥检查」成为独立特征。
2. **停用词表的取舍**：如前所述，疑问词必须保留；反而可以考虑把**疾病名**加入停用词或降低其权重（如果语料里病种分布不均衡，疾病名可能引入伪相关）。
3. **数据划分**：要注意**同一疾病的多个问句不能跨训练/测试集**（如果划分不当），否则模型会利用疾病名的记忆效应得到一个虚高的分数。正确的做法是按疾病分组划分，或用真实的时间/来源划分。
4. **错误分析的重点**：错例不会集中在"没见过的疾病"，而会集中在"句式模糊"的样本上（如「心脏病会引发癫痫吗」既像病因又像相关病症）。错误分析应该按**句式模板**归类，而不是按疾病归类。
5. **模型选择**：这条洞察解释了为什么 FastText（有 `wordNgrams=2`，能捕捉「用什么 + 药」的局部组合）明显优于纯词袋的随机森林；也解释了为什么 BERT 更强——它能建模整个问句的句法结构。
6. **验收标准**：如果训练出来的模型 Top 特征全是疾病名，这是一个**警告信号**，说明数据集里存在病种与类别的分布偏差（例如「定义」类恰好集中在少数几种病），模型学的是伪特征。这时应该检查数据分布，并考虑做病种分层采样。

</details>

## 7. 延伸阅读

- 知识蒸馏原始论文《Distilling the Knowledge in a Neural Network》(Hinton et al., 2015)：https://arxiv.org/abs/1503.02531
- 中文医疗预训练模型 MC-BERT《Conceptualized Representation Learning for Chinese Biomedical Text Mining》：https://arxiv.org/abs/2008.10813
- PyTorch 模型剪枝官方（`prune.l1_unstructured` / `ln_structured` / `remove` 的完整用法）：https://pytorch.org/tutorials/intermediate/pruning_tutorial.html
- PyTorch 动态量化（INT8 量化，适合 BERT/Linear 层）：https://pytorch.org/tutorials/recipes/quantization.html
- Hugging Face `Trainer` 文档（`TrainingArguments` 全部参数、早停与最佳模型加载）：https://huggingface.co/docs/transformers/main_classes/trainer
- `bert-base-chinese` 模型卡（中文 BERT 的配置与用法）：https://huggingface.co/bert-base-chinese
- 中文医疗 NLP 数据集与任务汇总（CMeKG、cMedQA、CBLUE 等）：https://github.com/CBLUEbenchmark/CBLUE

---

[⬅️ 返回 NLP 目录](README.md)
