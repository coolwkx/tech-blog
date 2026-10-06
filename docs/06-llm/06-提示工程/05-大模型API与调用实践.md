---
article_id: "563344f304a7"
learning_kind: "reference"
learning_category: "06-llm"
---

# -大模型API与调用实践


> **一句话总结**：大模型应用有两条落地路径——**不训练只调用**（API + 提示工程，低成本、快迭代）和**小代价训练**（Prompt-Tuning / P-Tuning / LoRA 等参数高效微调，让下游任务去迁就预训练目标）；生产上常见的组合是「API 调用跑通业务 + 少量参数高效微调换效果」。
> **前置知识**：BERT 与 MLM 预训练目标（见《02-Transformer与注意力机制》）、Python 与 HTTP 基础、PyTorch 训练循环。
> **学完能做到**：1. 熟练使用 Chat Completions 的各个参数并说明调参方向；2. 说清 PET 的 Pattern-Verbalizer 原理与 P-Tuning 演进；3. 判断一个业务需求该用 API 调用、提示工程还是参数高效微调。

## 1. 核心概念

### 1.1 大模型 API 调用的请求结构

主流服务（OpenAI、DeepSeek、通义、智谱、以及本地 Ollama）都提供 **OpenAI 兼容**的
`POST /chat/completions` 接口，请求体核心字段如下：

| 字段 | 类型 | 含义 |
|---|---|---|
| `model` | string | 模型标识，如 `gpt-4o-mini`、`deepseek-chat` |
| `messages` | array | 对话消息列表，每项含 `role` 与 `content` |
| `temperature` | float | 采样随机性，0~2 |
| `top_p` | float | 核采样阈值，0~1 |
| `max_tokens` | int | 生成 token 上限 |
| `stream` | bool | 是否流式返回 |
| `stop` | string/array | 命中即停止生成 |
| `frequency_penalty` | float | 按 token 累计出现次数惩罚 |
| `presence_penalty` | float | 只要出现过就惩罚 |
| `n` | int | 返回候选数 |
| `response_format` | object | 约束为 `json_object`（部分服务支持） |

`messages` 中的 `role` 只有三种：

| role | 作用 | 工程建议 |
|---|---|---|
| `system` | 设定角色、任务、输出格式、边界 | 放稳定不变的规则，便于复用与缓存 |
| `user` | 用户输入 / few-shot 示例的输入 | 用户内容**必须**与指令分隔，防提示注入 |
| `assistant` | 模型历史回复 / few-shot 示例的输出 | 用于多轮对话；few-shot 时人工撰写 |

### 1.2 采样参数速查表

| 参数 | 调大 | 调小 | 典型取值 |
|---|---|---|---|
| `temperature` | 更发散、更有创意、更易跑偏 | 更确定、更保守、趋近贪心 | 结构化任务 0；对话 0.7；创意 0.9~1.2 |
| `top_p` | 候选词更多、更随机 | 候选词更少、更确定 | 0.8~0.95 |
| `max_tokens` | 更完整，也更慢更贵 | 可能被截断 | 按任务预估 + 20% 余量 |
| `stream` | 首字延迟低、体验好 | 需等待完整结果 | 交互式产品开启 |
| `frequency_penalty` | 减少重复用词 | 允许重复 | 0~0.5（过高会破坏术语一致性） |
| `presence_penalty` | 鼓励引入新话题 | 允许围绕同一话题展开 | 0~0.5 |
| `stop` | — | — | 与输出格式约定一致（如 `["\n\n"]`） |
| `n` | 一次多候选，便于自洽性投票 | 省成本 | 评估/投票场景 3~5 |

> 经验：**一次只调一个参数**。同时压低 `temperature` 和 `top_p` 会让输出迅速坍缩成重复文本；
> 需要在同一 prompt 上做多次实验时，固定其他参数并记录版本。

### 1.3 NLP 的四种范式

| 范式 | 做法 | 代表 | 相对上一代的变化 |
|---|---|---|---|
| 第一范式 | 传统机器学习 | TF-IDF 特征 + 朴素贝叶斯等 | 基线方案，特征工程量大 |
| 第二范式 | 深度学习模型 | word2vec 特征 + LSTM 等 | 准确率提升，特征工程减少 |
| 第三范式 | 预训练模型 + Fine-Tuning | BERT + fine-tuning | 准确率显著提高，但需较多训练数据 |
| 第四范式 | 预训练模型 + Prompt + 预测 | BERT + Prompt | 小样本即可训练出好模型，训练数据显著减少 |

整个 NLP 领域的发展方向是**精度更高、监督更少，甚至无监督**，而 Prompt-Tuning 是这条路线最新的成果之一。

### 1.4 微调方法对比

**核心判据**：任务/领域固定、数据量在「几千~几万条」量级、要把领域知识固化进权重 → 参数高效微调；
需求频繁变化、以格式与流程编排为主 → 走 API 调用 + 提示工程。

## 2. 关键机制

### 2.1 为什么需要在两种路径间选择

| 维度 | API 调用 + 提示工程 | 参数高效微调 |
|---|---|---|
| 是否需要标注数据 | 不需要 / 少量 few-shot | 需要（几百~几万条） |
| 成本结构 | 按 token 付费，随调用量线性增长 | 一次性训练成本 + 自建推理成本 |
| 迭代速度 | 改 prompt 立即生效 | 需重训、需评估、需发布 |
| 能力上限 | 受基座模型限制 | 可把领域知识与输出规范写进权重 |
| 知识时效 | 依赖 prompt 注入（RAG） | 训练时冻结，时效性差 |
| 数据安全 | 数据出域 | 可私有化部署 |
| 典型场景 | 分类、抽取、摘要、客服问答 | 领域术语强的分类/匹配、固定格式生成 |

**参考项目的选择逻辑**（金融三大任务）：以 `Qwen2.5-7B` 通过 **few-shot / zero-shot 的 in-context learning** 直接完成，
`ChatGLM-6B` 本地加载做推理——选它的理由是**不需要专业算法知识、无需训练**，用 prompt 即可激发「涌现能力」。

### 2.4 Soft Prompt 的信息流

以「$p$ 个伪 token + 输入」为例，前向过程分四步：

| 步骤 | 操作 | 张量形状 |
|---|---|---|
| ① | $n$ 个 token $x_1,\dots,x_n$ 经预训练模型的 embedding table 映射为向量 | $n \times e$ |
| ② | 把连续模板中的每个伪标记 $v_i$ 视为参数，通过另一个 embedding table 得到 $p$ 个伪 token 的向量矩阵 | $p \times e$ |
| ③ | 将文本与 prompt 拼接得到新输入 | $(p+n)\times e \to \mathbb{R}^{(p+n)\times e}$ |
| ④ | 新的输入喂入模型，得到新的表征；**只有 prompt 对应的向量表征参数
 $\mathbf{P}\in\mathbb{R}^{p\times e}$ 随训练更新** | — |

关键结论：**整个过程中预训练的大模型参数被冻结**，只有 $\mathbf{P}$ 在更新。

**提示**：Prompt Tuning 的 embedding 前缀是加在开头的，看起来更像"模仿 Instruction 指令"，
而 P-Tuning 添加的位置不固定；Prompt Tuning 不需要额外的 MLP 来初始化，而 P-Tuning 需要
LSTM + MLP 做初始化。

### 2.5 Prompt Tuning / P-Tuning v1 / P-Tuning v2

**Prompt Tuning**（Google，2021，《The Power of Scale for Parameter-Efficient Prompt Tuning》，
基于 T5，最大 11B）：为每一个输入文本假设一个**固定前缀提示**，该提示由神经网络参数化，
并在下游任务微调时更新，**大模型参数被冻结**。

| 优点 | 缺点 |
|---|---|
| 大模型的微调新范式；小样本学习场景表现好；可固定大模型参数只调少量附加参数适配下游任务 | 模型参数规模大了之后可解释性不太行；收敛速度较慢；调参比较复杂 |

特点总结：**适配性能基本与全参数微调相当**。

**P-Tuning v1**（清华，2022，《GPT Understands, Too》，面向 NLU）：提出动机是
「大模型的 prompt 构造方式严重影响下游任务的效果」，因此**把 prompt 转换为可以学习的 Embedding 参数进行优化**。
做法：**固定 LLM 参数**，用 MLP + LSTM 对 prompt embedding 进行编码，编码后与其他向量拼接再正常输入 LLM。
训练后**只保留 prompt 编码之后的向量**即可，无需保留编码器。

直接优化 embedding 参数存在两个挑战：

| 挑战 | 含义 | 解法 |
|---|---|---|
| Discreteness（不连续性） | 输入正常语料的 embedding 已经过预训练，而直接对 prompt embedding 随机初始化训练，容易陷入局部最优 | 用 LSTM + MLP 重参数化，把可学习参数映射为连续 embedding |
| Association（关联性） | 无法捕捉 prompt embedding 之间的相关关系 | 同上，用序列模型建模 token 间依赖 |

**P-Tuning v1 与 Prompt Tuning 的区别**：

| 对比项 | Prompt Tuning | P-Tuning |
|---|---|---|
| 位置 | 额外 embedding 加在**开头**，更像模仿 Instruction | 添加位置**不固定** |
| 是否需额外网络初始化 | 不需要 MLP | 通过 LSTM + MLP 来做初始化 |

**P-Tuning v2**（《P-Tuning v2: Prompt Tuning Can Be Comparable to Fine-tuning Universally Across Scales and Tasks》）：
核心思想是**在模型的每一层都应用连续的 prompt**，并对 prompt 参数进行更新优化，
主要解决 P-Tuning v1 **在小参数量模型上表现差**的问题，同时针对 NLU 任务优化适配。
训练后同样只保留 prompt 编码后的向量，无需保留编码器。

> 一句话记忆三者差异：**Prompt Tuning 只在输入层加前缀；P-Tuning v1 用 LSTM+MLP 把可学习参数映射成连续 embedding
> 且位置灵活；P-Tuning v2 把前缀加到每一层**，因此小模型上也能逼近全量微调。

## 3. 可运行示例

### 3.1 参数演示 + 流式输出

```python
# 依赖：pip install openai>=1.0；环境变量：export OPENAI_API_KEY=sk-xxx
import os, time
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# 1) 非流式：结构化任务用 temperature=0 保证确定性
resp = client.chat.completions.create(
model="gpt-4o-mini",
messages=[{"role": "system", "content": "你是金融文本分类器，只输出一个类别名称。"},
{"role": "user", "content": "央行今日宣布降息以刺激经济增长。"}],
temperature=0, top_p=1.0, max_tokens=16, n=1,
)
print("分类结果:", resp.choices[0].message.content)
print("用量 :", resp.usage.model_dump()) # 监控 prompt/completion tokens

# 2) 流式：统计首字延迟 TTFT
start, first, buf = time.time(), None, []
for chunk in client.chat.completions.create(
model="gpt-4o-mini",
messages=[{"role": "user", "content": "用两句话解释什么是参数高效微调。"}],
temperature=0.7, top_p=0.9, max_tokens=256, stream=True,
):
    piece = chunk.choices[0].delta.content
    if piece:
        if first is None:
            first = time.time() - start
            buf.append(piece)
            print(piece, end="", flush=True)
            print(f"\n[TTFT {first:.2f}s / 总耗时 {time.time() - start:.2f}s]")
```

**要点**：结构化任务 `temperature=0`；创意任务 0.7~1.0 配 `top_p=0.8~0.95`；
**不要同时大幅调低两者**，否则输出会坍缩成重复文本。

```python
# 依赖：pip install torch transformers peft datasets
import torch
from datasets import Dataset
from transformers import (AutoTokenizer, AutoModelForSequenceClassification,
TrainingArguments, Trainer, DataCollatorWithPadding)
from peft import LoraConfig, get_peft_model, TaskType

MODEL = "hfl/chinese-roberta-wwm-ext" # 小模型便于本地验证，换大模型同理
raw = {"text": ["央行宣布降息刺激经济", "公司发布年度财务报告", "分析师看好新能源行业"],
"label": [0, 1, 2]}
ds = Dataset.from_dict(raw).train_test_split(test_size=0.33, seed=42)
tok = AutoTokenizer.from_pretrained(MODEL)
ds = ds.map(lambda b: tok(b["text"], truncation=True, max_length=128), batched=True)

model = AutoModelForSequenceClassification.from_pretrained(MODEL, num_labels=3)
lora_cfg = LoraConfig(task_type=TaskType.SEQ_CLS, r=8, lora_alpha=32, lora_dropout=0.1,
target_modules=["query", "value"]) # 只对注意力的 Q/V 注入
model = get_peft_model(model, lora_cfg)
model.print_trainable_parameters() # 可训练参数通常 < 1%

trainer = Trainer(
model=model,
args=TrainingArguments(output_dir="./lora_out", num_train_epochs=5,
per_device_train_batch_size=4, learning_rate=2e-4,
logging_steps=1, save_strategy="no", report_to=[]),
train_dataset=ds["train"], eval_dataset=ds["test"],
data_collator=DataCollatorWithPadding(tok),
)
trainer.train()
model.save_pretrained("./lora_out/adapter") # 只保存几十 MB 的 adapter
print("GPU 可用" if torch.cuda.is_available() else "使用 CPU（很慢，仅验证流程）")
```

## 4. 常见坑

| 坑 | 现象 | 原因 | 正确做法 |
|---|---|---|---|
| 标签词被切成多 token | 取 `[MASK]` 概率时报错或结果异常 | 中文 tokenizer 会把长词切碎 | 选单 token 标签词（如「好/差」），或对多 token 概率求和/取平均 |
| 模板里出现多个 `[MASK]` | 逻辑混乱、映射错位 | 模板设计不严谨 | 保证模板有且仅有一个 `[MASK]`，并用断言校验 |
| 不同模板结果差异大 | 同一数据准确率相差近 10 个点 | PET 对 Pattern 高度敏感 | 多模板集成（ensemble）取平均，或用 P-Tuning 转向软模板 |
| 在 P-Tuning 中误更新基座参数 | 显存暴涨、失去参数高效的意义 | 未冻结预训练模型 | 训练前 `requires_grad=False` 冻结基座，只训练 prompt/adapter |
| 把 Prompt Tuning 与 P-Tuning 混为一谈 | 讲错实现细节 | 两者名字相近 | 记住：Prompt Tuning 加**开头**前缀且无需 MLP；P-Tuning 位置灵活且用 LSTM+MLP 初始化；v2 加到**每层** |
| 认为参数高效微调总能媲美全量微调 | 小模型上效果明显变差 | P-Tuning v1 在小模型上表现差 | 小参数量模型用 P-Tuning v2 或 LoRA，或提高 LoRA 的 `r` |
| LoRA 学习率照抄全量微调 | 收敛极慢 | LoRA 只训练少量参数 | LoRA 学习率通常用 1e-4 ~ 3e-4（比全量微调大 1~2 个数量级） |
| `r` 与 `lora_alpha` 随意设置 | 欠拟合或过拟合 | `alpha/r` 决定更新幅度的缩放 | 保持 `alpha` 为 `r` 的 2~4 倍，从 `r=8` 起调 |
| API 分类任务用高 temperature | 同一输入标签漂移 | 采样随机性 | 结构化任务 `temperature=0`，并校验输出词表 |
| 忽视 token 成本 | 账单暴涨 | few-shot 让 prompt 变长、重试放大用量 | 压缩示例数量、启用 prompt 缓存、监控 `usage` |
| 把生成式问诊机器人当医疗建议 | 输出编造、有风险 | 无知识约束与安全护栏 | 加免责声明 + 检索增强 + 敏感内容过滤 |

## 5. 面试问答

**Q1：PET 的核心思想是什么？它相比「BERT + 新初始化 MLP」的优势在哪？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

PET（Pattern-Exploiting Training）的核心思想是**把下游分类任务改写成与预训练 MLM 一致的完形填空**：
用人工先验知识设计含 `[MASK]` 的模板（Pattern），把原句拼进去，复用预训练好的 MLM head 得到 `[MASK]`
位置的概率分布，再通过标签词映射（Verbalizer）把预测词转回类别标签，用交叉熵训练。

优势在于：① **消除了预训练任务与下游任务之间的 gap**——模型在预训练时做的就是完形填空；
② **不引入随机初始化的新参数**（不像传统微调会新加一个 MLP 分类头），因此在极少量样本下也不易过拟合，
较少样本即可媲美多样本的传统微调；③ 释放了预训练模型的知识潜力。

代价是**对人工模板高度敏感**——不同模板在同一数据集上准确率可相差近 10 个百分点，且模板无法全局优化，
需要领域先验知识。这直接催生了后续自动寻找模板的 Prompt-Tuning / P-Tuning 系列方法。

</details>

**Q2：Prompt Tuning、P-Tuning v1、P-Tuning v2 有什么区别？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

| 维度 | Prompt Tuning | P-Tuning v1 | P-Tuning v2 |
|---|---|---|---|
| 提出方/论文 | Google《The Power of Scale for PEFT》（T5-11B） | 清华《GPT Understands, Too》 | 《P-Tuning v2》 |
| 目标 | NLG，参数高效微调新范式 | NLU，解决 prompt 构造影响效果的问题 | 解决 v1 在小参数量模型上表现差 |
| 前缀位置 | 加在输入**开头**（像 Instruction） | 位置**不固定** | **每一层**都加连续 prompt |
| 初始化 | 不需要额外网络 | 需要 LSTM + MLP 重参数化 | 每层 prompt 独立可学习 |
| 是否冻结基座 | 冻结 | 冻结 | 冻结 |

共同点：都**冻结预训练模型参数**，只训练少量连续 prompt 向量（伪 token，本质是向量），
训练后只保留 prompt 编码后的向量即可，无需保存基座副本。

处理两个关键挑战的是 P-Tuning v1：**Discreteness（随机初始化的 prompt embedding 易陷入局部最优）**
与 **Association（无法捕捉 prompt embedding 之间的相关性）**，方案是用 MLP + LSTM 做重参数化。

</details>

**Q3：一个业务需求来了，你怎么判断该用 API 调用 + 提示工程，还是参数高效微调？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

先看四个问题：

1. **任务稳定性**：需求频繁变化、本质是流程编排（分类、抽取、摘要、问答）→ API + 提示工程；
 任务形态固定、需要把领域知识与输出规范固化 → 微调。
2. **数据量**：没有标注数据或只有几十条 → 提示工程（few-shot）；有几百到几万条 → 考虑 LoRA/P-Tuning。
3. **成本结构**：调用量大且长期运行，自建推理更划算 → 微调 + 私有化部署；
 调用量小或波动大 → API 按量付费。
4. **数据合规**：数据不能出域 → 必须私有化部署（本地模型 + 微调）。

实践中常见组合是「**先用提示工程快速跑通业务、验证价值，再把高频且稳定的子任务用 LoRA 固化**」。
金融项目正是因为「不需要专业算法知识、无需训练」而选择 ChatGLM-6B + in-context learning；
而电商评论分类项目则因为要提升固定任务的准确率，选择了 PET / P-Tuning 路线。

</details>

## 6. 自测题

**1. 写出 NLP 四范式，并说明第四范式相比第三范式的核心优势。**

<details markdown="1">
<summary markdown="1">参考答案</summary>

① 传统机器学习（TF-IDF + 朴素贝叶斯等）；② 深度学习模型（word2vec + LSTM 等）；
③ 预训练模型 + Fine-Tuning（BERT + fine-tuning）；④ 预训练模型 + Prompt + 预测（BERT + Prompt）。

第四范式的核心优势是：**训练数据量显著减少**——通过添加模板把下游任务转换为预训练任务的形式，
让模型在小样本甚至零样本场景下也能达到理想效果，同时避免引入额外参数、缓解过拟合。

</details>

**2. 什么是 Hard Prompt 与 Soft Prompt？各自的优缺点是什么？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

Hard Prompt（离散提示）：提示模板固定，由真实文本字符串构成。
优点是不需要显式指定模板中各 token 的语义；缺点是依赖人工、改变 prompt 中单个单词就会带来巨大差异，
无法按任务动态调整。

Soft Prompt（连续提示）：输入一个**可参数化**的提示模板，模板中的伪标记本质是向量，
可以在连续向量空间中自适应寻找合适的表示。
优点是模板参数可按任务调整、参数量极小、泛化能力更好；
缺点是引入额外参数需要训练、收敛较慢、调参复杂、可解释性弱。

训练时两者的共同点是**预训练模型参数冻结**，只更新 prompt 相关参数。

</details>

**3. 为什么 LoRA 能大幅降低显存占用？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

因为 LoRA 假设「下游任务所需的权重更新量是低秩的」，对原始权重矩阵 $W\in\mathbb{R}^{d\times d}$
不做全量更新，而是用 $W + BA$ 表示，其中 $B\in\mathbb{R}^{d\times r}$、$A\in\mathbb{R}^{r\times d}$、$r\ll d$，
只训练 $A$ 与 $B$。

收益：① **可训练参数量下降几个数量级**（`r=8` 时通常不到基座的 1%），
因此优化器状态与梯度显存大幅减少；② 不需要为每个任务保存完整模型，只保存几十 MB 的 adapter；
③ 推理时可把 $BA$ 合并回 $W$，**不引入额外推理延迟**。
工程上还需注意学习率要比全量微调大 1~2 个数量级，`lora_alpha` 通常取 `r` 的 2~4 倍。

</details>

**4. Chat 接口里 `system` / `user` / `assistant` 三种角色分别适合放什么内容？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

- `system`：稳定的角色设定、任务说明、输出格式与边界约束（如「你是金融文本分类器，只输出类别名」）。
 放这里便于复用与缓存，也让指令与用户数据天然分隔。
- `user`：用户的实际输入，以及 few-shot 示例中的「输入部分」。用户内容应与指令明确分隔，防提示注入。
- `assistant`：多轮对话中模型的历史回复，以及 few-shot 示例中的「输出部分」（需人工撰写并校验格式）。

给 few-shot 示例时要注意：示例必须与期望输出**逐字符同构**（含字段名、标点、大小写），
否则模型会忠实模仿错误的格式。

</details>

**5. 基于 GPT2 的医疗问诊机器人与 PET 文本分类在技术路线上有什么本质区别？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

本质上一个是**生成式（自回归）**、一个是**判别式（完形填空/分类）**。

- GPT2 问诊机器人：把「提问 + 分隔符 + 回答」拼成序列，用自回归语言模型（next-token prediction）
 在医疗问答语料上训练，推理时按上文续写回答。输出空间是**开放的整个词表**，因此灵活但可能编造，
 需要 `max_length`、停止符与安全过滤。
- PET 分类：把评论文本填入固定模板，只在 `[MASK]` 位置取概率，再用 Verbalizer 映射到**封闭的标签集合**，
 输出空间受限、结果稳定可校验。

工程含义：判别式方案输出可控、易评估，适合分类/抽取/匹配；生成式方案表达自由，
在高风险领域（医疗）必须叠加检索增强（RAG）与免责声明，不能直接作为诊疗依据。

</details>

## 7. 延伸阅读

- [GPT Understands, Too / P-Tuning (arXiv:2103.10385)](https://arxiv.org/abs/2103.10385)
- [P-Tuning v2 (arXiv:2110.07602)](https://arxiv.org/abs/2110.07602)
- [The Power of Scale for Parameter-Efficient Prompt Tuning (arXiv:2104.08691)](https://arxiv.org/abs/2104.08691)
- [LoRA (arXiv:2106.09685)](https://arxiv.org/abs/2106.09685)
- [Hugging Face PEFT 文档](https://huggingface.co/docs/peft/index)
- [OpenAI 文本生成指南](https://platform.openai.com/docs/guides/text-generation)

---

[⬅️ 返回本目录索引](README.md)
