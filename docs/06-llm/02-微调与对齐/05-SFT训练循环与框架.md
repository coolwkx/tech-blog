# SFT 训练循环与框架

> **一句话总结**：SFT（Supervised Fine-Tuning）的本质是"**在 chat template 生成的目标序列上做下一 token 预测，但只对 assistant 的回答部分计算 loss**"——数据、模板、掩码、collator、监控这五步里任何一步错位，都会表现为"loss 在降但模型不会用"。
> **前置知识**：因果语言模型的训练目标；tokenizer 与特殊 token（BOS/EOS/PAD）；交叉熵损失；LoRA 的注入方式（见 [03 篇](03-LoRA原理与工程实践.md)）与显存账本（见 [02 篇](02-全参微调与显存账本.md)）。
> **学完能做到**：
> 1. 从原始 instruction 数据出发，写出"chat template → tokenize → label masking → collator → Trainer"的完整可运行管线，并解释每一步在做什么。
> 2. 手写 label masking（把 prompt 部分置为 -100），并说清不掩码会发生什么。
> 3. 根据 loss 曲线形状、梯度范数和显存表现，定位"数据 bug / 学习率过大 / 过拟合 / 灾难性遗忘"。

## 1. 核心概念

> **说明**：本节内容超出你提供的课程资料范围，基于公开文档与论文整理。
> chat template 与 assistant-only mask、packing、框架选型等细节来自官方文档与公开实践。

### 1.1 SFT 在训练流水线中的位置

| 阶段 | 数据 | 目标函数 | 产出 |
| --- | --- | --- | --- |
| 预训练（Pre-training） | 海量无标注语料 | 下一 token 预测 $\mathcal{L}_{\text{CLM}}$ | 基座模型 |
| **SFT / 指令微调** | **（指令，回答）配对数据** | **同 $\mathcal{L}_{\text{CLM}}$，但只对回答算 loss** | **会跟随指令的模型** |
| 偏好对齐（RLHF / DPO） | 成对偏好数据 | 奖励最大化 / DPO 损失 | 与人类偏好对齐的模型 |

关键认识：**SFT 没有新的目标函数**。它用的还是语言模型的交叉熵，区别只在数据的组织方式（指令-回答格式）和 loss 的计算位置（只算回答）。所谓"教会模型对话"，本质是让模型在"看到指令和分隔符之后，继续生成回答"这个条件分布上概率更高。

这一点与 InstructGPT（[arXiv:2203.02155](https://arxiv.org/abs/2203.02155)）的描述一致：SFT 阶段就是用标注者写的示范回答做有监督微调。

### 1.2 数据格式的三种常见组织方式

| 格式 | 结构 | 优点 | 缺点 |
| --- | --- | --- | --- |
| Alpaca 式 | `{"instruction": ..., "input": ..., "output": ...}` | 简单直观，单轮任务友好 | 多轮对话表达力弱 |
| ShareGPT / messages 式 | `{"messages": [{"role": "system"/"user"/"assistant", "content": ...}, ...]}` | 原生支持多轮、角色、工具调用 | 需要正确的 chat template |
| 纯文本续写式 | `{"text": "..."}` | 不需要模板 | **无法做 assistant-only 掩码**，会把 prompt 也学进去 |

**推荐**：只要基座有官方 chat template，就用 messages 式，并让 tokenizer 负责拼接。手写字符串拼接是最常见的 bug 来源（漏掉 `<|im_start|>`、多一个空格、少一个 `<|eot_id|>`）。

### 1.3 关键超参表

| 超参 | 全参 SFT 经验区间 | LoRA SFT 经验区间 | 说明 |
| --- | --- | --- | --- |
| learning rate | $1\times10^{-5}$～$5\times10^{-5}$ | $1\times10^{-4}$～$3\times10^{-4}$ | LoRA 只训少量参数，需要更大步长 |
| epochs | 2～3 | 2～5 | 超过 3 轮在指令数据上极易过拟合/复读 |
| per_device_batch_size | 受显存限制 | 同左 | 与 `max_seq_len` 强耦合 |
| gradient_accumulation_steps | 使有效 batch $\approx$ 32～128 | 同左 | 有效 batch = micro × accum × 卡数 |
| warmup_ratio | 0.03～0.1 | 0.03～0.1 | 防早期发散 |
| lr_scheduler | cosine | cosine | linear 也可 |
| weight_decay | 0.0～0.1 | 0.0 | 指令数据上通常 0 或很小 |
| max_grad_norm | 1.0 | 1.0 | 梯度裁剪 |
| max_seq_len | 1024～4096 | 同左 | 超过训练长度会静默截断 |
| gradient_checkpointing | 长序列必开 | 长序列必开 | 换时间省显存 |
| bf16 | 推荐 | 推荐 | 比 fp16 稳，无需 loss scaling |
| packing | 视情况 | 视情况 | 提升吞吐，但需 attention mask 正确 |

> 上表是**社区与官方文档中的常见取值区间**，不是普适最优值。任何超参都应通过小规模扫描（例如 3 个学习率 × 2 个 epoch）在自建评测集上确定。

### 1.4 训练框架的取舍

| 方案 | 定位 | 优点 | 代价 |
| --- | --- | --- | --- |
| 手写 PyTorch 循环 | 完全可控 | 每行都可解释，便于 debug 与自定义 loss | 要自己处理 AMP、梯度累积、分布式、checkpoint |
| `transformers.Trainer` | 通用训练器 | 开箱即用，支持 AMP、累积、断点续训 | 数据侧仍要自己写 collator 与 masking |
| `trl.SFTTrainer` | 为 SFT 定制 | 内置 packing、chat template、assistant-only loss 掩码 | 抽象层多，出问题时要读源码 |
| `axolotl` / `LLaMA-Factory` | 配置驱动的一站式方案 | YAML 配置即训，支持大量模型与技巧 | 自由度受限，隐藏细节多 |
| `deepspeed` + 上述任一 | 大模型分布式 | ZeRO-3/offload，支撑 70B 级 | 配置复杂，调试成本高 |

建议路径：**先用 `Trainer` + 手写 masking 跑通一次（理解机制），再切到 `SFTTrainer` 或配置驱动框架提高效率。**

### 1.5 完整数据流

```text
 原始数据 (jsonl: instruction/input/output 或 messages)
        │
        ▼
 [1] 数据清洗与去重 ──► 长度过滤、格式校验、按任务配比采样
        │
        ▼
 [2] 套 chat template ──► tokenizer.apply_chat_template(..., tokenize=False)
        │                  （得到带特殊 token 的完整字符串）
        ▼
 [3] tokenize ──► input_ids / attention_mask
        │
        ▼
 [4] label masking ──► labels = input_ids 的副本，
        │              将 prompt（system+user+模板标记）位置置为 -100
        ▼
 [5] collator ──► 动态 padding 到 batch 内最长（或 pad_to_multiple_of=8），
        │          labels 的 pad 位也必须是 -100
        ▼
 [6] 训练循环 ──► forward → CrossEntropyLoss(ignore_index=-100) → backward
        │          → 梯度裁剪 → optimizer.step() → scheduler.step()
        ▼
 [7] 验证 ──► 独立验证集 loss + 生成式任务指标 ──► [8] 保存 best checkpoint
                    与 tokenizer、训练配置一并落盘
```

## 2. 关键机制

### 2.1 损失掩码：为什么只对回答算 loss

设一条样本的 token 序列为 $x_{1:T}$，其中 prompt 部分占前 $P$ 个 token（$x_{1:P}$），回答部分占后 $T-P$ 个 token。原始语言模型损失是

$$
\mathcal{L}_{\text{full}}
= -\frac{1}{T-1}\sum_{t=2}^{T}\log p_\theta(x_t \mid x_{<t})
$$

**掩码后的损失**是给每个位置引入权重 $m_t\in\{0,1\}$：

$$
\boxed{\;
\mathcal{L}_{\text{masked}}
= -\frac{1}{\sum_{t=2}^{T} m_t}\sum_{t=2}^{T} m_t \log p_\theta(x_t \mid x_{<t})
\;}
$$

其中 $m_t = 0$（被掩码）当 $t \le P$，$m_t = 1$ 当 $t > P$。PyTorch 的实现约定是：**把 $m_t=0$ 的位置的 label 写成 `-100`**，然后使用

```python
loss_fct = nn.CrossEntropyLoss(ignore_index=-100)
```

`ignore_index=-100` 表示该位置既不贡献分子（loss 项），也不贡献分母（归一化计数）。这与 `nn.CrossEntropyLoss` 支持 `ignore_index` 的官方语义一致（见 [PyTorch 文档](https://pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html)）。

**不掩码会发生什么？**

| 后果 | 机制 |
| --- | --- |
| 模型学会"复述用户输入" | prompt 的每个 token 都被要求高概率预测，而它们是给定的确定性文本，模型会倾向于在推理时把它们重写出来 |
| loss 数值被低估、失去可比性 | 分母包含了大量"简单"的 prompt token，loss 看起来降得很快但并不代表回答质量提升 |
| 训练与推理目标不一致 | 推理时我们只关心从 prompt 之后开始的分布，训练却把注意力分散到 prompt 上 |
| 短回答样本被稀释 | prompt 越长，回答部分在 loss 中的占比越小，模型对回答的学习信号越弱 |

**注意例外**：如果你做的是**领域继续预训练（DAPT）**，那就应该对全文算 loss——此时数据本身没有"prompt/回答"的区分。掩码策略必须与训练目标匹配。

### 2.2 chat template：为什么不能手工拼字符串

`apply_chat_template` 做的事是：把 messages 列表按模型自带的 Jinja 模板渲染成**与预训练时完全一致**的格式。不同模型的格式差异极大，例如：

```text
# 一类模板（ChatML 风格）
<|im_start|>system
你是一个助手<|im_end|>
<|im_start|>user
你好<|im_end|>
<|im_start|>assistant
你好，有什么可以帮你？<|im_end|>

# 另一类模板（特殊 token 分隔，注意 header 后的空行）
<|begin_of_text|><|start_header_id|>user<|end_header_id|>

你好<|eot_id|><|start_header_id|>assistant<|end_header_id|>
```

手工拼接的风险：少一个换行、把 `<|im_end|>` 写成 `<|endoftext|>`、忘记在 assistant 前加空格——这些都可能让模型进入"非训练分布"的格式，表现为回答质量暴跌却不报错。

**正确姿势**：

```python
text = tokenizer.apply_chat_template(messages, tokenize=False)
ids = tokenizer(text, add_special_tokens=False)["input_ids"]
```

注意 `tokenize=True` 也可以直接用，但做 masking 时我们往往需要同时拿到"带生成前缀的 prompt 长度"和"完整序列"，所以模式上更常见的是先渲染成字符串（见 3 节的实现）。

### 2.3 掩码的两种实现路径

| 路径 | 做法 | 优点 | 风险 |
| --- | --- | --- | --- |
| **前缀长度法**（通用） | 对每个 assistant 轮次，用 `apply_chat_template(messages[:i], add_generation_prompt=True)` 渲染出 prompt 前缀，tokenize 得到长度 $L$，把 `labels[:L] = -100` | 不依赖模板细节，几乎所有模型可用 | 需要保证前缀渲染与完整渲染的前缀部分逐 token 一致（绝大多数模板满足） |
| **模板自带掩码**（推荐，若支持） | `apply_chat_template(..., return_assistant_tokens_mask=True)`，模板中用 `{% generation %}` 块标记需要计算 loss 的部分 | 精确、无需二次渲染 | 只对带 `{% generation %}` 的模板生效，否则 mask 全 0 |

一个**必须检查**的点：`return_assistant_tokens_mask` 生成的掩码是否包含 assistant 结尾的 EOS/`<|im_end|>`/`<|eot_id|>`。结尾 token **应该**参与 loss（要教模型"什么时候停"），如果被掩掉，模型可能不会正常结束。相关的修复讨论可参考 TRL 仓库中关于"训练模板必须保留 stop token 在 loss mask 中"的 issue/PR（例如 [huggingface/trl#5988](https://github.com/huggingface/trl/pull/5988)）。

### 2.4 padding 侧、position_ids 与生成

| 问题 | 训练时 | 推理时 |
| --- | --- | --- |
| padding 放在哪一侧 | 训练必须**右侧** padding（配合 causal mask 才正确）；左 padding 在训练中会让位置对齐出错 | 生成时必须**左侧** padding（否则不同长度样本的生成起点不一致） |
| attention mask | 必须以 `attention_mask` 明确告知 padding 位置，不能只靠 `input_ids` | 同左 |
| labels 的 pad 位 | 必须是 `-100` | 不适用 |

在 `transformers` 中，`DataCollatorForSeq2Seq` / `DataCollatorForLanguageModeling` 默认做右侧 padding；而 `tokenizer.padding_side = "left"` 是很多生成式推理示例的默认设置。**同一个 tokenizer 在训练与推理之间切换 padding 侧时，最容易出问题。**

### 2.5 序列打包（packing）

**做法**：把多条短样本拼接成一条长度为 `max_seq_len` 的序列，用 EOS 分隔，以避免大量 padding 浪费算力。

| 维度 | 不打包 | 打包 |
| --- | --- | --- |
| 有效 token 比例 | 低（大量 pad） | 接近 100% |
| 吞吐 | 基线 | 明显更高 |
| 风险 | 无 | 跨样本注意力泄漏；loss 归一化口径变化 |
| 正确实现 | —— | 必须使用 block-diagonal attention mask（或 FlashAttention 的 varlen 接口） |

如果框架只是简单拼接而没有做 block-diagonal mask，模型会"看到"上一条样本的内容——这是数据泄漏，会让验证 loss 看起来异常低。使用前务必确认实现的注意力掩码语义。

### 2.6 有效 batch、学习率与 warmup

$$
B_{\text{有效}} = b_{\text{micro}} \times n_{\text{accum}} \times N_{\text{卡数}}
$$

学习率与有效 batch 大致成**亚线性**关系：把有效 batch 扩大 $k$ 倍，常用做法是把学习率放大 $\sqrt{k}$ 倍（线性放大 $\times k$ 往往过大）。这也是"小 batch 用大学习率、大 batch 用相对小学习率"的经验来源。

**warmup 的作用**：训练初期 Adam 的二阶动量估计方差很大，直接上大学习率容易发散或掉进坏区域。warmup 的步数常取总步数的 3%～10%。在 `Trainer` 里用 `warmup_ratio` 或 `warmup_steps` 指定。

### 2.7 灾难性遗忘与数据配比

SFT 数据通常是高度同质的（例如全是"客服问答"），连续训练会让通用能力退化。缓解手段：

| 手段 | 具体做法 | 效果 |
| --- | --- | --- |
| 数据混合 | 掺入 5%～20% 的通用指令数据（如开源指令集） | 最有效，成本低 |
| 降低学习率/减少 epoch | 用验证集选最优 checkpoint | 有效 |
| 只训部分参数 | LoRA / 只训顶层 | 有效但限制上限 |
| 早停 | 监控通用能力评测，一旦下降就停 | 需要评测成本 |
| 正则项 | 加 KL 约束或多任务联合训练 | 有效但需调参 |

**判断遗忘是否已经开始**的实用信号：① 通用指令的验证 loss 开始上升（即使下游任务 loss 仍在降）；② 模型输出的多样性下降（同一 prompt 的多次采样高度相似）；③ 出现任务无关的固定开头/结尾模板。

### 2.8 训练监控：loss 曲线怎么读

| 曲线形状 | 诊断 | 处理 |
| --- | --- | --- |
| 训练 loss 与验证 loss 同步平滑下降并收敛 | 正常 | 继续，按验证指标选 checkpoint |
| 训练 loss 持续下降，验证 loss 先降后升 | 过拟合 | 减少 epoch、加 dropout/weight decay、增数据 |
| loss 一开始就变成 NaN / inf | 学习率过大、fp16 溢出、数据含脏样本 | 降学习率、换 bf16、检查数据 |
| loss 剧烈震荡（锯齿状） | 学习率过大、batch 太小、warmup 不足 | 降学习率、加 warmup、增有效 batch |
| loss 几乎不降（平的） | 标签全被掩码成 -100、`target_modules` 没匹配上、学习率过小 | 检查 `labels != -100` 的比例、检查可训练参数 |
| loss 断崖式降到极低（如 0.01） | 数据泄漏（训练集与验证集重复、packing 未做 block-diagonal mask） | 去重、检查 mask |
| loss 周期性台阶 | 学习率调度器的阶梯点或数据按长度排序 | 正常，关注趋势 |

**梯度范数**：`grad_norm` 是第二个必须监控的量。

- 长期在 $10^{-3}$ 量级并且 loss 不降 → 学习率过小或梯度被裁剪过头；
- 频繁出现尖峰（$\gg$ `max_grad_norm`）→ 数据中有异常样本（超长、乱码）或学习率过大；
- 突然变成 0 → 该 batch 的所有 label 都是 -100（整批被掩码），此时 loss 为 nan 或 0，需要过滤。

**OOM 排查顺序**（按代价从低到高）：

```text
1. 降 per_device_train_batch_size 到 1，用 gradient_accumulation_steps 补回有效 batch
2. 开 gradient_checkpointing（注意同时把 use_cache=False）
3. 降 max_seq_len（检查是否有超长样本被截断）
4. 关掉 packing 或检查 packing 实现是否产生超长序列
5. 换优化器：adamw -> paged_adamw_8bit / adafactor
6. 换精度：fp32 -> bf16；QLoRA 场景把 bnb_4bit_compute_dtype 调低
7. 上 ZeRO 分片 / FSDP / CPU offload（见第 02 篇）
8. 仍不行则换更小的模型，或先做 LoRA
```

## 3. 可运行示例

下面是"chat template → tokenize → label masking → collator → Trainer"的完整骨架。

> **说明**：本机没有 GPU、没有安装 `torch`/`transformers`/`datasets`，**代码未在本机执行**；API 用法与参数名以 `transformers` 官方文档为准。

依赖：`torch>=2.1`、`transformers>=4.40`、`datasets>=2.16`、`accelerate`。（可选：`peft` 用于 LoRA。）

```python
# -*- coding: utf-8 -*-
"""
SFT 管线骨架：chat template + assistant-only label masking + Trainer。

核心是 mask_prompt_tokens()：把 prompt（含模板标记）位置的 label 置为 -100，
只对 assistant 回答部分计算交叉熵。
"""

from __future__ import annotations

import torch
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    Trainer,
    TrainingArguments,
)

IGNORE_INDEX = -100


def load_tokenizer(model_id: str) -> AutoTokenizer:
    tok = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token      # 常见做法：复用 EOS 作为 PAD
    tok.padding_side = "right"             # 训练必须右侧 padding
    return tok


def build_labels_with_masking(messages, tokenizer, max_len: int):
    """构造 input_ids 与 labels，prompt 部分置 -100。

    做法（前缀长度法，通用）：
      对每个 role == "assistant" 的轮次 i：
        prefix = apply_chat_template(messages[:i], add_generation_prompt=True)
        把 labels[:len(tokenize(prefix))] = -100
    这样每个 assistant 轮次的内容与结束标记都会参与 loss，
    而 system/user 与模板标记不参与。
    """
    full_text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=False
    )
    enc = tokenizer(full_text, truncation=True, max_length=max_len,
                    add_special_tokens=False)
    input_ids = enc["input_ids"]
    labels = list(input_ids)               # 先全部参与 loss

    for i, msg in enumerate(messages):
        if msg.get("role") != "assistant":
            continue
        prefix_text = tokenizer.apply_chat_template(
            messages[:i], tokenize=False, add_generation_prompt=True
        )
        prefix_len = len(
            tokenizer(prefix_text, add_special_tokens=False)["input_ids"]
        )
        prefix_len = min(prefix_len, len(labels))
        for j in range(prefix_len):
            labels[j] = IGNORE_INDEX

    return {
        "input_ids": input_ids,
        "attention_mask": enc["attention_mask"],
        "labels": labels,
    }


def build_dataset(tokenizer, records, max_len: int = 1024) -> Dataset:
    ds = Dataset.from_list(records)

    def _map(example):
        return build_labels_with_masking(example["messages"], tokenizer, max_len)

    return ds.map(_map, remove_columns=["messages"])


def sanity_check(dataset, tokenizer) -> None:
    """上线训练前必做：确认 mask 比例合理。"""
    n_total = n_train = 0
    for row in dataset:
        for lab in row["labels"]:
            n_total += 1
            if lab != IGNORE_INDEX:
                n_train += 1
    ratio = n_train / max(1, n_total)
    print(f"[自检] 参与 loss 的 token 占比 = {ratio:.2%}（期望 0.1 ~ 0.6）")
    if ratio == 0:
        raise RuntimeError("所有 label 都被掩码了：模板或掩码逻辑有问题")
    if ratio > 0.9:
        print("[警告] 掩码比例过低，prompt 可能也参与了 loss")
    first = dataset[0]
    kept = [tokenizer.decode([t]) for t, l in
            zip(first["input_ids"], first["labels"]) if l != IGNORE_INDEX]
    print("[自检] 第一个样本参与 loss 的文本片段：", repr("".join(kept))[:200])


def build_trainer(model, tokenizer, train_ds, eval_ds) -> Trainer:
    args = TrainingArguments(
        output_dir="./sft_out",
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        gradient_accumulation_steps=8,      # 有效 batch = 2 × 8 × 卡数
        num_train_epochs=3,
        learning_rate=2e-5,                 # 全参 SFT 常用 1e-5 ~ 5e-5
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        weight_decay=0.0,
        max_grad_norm=1.0,
        bf16=True,
        gradient_checkpointing=True,
        logging_steps=10,
        eval_strategy="steps",
        eval_steps=100,
        save_strategy="steps",
        save_steps=100,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        report_to=[],
    )
    collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        padding=True,
        pad_to_multiple_of=8,
        label_pad_token_id=IGNORE_INDEX,     # padding 位在 labels 中也是 -100
    )
    return Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        data_collator=collator,
        tokenizer=tokenizer,
    )


def demo_manual_loop(model, batch) -> float:
    """等价的手写训练步：展示 ignore_index 与梯度累积的归一化方式。"""
    model.train()
    accum_steps = 4
    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad], lr=2e-5
    )
    loss_fct = torch.nn.CrossEntropyLoss(ignore_index=IGNORE_INDEX)

    total_loss = 0.0
    for step in range(accum_steps):
        out = model(**batch)
        # transformers 的模型内部已用 ignore_index=-100；此处展示等价的显式写法
        shift_logits = out.logits[:, :-1, :].contiguous()
        shift_labels = batch["labels"][:, 1:].contiguous()
        loss = loss_fct(
            shift_logits.view(-1, shift_logits.size(-1)),
            shift_labels.view(-1),
        )
        (loss / accum_steps).backward()      # 除累积步数，保证梯度尺度一致
        total_loss += loss.item()
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    optimizer.step()
    optimizer.zero_grad(set_to_none=True)
    return total_loss / accum_steps


def main() -> None:
    model_id = "Qwen/Qwen2.5-1.5B-Instruct"
    tokenizer = load_tokenizer(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.bfloat16, trust_remote_code=True
    )
    if hasattr(model, "gradient_checkpointing_enable"):
        model.gradient_checkpointing_enable()
    model.config.use_cache = False          # 与 gradient checkpointing 冲突

    records = [{"messages": [
        {"role": "system", "content": "你是一个严谨的技术助手。"},
        {"role": "user", "content": "什么是 LoRA？"},
        {"role": "assistant", "content": "LoRA 冻结预训练权重，只训练低秩矩阵 A 和 B。"},
    ]}] * 16

    ds = build_dataset(tokenizer, records, max_len=1024)
    sanity_check(ds, tokenizer)
    trainer = build_trainer(model, tokenizer, ds, ds)
    trainer.train()
    trainer.save_model("./sft_out/final")
    tokenizer.save_pretrained("./sft_out/final")


if __name__ == "__main__":
    main()
```

**要点说明**：

1. `add_special_tokens=False` 用在渲染后的字符串上，因为 `apply_chat_template` 已经把 BOS 等特殊 token 写进字符串了，再让 tokenizer 加一次就会重复。
2. `prefix_len` 用同样的 tokenizer 与 `add_generation_prompt=True` 计算，保证 assistant 的起始位置准确。
3. `DataCollatorForSeq2Seq` 的 `label_pad_token_id` 必须设为 `-100`，否则 padding 位置会参与 loss，把短样本的 loss 拉低。
4. `sanity_check` 是**上线训练前必做的一步**：参与 loss 的 token 比例应在 0.1～0.6 之间（取决于回答/提问的长度比）。比例为 0 说明掩码逻辑错误。
5. 手写循环里 `(loss / accum_steps).backward()` 与 `Trainer` 内部行为一致；显式算 loss 时要注意 `logits[:, :-1]` 与 `labels[:, 1:]` 的错位。

## 4. 常见坑

| 现象 | 原因 | 解决 |
| --- | --- | --- |
| 模型只会复述用户问题 | 没有做 label masking，prompt 也参与了 loss | 按 2.1/2.3 实现掩码，并用 `sanity_check` 验证比例 |
| 训练 loss 很快降到很低，但生成质量差 | 训练集与验证集重复；或 packing 没做 block-diagonal mask 导致跨样本泄漏 | 数据去重；检查 packing 的 attention mask |
| 训练 loss 是 nan | 该 batch 所有 label 都是 -100（`CrossEntropyLoss` 分母为 0） | 过滤过短/无回答样本，或在 collator 里丢弃全掩码样本 |
| 回答总是停不下来，一直复读 | assistant 结尾的 EOS / `<\|im_end\|>` 被掩码掉了，或训练数据本身没加结束符 | 确认结束 token 参与 loss；检查数据里每条回答是否以 EOS 结尾 |
| 训练正常但推理时结果全乱 | 推理用了左 padding 而训练用右 padding（或反之），或漏传 `attention_mask` | 训练右 padding、推理左 padding；始终传 `attention_mask` |
| 验证 loss 上升但训练 loss 下降 | 过拟合 | 减 epoch、加正则、增数据；按 `eval_loss` 早停 |
| 通用能力明显下降 | 灾难性遗忘开始 | 掺 5%～20% 通用指令数据；降学习率；减少 epoch |
| 长样本被静默截断 | `max_seq_len` 小于实际长度 | 统计长度分布（分位数），必要时提升 `max_len` 或过滤超长样本 |
| `loss` 不降且可训练参数为 0 | `target_modules` 未匹配，或模型被全冻结 | `print_trainable_parameters()`；检查 `requires_grad` |
| `use_cache=True` 与 gradient checkpointing 同时开启导致报错或变慢 | 二者冲突 | `model.config.use_cache = False` |
| 恢复训练后 loss 跳变 | 只存了模型没存优化器/调度器状态；或数据顺序改变 | 用 `resume_from_checkpoint` 完整恢复；固定随机种子 |
| 训练时 GPU 利用率很低、呈锯齿 | 数据加载（tokenize）成为瓶颈 | 预处理后就地缓存（`map` 带 `num_proc`）、多 worker DataLoader |
| 保存的模型忘了 tokenizer | 部署时 chat template 丢失 | `tokenizer.save_pretrained(same_dir)` |

## 5. 面试问答

**Q1：SFT 为什么要做 label masking？不掩码会怎样？**

<details><summary>参考答案</summary>

SFT 用的是自回归交叉熵，它会给序列里**每个位置**都分配一个"预测下一个 token"的监督信号。如果 prompt 部分也参与 loss，模型就被要求在给定前文的情况下高概率地"生成用户的问题"，这带来三个问题：

1. **学到不该学的东西**：prompt 是给定的而不是要生成的，把它当作目标会让模型在推理时倾向于复述用户输入。
2. **训练与推理目标不一致**：推理时我们只关心 prompt 之后的分布。
3. **loss 数值失真**：prompt 部分通常是高度可预测的（甚至是逐字复制），会拉低平均 loss，让你误以为模型学得好；同时回答部分的监督信号被稀释，长 prompt 的样本尤其明显。

实现上就是构造一份 `labels` 副本，把 prompt 对应的位置置为 `-100`，然后依赖 `CrossEntropyLoss(ignore_index=-100)` 让这些位置既不进入分子也不进入分母。注意区分场景：如果是领域继续预训练（DAPT），那全序列都应该算 loss。

</details>

**Q2：你的 SFT 训练 loss 从 2.4 降到 0.3，但人工评测说模型变差了。排查思路是什么？**

<details><summary>参考答案</summary>

按"数据 → 目标 → 超参 → 评测"的顺序查：

1. **数据层**：训练集与验证集是否有重叠？是否做了去重（精确 + 近似）？数据模板是否高度同质（例如所有回答都以同一句话开头），导致模型学会模板而不是内容？
2. **目标层**：掩码是否正确？`labels` 里 `-100` 的比例是多少？如果比例接近 1（几乎不掩码），loss 低只是因为 prompt 好预测，不代表回答好。另外检查 assistant 结尾 token 是否参与 loss。
3. **泄漏层**：如果开了 packing，确认 attention mask 是 block-diagonal 的；否则模型能看到下一条样本，loss 会异常低。
4. **超参层**：epoch 是否过多（3 轮以上在指令数据上很容易复读）？学习率是否过大？有没有监控通用能力的验证 loss？
5. **评测层**：人工评测的样本分布是否和训练数据一致？是否只看 loss 没看任务指标（生成式任务必须用生成式评测，例如 LLM-as-judge 或精确匹配）？

最终一定要建立**与 loss 解耦的任务评测集**，否则无法判断"loss 降"和"模型变好"之间的关系。

</details>

**Q3：SFT 训练需要监控哪些指标？OOM 时按什么顺序降负载？**

<details><summary>参考答案</summary>

**监控指标**：

- 训练 loss 与验证 loss（形状比绝对值重要：是否同步下降、是否出现分叉）；
- 学习率曲线（确认 warmup 与调度器按预期变化）；
- `grad_norm`（尖峰提示脏数据或学习率过大；长期极小提示学习率过小或梯度被裁过头）；
- 显存峰值与 GPU 利用率（利用率长期偏低说明数据管道是瓶颈）；
- 生成式抽样（每 N 步用固定 prompt 生成，肉眼检查退化，这是最便宜的有效监控）。

**OOM 降负载顺序**（代价从低到高）：

1. `per_device_train_batch_size=1` + 提高 `gradient_accumulation_steps` 保持有效 batch（几乎无损）；
2. 开 `gradient_checkpointing`（时间换显存，约 +20%～40% 时间）；
3. 降 `max_seq_len`（注意别静默截断重要内容）；
4. 换优化器为 `paged_adamw_8bit` 或 `adafactor`；
5. 上 ZeRO-2/3 或 FSDP 分片、CPU offload；
6. 改用 LoRA / QLoRA；
7. 换更小的模型或更短的序列任务。

</details>

## 6. 自测题

**1. 写出掩码后的 SFT 损失公式，并说明分母为什么不是 $T$。**

<details><summary>参考答案</summary>

$$
\mathcal{L} = -\frac{1}{\sum_t m_t}\sum_t m_t \log p_\theta(x_t\mid x_{<t})
$$

分母是被监督位置（$m_t=1$，即回答部分）的个数，而不是序列长度 $T$。如果分母用 $T$，那么 prompt 越长，loss 被稀释得越厉害，不同样本之间的 loss 就不可比——同样质量的回答，配长 prompt 会得到更低的 loss。`CrossEntropyLoss(ignore_index=-100)` 正是按"非忽略位置数"归一化的，与上式一致。

</details>

**2. 训练时 padding 应该放哪一侧？推理时呢？为什么？**

<details><summary>参考答案</summary>

训练时放**右侧**。因为因果语言模型的注意力掩码是下三角的，右侧 padding 不会影响前面 token 的表示；而左侧 padding 会让有效 token 的位置索引发生偏移，位置编码与注意力对齐出错（除非同时正确设置 `position_ids`）。

推理生成时放**左侧**。生成时是从序列末尾继续采样，左侧 padding 能保证所有样本的"生成起点"在同一列，便于批量采样与 KV cache 对齐。

这也是很多"训练正常、推理乱码"问题的根源：同一个 tokenizer 在两种场景下需要的 `padding_side` 不同。

</details>

**3. 你的数据集是 `{"messages": [...]}`，如何检查 chat template 用对了？**

<details><summary>参考答案</summary>

三个可执行的检查：

① **渲染后肉眼比对**：`print(tokenizer.apply_chat_template(messages, tokenize=False))`，确认角色标记与特殊 token 与模型卡（model card）里给出的示例完全一致。
② **往返检查**：把渲染出的文本再 tokenize，检查 BOS/EOS 是否只出现一次（`add_special_tokens=False` 时不应重复添加）。
③ **掩码检查**：把参与 loss 的片段 decode 出来，应当**只包含 assistant 的回答与结束标记**，不含 `system`/`user` 内容与模板符号。这一条能同时抓出模板错误与掩码错误。

补充：分词器的 `chat_template` 可以打印出来读一遍 Jinja 模板，特别是确认它是否有 `{% generation %}` 块（决定能否用 `return_assistant_tokens_mask`）。

</details>

**4. 你的 SFT 跑了 5 个 epoch，下游任务提升了但通用问答退化了，怎么办？**

<details><summary>参考答案</summary>

这是典型的灾难性遗忘。处理优先级：① **减少 epoch**（2～3 轮通常足够）并用验证集选最优 checkpoint，而不是用最后一个；② **数据混合**：掺入 5%～20% 通用指令数据，最有效且便宜；③ **降低学习率**，或改用 LoRA（冻结基座天然减轻遗忘）；④ 建立**通用能力评测**作为回归测试，训练中定期评估，一旦下降就早停；⑤ 若资源允许，用多任务联合训练代替单任务串行训练。补充：应记录"遗忘曲线"——通用能力随训练步数的变化，用它选停止点，而不是只看下游任务指标。

</details>

## 7. 延伸阅读

- [Training language models to follow instructions with human feedback (arXiv:2203.02155)](https://arxiv.org/abs/2203.02155) —— SFT → RM → PPO 三阶段，SFT 数据的标注方式。
- [LIMA: Less Is More for Alignment (arXiv:2305.11206)](https://arxiv.org/abs/2305.11206) —— 1,000 条高质量 SFT 数据的效果与"对齐主要是风格塑造"的论点。
- [Self-Instruct (arXiv:2212.10560)](https://arxiv.org/abs/2212.10560) —— 自举生成指令数据的方法。
- [Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer (arXiv:1910.10683)](https://arxiv.org/abs/1910.10683) —— 迁移学习与微调范式的系统研究。
- [HuggingFace — Chat Templates 文档](https://huggingface.co/docs/transformers/main/en/chat_templating) —— `apply_chat_template`、`return_assistant_tokens_mask` 与 `{% generation %}`。
- [HuggingFace TRL — SFTTrainer](https://huggingface.co/docs/trl/sft_trainer) 与 [TRL chat templates 指南](https://huggingface.co/docs/trl/main/en/chat_templates) —— assistant-only loss 的正确配置方式。
- [HuggingFace Transformers — Trainer](https://huggingface.co/docs/transformers/main_classes/trainer) —— 训练参数、断点续训、回调。
- [PyTorch — CrossEntropyLoss](https://pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html) —— `ignore_index` 的语义。
- [huggingface/trl PR #5988](https://github.com/huggingface/trl/pull/5988) —— "训练模板必须保留 stop token 在 loss mask 中"的相关修复。
- [Scaling Laws for Neural Language Models (arXiv:2001.08361)](https://arxiv.org/abs/2001.08361) —— 数据量、模型规模与损失之间的定量关系，用于理解"数据配比"的边界。

---

[⬅️ 返回本章目录](README.md)
