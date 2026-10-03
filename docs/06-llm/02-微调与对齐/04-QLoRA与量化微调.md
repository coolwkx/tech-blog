# QLoRA 与量化微调

> **一句话总结**：QLoRA 用"**nf4 分块量化冻结基座 + 双重量化压常量 + 分页优化器抗峰值**"三件套，把 7B 全参微调需要的上百 GB 显存压到单张 24 GB 消费级显卡可训的范围，代价是训练变慢、且量化基座上的 LoRA 权重不能直接合并回 nf4。
> **前置知识**：LoRA 的前向公式与参数量推导（见 [03 篇](03-LoRA原理与工程实践.md)）；显存五大组成与"模型状态 16 B/参数"的来历（见 [02 篇](02-全参微调与显存账本.md)）；浮点数的指数/尾数表示。
> **学完能做到**：
> 1. 说清 NF4 为什么按正态分位数分桶、分块量化与双重量化分别省了多少字节（能推算出 4.5 bits/参数 → 4.127 bits/参数）。
> 2. 写出可运行的 `BitsAndBytesConfig` + PEFT 配置，并说明每一项配置的作用与硬件前提。
> 3. 判断什么时候该用 QLoRA、什么时候该用 GPTQ/AWQ，以及为什么量化后的基座不能直接 merge adapter。

## 1. 核心概念

> **说明**：本节内容超出你提供的课程资料范围，基于公开文档与论文整理。
> NF4 分位数量化、双重量化、分页优化器、GPTQ/AWQ 的对比等，均来自公开论文与官方文档。

### 1.1 QLoRA 的三件套

| 技术 | 解决的问题 | 做法 | 省下什么 |
| --- | --- | --- | --- |
| **4-bit NormalFloat（NF4）** | 权重存储太占显存 | 假设权重近似正态分布，用正态分布的 16 个分位点作为量化桶（每桶等概率），并**分块**（默认块大小 64）用块内 absmax 归一化 | 权重从 2 字节/参数降到 4 bit/参数 |
| **双重量化（Double Quantization）** | 量化常量本身也要占地方 | 把第一层的 fp32 缩放常量再量化一次（fp8，块大小 256） | 常量开销从 0.5 bit/参数降到约 0.127 bit/参数 |
| **分页优化器（Paged Optimizers）** | 训练中的显存峰值导致 OOM | 借用 NVIDIA 统一内存，在显存紧张时把优化器状态自动换出到 CPU 内存，需要时再换入 | 抗住瞬时峰值，代价是变慢 |

前两项是**空间**优化，第三项是**峰值鲁棒性**优化。三者叠加后，7B 模型的权重约 3.6 GB，才使得"单卡 24 GB 微调 7B"成为现实。

### 1.2 量化位宽与显存/效果的取舍

| 方案 | 权重字节/参数（推导） | 7B 权重占用 | 可训练性 | 相对 bf16 的效果损失 | 典型用途 |
| --- | --- | --- | --- | --- | --- |
| fp32 | 4 | 28.0 GB | 全参可训 | 无（基准） | 小模型研究 |
| bf16 / fp16 | 2 | 14.0 GB | 全参可训 | 无 | 主流训练 |
| int8（LLM.int8()） | 1 + 少量离群列 fp16 | ≈ 7.0 GB+ | 冻结基座 + LoRA | 很小 | 推理；`load_in_8bit` |
| **nf4 + 双重量化** | **4.127/8 ≈ 0.5159** | **≈ 3.61 GB** | 冻结基座 + LoRA | 小（配合 LoRA 后可忽略） | QLoRA 训练 |
| nf4（无双重量化） | 4.5/8 = 0.5625 | ≈ 3.94 GB | 冻结基座 + LoRA | 同上，略优 | 追求极致精度时 |

推导过程见 2.3 与 2.4。**注意**：上表只是"权重"一项。QLoRA 的实际显存还要加 LoRA 参数及其优化器状态、激活值、CUDA 上下文（通常 0.5～1 GB）与临时缓冲。

### 1.3 三种训练配置的显存账本对照（7B）

| 项目 | 全参（bf16 + Adam） | LoRA（bf16 基座） | QLoRA（nf4 基座 + LoRA） |
| --- | --- | --- | --- |
| 基座权重 | 14 GB（bf16） | 14 GB（bf16，冻结） | 3.61 GB（nf4，冻结） |
| 基座梯度 | 14 GB | 0 | 0 |
| 优化器状态（基座） | 84 GB（fp32 主权重 + $m$ + $v$） | 0 | 0 |
| 适配器参数 + 梯度 + 优化器 | —— | 约 0.4～1 GB（$r=16$，视 target_modules） | 约 0.4～1 GB |
| 激活值 | 数 GB ~ 数十 GB（随 $b$、$s$ 变化） | 同量级，通常需要 gradient checkpointing | 同量级 |
| **单卡最小可行显存（粗估）** | **远超 80 GB，必须分片** | **约 18～24 GB**（$s$ 较短时） | **约 6～12 GB**（$s$ 较短时） |

> 上表中的激活值不是固定数：按 [02 篇](02-全参微调与显存账本.md) 的估算式，$s=2048,b=1$ 时仅激活就约 28 GiB，**但 QLoRA 场景下这一项并不会因为基座被量化而减少**——量化只省权重，不省激活。所以长序列的 QLoRA 依然要开 gradient checkpointing。

### 1.4 QLoRA 与训练后量化（PTQ）的区别

| 维度 | QLoRA | GPTQ | AWQ |
| --- | --- | --- | --- |
| 类别 | 量化 + 微调（Quantization-aware-ish fine-tuning） | 训练后量化 PTQ | 训练后量化 PTQ |
| 目标 | **省训练显存**，得到可用的下游模型 | **省推理显存/加速** | 同 GPTQ |
| 是否需要反向传播 | 需要（但只更新 LoRA 适配器） | 不需要 | 不需要 |
| 是否需要校准数据 | 需要下游训练数据 | 需要 128～1024 条校准样本 | 需要校准样本 |
| 核心机制 | nf4 分块量化 + 双重量化 + LoRA | 基于 Hessian 近似逐列量化并做误差补偿 | 按激活幅度做 per-channel 缩放，保护重要通道 |
| 量化对象 | 训练时的冻结基座 | 推理权重（通常 W4A16） | 推理权重（通常 W4A16） |
| 与 LoRA 组合 | 原生组合 | 可在量化模型上再挂 LoRA（支持有限，需注意内核兼容） | 同 GPTQ |
| 典型场景 | 单卡微调 7B～33B | 把已训好的模型压缩后部署 | 同 GPTQ，通常在部分任务上精度更好 |

**一句话区分**：**GPTQ/AWQ 是"训练完再压缩"，QLoRA 是"压缩着训练"。** 若你的目的是把已有模型部署得更省，用 GPTQ/AWQ；若你连训练都跑不起来，用 QLoRA。

## 2. 关键机制

### 2.1 量化的基本形式：仿射量化

最通用的量化形式是**分块仿射量化**：

$$
q = \mathrm{round}\!\left(\frac{x - \beta}{S}\right),\qquad
\hat{x} = q\cdot S + \beta
$$

其中 $S$ 是缩放因子（scale），$\beta$ 是零点（zero-point）。对**对称**量化（$\beta=0$，权重通常适用），$b$ 位有符号整数的取值区间是 $[-2^{b-1},\,2^{b-1}-1]$，于是

$$
S = \frac{\text{absmax}}{2^{b-1}-1},\qquad
q = \mathrm{clamp}\!\left(\mathrm{round}\!\left(\frac{x}{S}\right),\ -2^{b-1},\ 2^{b-1}-1\right),\qquad
\hat{x} = q\cdot S
$$

反量化即把整数桶乘回缩放因子。**误差来源**：舍入误差上界约为 $S/2$，即量化误差随**每个桶覆盖的数值范围**线性增长。这就是"分块量化"的动机——把一大片权重切成小块（QLoRA 默认块大小 64），每块独立计算 absmax，于是桶的覆盖范围由块内极值决定，而不是被全局极值放大。

### 2.2 NF4：为什么按正态分位数分桶

**问题**：均匀量化假设权重在区间内均匀分布。但实际预训练权重近似零均值正态分布——**大多数值集中在 0 附近，极值很少**。均匀分桶会把大量桶浪费在几乎没数据的尾部，而 0 附近数据密集的地方每桶只有很少的几个桶可用。

**NF4 的做法**（*QLoRA*, [arXiv:2305.14314](https://arxiv.org/abs/2305.14314)）：对于 $k$ 位量化（$k=4$，共 $2^k=16$ 个桶），取标准正态分布的分位点作为桶边界：

$$
q_i = \frac{1}{2}\left(
\frac{Q_X\!\left(\dfrac{i}{2^{k}+1}\right)}
{\left|Q_X\!\left(\dfrac{1}{2^{k}+1}\right)\right|} + 1
\right),\qquad i = 0,1,\dots,2^{k}
$$

其中 $Q_X(\cdot)$ 是标准正态分布的分位数函数。这个构造把 $[-1,1]$ 区间切成 16 段，使得**每个桶在标准正态分布下的概率质量近似相等**（information-theoretically optimal for zero-mean normal data，如论文所述）。

**直觉总结**：与其给"每个数值区间相同的宽度"，不如给"**每个桶相同的数据量**"。这样量化误差在权重的实际分布上近似均匀，而不是在 0 附近极度浪费精度。

### 2.3 分块量化与常量开销（推导）

分块量化的存储由两部分组成：

1. **量化后的权重**：$k$ bit/参数（$k=4$）；
2. **每块的缩放常量**：块大小 $B=64$，每个块一个 fp32 absmax，即 $32$ bit / $64$ 参数 $= 0.5$ bit/参数。

于是**没有双重量化时**：

$$
\text{总开销} = 4 + 0.5 = 4.5\ \text{bit/参数} = 0.5625\ \text{字节/参数}
$$

7B 上：$4.5\times7\times10^9 / 8 = 3.94\times10^9$ 字节 $\approx 3.94$ GB。

### 2.4 双重量化：再省 0.37 bit/参数（推导）

**做法**：把那 $N = P/B$ 个 fp32 常量，再用块大小 $B_2=256$ 做一次 fp8（8 bit）量化：

- 第二层权重（即第一层的常量）本身：$8$ bit / 64 参数 $= 0.125$ bit/参数；
- 第二层的常量：一个 fp32 每 256 个第一层常量，即 $32 / (256\times64) = 32/16384 \approx 0.00195$ bit/参数。

$$
\text{双重量化后总开销} = 4 + 0.125 + 0.00195 = 4.127\ \text{bit/参数}
$$

节省：

$$
4.5 - 4.127 = 0.373\ \text{bit/参数}
$$

7B 上：$4.127\times7\times10^9 / 8 = 3.61\times10^9$ 字节 $\approx 3.61$ GB（相比 3.94 GB 省约 0.33 GB）。

> 这个 $0.373$ bit/参数的推导结果与 QLoRA 论文中报告的"双重量化平均为每个参数节省约 0.37 bit"一致，可作为交叉验证。

### 2.5 分页优化器

训练中的 OOM 往往不是平均显存不够，而是**瞬时峰值**超了：例如某一步的激活重算、或者优化器状态更新时的临时张量。

分页优化器借助 NVIDIA 的统一内存（unified memory）机制，允许把优化器状态"换页"到 CPU 内存，显存充足时自然换回。

| 特性 | 说明 |
| --- | --- |
| 解决的问题 | 显存瞬时峰值导致的 OOM |
| 配置 | `TrainingArguments(optim="paged_adamw_8bit")` 或 `paged_adamw_32bit` |
| 代价 | 换页时 PCIe 传输会显著拖慢该步；吞吐下降幅度取决于换页频率 |
| 与 gradient checkpointing 的关系 | 互补：一个压激活峰值，一个压优化器状态峰值 |

### 2.6 为什么"量化基座 + LoRA"还能保住效果

这是 QLoRA 最反直觉的地方：基座被压到 4 bit，按理说精度损失应该传导到下游表现，但实践中 QLoRA 通常能在下游任务上接近 16-bit LoRA。四个层面的解释：

1. **梯度不流经量化权重**。QLoRA 中基座完全冻结，只有 LoRA 的 $A$、$B$ 参与反向传播。前向时把 nf4 权重**反量化到 bf16** 参与计算：

   $$
   h = \mathrm{dequant}(W^{\text{nf4}})\,x + \frac{\alpha}{r}BAx
   $$

   反向传播只计算 $A$、$B$ 的梯度，量化误差不会通过梯度放大器被反复放大。

2. **LoRA 会主动补偿量化误差**。把量化误差记作 $E = \mathrm{dequant}(W^{\text{nf4}}) - W$。微调时 $BA$ 的目标是拟合下游任务所需的更新 $\Delta W^\star$；由于 $E$ 在前向中是一个固定的偏置，**低秩分支可以在拟合任务的同时部分吸收 $E$ 的影响**。可以把它理解为：适配器的容量被用来同时承担"任务适配"和"误差补偿"两件事。

3. **NF4 的量化误差在分布意义上是均匀的**。如 2.2 所述，等概率分桶让误差在权重实际分布的每个区间上量级相近，避免出现"大部分权重误差很小、少数权重误差巨大"的长尾，而长尾误差恰恰最容易破坏模型行为。

4. **量化误差近似于加性噪声，且被后续层的非线性平均**。4 bit 的逐元素误差在通过 LayerNorm、注意力 softmax、残差堆叠后部分被平均掉。这也是为什么**量化的层越靠后越敏感、量化 MLP 比量化注意力更危险**这类经验的存在。

**但要注意边界**：这些解释都是直觉层面的，不能推出"量化无损"。经验上更可靠的说法是：**只要微调数据充分，LoRA 适配器能吸收相当一部分量化损失；如果数据极少或任务对数值极敏感（如长链推理、代码生成），量化损失会显现。**

### 2.7 训练时的显存换算细节

一个常被忽略的点：QLoRA 的反量化是**按块即时发生**的，前向中会把当前块的 nf4 权重反量化成 bf16。这意味着：

$$
B_{\text{峰值}} \approx B_{\text{nf4 权重}} + B_{\text{当前反量化的块}} + B_{\text{激活}} + B_{\text{适配器}}
$$

由于是分块处理，反量化产生的临时张量规模有限，但**并非 0**。同理，`bnb_4bit_compute_dtype` 选择的计算精度会影响这一项的峰值：

| `bnb_4bit_compute_dtype` | 效果 | 显存 |
| --- | --- | --- |
| `torch.bfloat16` | 推荐，动态范围同 fp32 | 中 |
| `torch.float16` | 老卡兼容（无 bf16 支持时） | 中 |
| `torch.float32` | 精度最高但慢且费显存 | 高 |

### 2.8 合并限制

QLoRA 训完后**不能直接把 adapter 合并进 nf4 权重**。原因：nf4 是分块量化的——$W^{\text{nf4}}$ 的每个块有一个 absmax 常量，$\Delta W$ 与它的和不再满足"同块同尺度"的前提，无法用原量化参数表示。正确路径是：

```text
nf4 基座 ──(反量化)──► bf16/fp16 权重 ──(加上 ΔW)──► 合并后的完整模型 ──(可选)──► 重新 GPTQ/AWQ 量化用于推理
```

这条路径意味着**合并会临时占用一份完整精度的权重**（7B 约 14 GB），并且合并产物是 fp16/bf16 的普通模型，失去了 nf4 的存储优势。多数生产部署的做法是：**QLoRA 只用于训练，部署时用 bf16 或者重新做 PTQ 量化。**

## 3. 可运行示例

下面给出 QLoRA 的完整配置片段。

> **说明**：本机没有 GPU、没有安装 `torch`/`transformers`/`peft`/`bitsandbytes`，**代码未在本机执行**；参数取值来自各库官方文档的推荐配置。

依赖与硬件前提：

| 项 | 要求 |
| --- | --- |
| Python | 3.9+ |
| 库 | `torch>=2.1`、`transformers>=4.36`、`peft>=0.6`、`bitsandbytes>=0.41`、`accelerate`、`datasets` |
| GPU | **NVIDIA CUDA GPU**（bitsandbytes 不支持 CPU / Apple MPS）；对 compute capability 有下限要求，具体以下载安装时 bitsandbytes 官方文档的 requirements 为准 |
| 显存 | 7B / $s\le1024$ / gradient checkpointing 开：约 8～12 GB 可跑；13B 建议 24 GB |

```python
# -*- coding: utf-8 -*-
"""
QLoRA 配置骨架：nf4 量化基座 + LoRA 适配器 + 分页优化器。

注意：需要 NVIDIA GPU 且安装 bitsandbytes，CPU 环境无法运行本脚本。
"""

from __future__ import annotations

import torch
from datasets import Dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    DataCollatorForSeq2Seq,
    Trainer,
    TrainingArguments,
)

MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"  # 换成你要微调的基座


def build_bnb_config() -> BitsAndBytesConfig:
    """QLoRA 三件套中的前两件：NF4 + 双重量化。"""
    return BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",              # 4-bit NormalFloat
        bnb_4bit_use_double_quant=True,          # 双重量化：量化常量也压
        bnb_4bit_compute_dtype=torch.bfloat16,   # 反量化后的计算精度
    )


def load_quantized_model(model_id: str):
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=build_bnb_config(),
        device_map="auto",           # 需要 accelerate
        trust_remote_code=True,
    )
    # 关键：把 LayerNorm 等提成 fp32、关闭 cache、准备 k-bit 训练
    model = prepare_model_for_kbit_training(
        model, use_gradient_checkpointing=True
    )
    model.config.use_cache = False   # 与 gradient checkpointing 冲突，必须关
    return model, tokenizer


def attach_lora(model):
    config = LoraConfig(
        r=16,
        lora_alpha=32,               # alpha/r = 2
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
    )
    model = get_peft_model(model, config)
    model.print_trainable_parameters()   # 必须确认可训练参数不为 0
    return model


def build_dataset(tokenizer, texts, max_len: int = 512) -> Dataset:
    """最简数据管道；生产环境请用 chat template + label masking，见第 05 篇。"""

    def _tok(example):
        out = tokenizer(example["text"], truncation=True, max_length=max_len)
        out["labels"] = list(out["input_ids"])
        return out

    return Dataset.from_dict({"text": texts}).map(_tok, remove_columns=["text"])


def build_trainer(model, tokenizer, train_ds) -> Trainer:
    args = TrainingArguments(
        output_dir="./qlora_out",
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,        # 有效 batch = 1 × 8 × 卡数
        num_train_epochs=3,
        learning_rate=2e-4,                   # LoRA 常用 1e-4 ~ 3e-4
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        weight_decay=0.0,
        bf16=True,                            # 有 bf16 支持的卡优先用；不要和 fp16 同开
        gradient_checkpointing=True,
        optim="paged_adamw_8bit",             # 第三件套：分页优化器
        logging_steps=10,
        save_strategy="epoch",
        report_to=[],
    )
    collator = DataCollatorForSeq2Seq(
        tokenizer, padding=True, pad_to_multiple_of=8, label_pad_token_id=-100
    )
    return Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        data_collator=collator,
        tokenizer=tokenizer,
    )


def main() -> None:
    model, tokenizer = load_quantized_model(MODEL_ID)
    model = attach_lora(model)
    train_ds = build_dataset(tokenizer, ["你好，请介绍一下你自己。"] * 32)
    trainer = build_trainer(model, tokenizer, train_ds)
    trainer.train()
    # 只保存适配器（几十 MB），不要保存整个基座
    trainer.model.save_pretrained("./qlora_out/adapter")
    tokenizer.save_pretrained("./qlora_out/adapter")


if __name__ == "__main__":
    main()
```

**部署时的合并路径**（必须先反量化，不能直接合并进 nf4）：

```python
# -*- coding: utf-8 -*-
"""把 QLoRA 适配器合并回 bf16 基座（需要 GPU 与 bitsandbytes）。"""

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

BASE = "Qwen/Qwen2.5-1.5B-Instruct"
ADAPTER = "./qlora_out/adapter"

tokenizer = AutoTokenizer.from_pretrained(ADAPTER)
# 用 bf16 加载基座（不量化），才能安全地做加法
base = AutoModelForCausalLM.from_pretrained(BASE, torch_dtype=torch.bfloat16)
model = PeftModel.from_pretrained(base, ADAPTER)

with torch.no_grad():
    merged = model.merge_and_unload()   # 内部在 fp32/bf16 上完成 W0 + alpha/r * BA
merged.save_pretrained("./merged_bf16")
tokenizer.save_pretrained("./merged_bf16")
print("合并完成：产物是 bf16 全精度模型，如需 4-bit 部署请重新做 GPTQ/AWQ 量化")
```

## 4. 常见坑

| 现象 | 原因 | 解决 |
| --- | --- | --- |
| `load_in_4bit=True` 报错或直接崩 | 非 NVIDIA GPU、驱动/CUDA 不匹配，或 compute capability 不满足 bitsandbytes 要求 | 换 CUDA GPU；按官方 requirements 对齐驱动与库版本 |
| 训练时报 `Expected all tensors to be on the same device` | `device_map="auto"` 与 Trainer/accelerate 的设备分配冲突 | 用 `accelerate config` 统一配置，或显式 `device_map={"": 0}` |
| 开了 gradient checkpointing 后报 cache 相关错误 | `use_cache=True` 与重计算冲突 | `model.config.use_cache = False` |
| 训练 loss 是 NaN | fp16 溢出（旧卡无 bf16 时） | 改 `bnb_4bit_compute_dtype=torch.float32` 或换支持 bf16 的卡；不要同时开 fp16 与 bf16 |
| 可训练参数为 0 | `target_modules` 与模型的真实层名不匹配 | 打印 `named_modules()` 确认真实命名，再填 `target_modules` |
| 保存的 checkpoint 有几十 GB | 保存了整模型而不是适配器 | 只 `save_pretrained` PEFT 模型（`PeftModel`），或设置 `save_only_model`/过滤 |
| 合并 adapter 时报 dtype 或量化相关错误 | 试图把 LoRA 合并进 nf4 权重 | 用 bf16 重新加载基座再合并（见 2.8 与示例二） |
| 合并后效果下降 | 合并时的低精度加法舍入 | 在 fp32 下合并；或部署时不合并 |
| 训练比 16-bit LoRA 慢很多 | 反量化开销 + 分页换页 | 调大 micro-batch 摊薄开销；确认没有频繁换页（换页时 PCIe 是瓶颈） |
| 推理时忘记反量化路径，直接加载 nf4 权重做普通推理 | 混淆了"训练配置"与"部署配置" | 部署走 vLLM/llama.cpp 等推理栈，或使用 GPTQ/AWQ 量化产物 |
| 长序列仍然 OOM | 量化只省权重，不省激活 | 开 gradient checkpointing；降 `max_seq_len`；减小 micro-batch + 梯度累积 |
| 用 GPTQ 量化模型再挂 LoRA 时训练报错 | GPTQ 内核与训练路径兼容性有限 | 确认 PEFT 对该量化后端的支持情况；必要时改用 nf4 训练 |

## 5. 面试问答

**Q1：NF4 和普通的 INT4 均匀量化有什么区别？为什么 NF4 更好？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

均匀 INT4 把数值区间等宽切成 16 段；NF4 则按**标准正态分布的分位点**切分，使每个桶在正态分布下拥有近似相等的概率质量。

预训练权重近似零均值正态分布，绝大多数值集中在 0 附近。均匀分桶会让大量桶浪费在几乎无数据的尾部区间，而 0 附近数据密集处可用桶很少，导致均方量化误差偏大。NF4 的等概率分桶让误差在整个分布上近似均匀，因此在**权重服从正态分布**这个前提下，NF4 的量化误差小于均匀 INT4。

补充：NF4 在论文中是通过对正态分布分位数归一化到 $[-1,1]$ 构造的，并且实际使用时会配合分块（块大小 64）的 absmax 缩放，以处理不同权重的尺度差异。

</details>

**Q2：双重量化具体省了多少？请推导。**

<details markdown="1">
<summary markdown="1">参考答案</summary>

不分块量化的权重本身是 4 bit/参数。分块量化后每块（64 个参数）需要一个 fp32 的 absmax 常量，即 $32/64 = 0.5$ bit/参数，合计 $4.5$ bit/参数。

双重量化把这批常量再用块大小 256 的 fp8 量化：常量本身占 $8/64 = 0.125$ bit/参数，第二层常量占 $32/(256\times64) \approx 0.00195$ bit/参数。合计 $4 + 0.125 + 0.00195 = 4.127$ bit/参数。

节省 $4.5 - 4.127 = 0.373$ bit/参数，与论文报告的"约 0.37 bit/参数"一致。在 7B 上相当于从约 3.94 GB 降到约 3.61 GB。

</details>

**Q3：QLoRA 微调后的 adapter 能直接合并进 4-bit 权重吗？为什么？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

不能。nf4 是**分块量化**：每个 64 元素的块共享一个 absmax 缩放常量，块内所有元素共用一套量化刻度。合并需要计算 $W_{\text{nf4}} + \frac{\alpha}{r}BA$，而加法结果的数值范围与原来不同，无法用同一组量化常量表示；强行合并会破坏量化结构或引入巨大误差。

正确做法是先用 bf16/fp16 重新加载基座（即反量化），在精确精度下完成加法，得到一份普通精度的合并模型；如果需要 4-bit 部署，就对合并后的模型重新做 GPTQ/AWQ 等训练后量化。多数生产实践干脆不合并，直接以"bf16 全精度基座 + adapter"或"重新 PTQ 量化 + 独立推理引擎"的方式部署。

</details>

## 6. 自测题

**1. 4-bit 分块量化、块大小 64、不开双重量化时，总存储是多少 bit/参数？7B 模型权重占多少 GB？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

$4 + 32/64 = 4.5$ bit/参数。7B：$4.5\times7\times10^9/8 = 3.9375\times10^9$ 字节 $\approx 3.94$ GB。开双重量化后为约 3.61 GB。

</details>

**2. 你的目标是"把已经训好的 13B 模型部署到一张 24 GB 卡上做推理"，应该选 QLoRA 还是 GPTQ/AWQ？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

选 GPTQ 或 AWQ。QLoRA 的价值在**训练阶段**省显存，它产出的仍然是需要训练/合并的模型；对"纯推理压缩"这个目标，GPTQ/AWQ 是专门的训练后量化方案，通常配合 vLLM/TensorRT-LLM 等推理栈能获得数倍吞吐提升。QLoRA 在这个场景下不带来额外收益。

（如果既要在 24 GB 上继续微调，又要推理，可以先用 QLoRA 微调、合并成 bf16，再用 GPTQ/AWQ 量化部署。）

</details>

**3. 为什么说"量化只省权重、不省激活"？这对长序列 QLoRA 意味着什么？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

QLoRA 的量化针对的是模型权重（$P$ 个参数），激活值由前向传播的中间张量决定，形状是 $b\times s\times h$ 和 $b\times a\times s\times s$，与权重存储精度无关。因此即便权重压到 4 bit，激活仍然按计算精度（通常 bf16）分配。

对长序列意味着：$s$ 增大时激活的二次项 $a s^2$ 会迅速成为显存瓶颈，此时必须开 gradient checkpointing、降低 micro-batch 并配合梯度累积，或者使用 FlashAttention 这类不物化完整注意力矩阵的实现。

</details>

**4. QLoRA 训练中，反向传播会更新被量化的基座权重吗？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

不会。基座权重在 QLoRA 中是冻结的（`requires_grad=False`），并且量化权重本身也无法直接承载高精度梯度更新。反向传播只计算 LoRA 的 $A$、$B$ 的梯度。前向时 nf4 权重被反量化到 `bnb_4bit_compute_dtype` 指定的精度参与矩阵乘，反量化是前向计算的一部分，不产生对量化常量的梯度。

这也解释了为什么 QLoRA 的显存账本里完全没有"基座梯度 + 基座优化器状态"这两项（对比全参微调的 14 GB + 84 GB）。

</details>

**5. 用 `paged_adamw_8bit` 之后训练变慢了很多，怎么判断是"分页换页"导致的？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

观察点：① 用 `nvidia-smi` 或 `torch.cuda.memory_summary()` 看显存是否长期贴着实测上限；② 用 profiler 或 `nvidia-smi dmon` 看 PCIe 吞吐是否出现周期性尖峰；③ 观察每步耗时是否呈双峰分布（部分步特别慢）。如果三个信号都有，说明优化器状态在被反复换出换入。

处理：降低 micro-batch 并提高梯度累积、缩短序列长度、开启 gradient checkpointing 把峰值让给优化器状态，或者干脆改用 `paged_adamw_32bit` 之外更省显存的方案（如 Adafactor）。慢但能跑通常比 OOM 好，所以这是一个"用时间换显存"的取舍。

</details>

## 7. 延伸阅读

- [QLoRA: Efficient Finetuning of Quantized LLMs (arXiv:2305.14314)](https://arxiv.org/abs/2305.14314) —— NF4、双重量化、分页优化器与 Guanaco 实验。
- [LoRA: Low-Rank Adaptation of Large Language Models (arXiv:2106.09685)](https://arxiv.org/abs/2106.09685) —— QLoRA 所组合的适配器方法。
- [LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale (arXiv:2208.07339)](https://arxiv.org/abs/2208.07339) —— 8-bit 量化与离群特征处理。
- [GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers (arXiv:2210.17323)](https://arxiv.org/abs/2210.17323)。
- [AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration (arXiv:2306.00978)](https://arxiv.org/abs/2306.00978)。
- [HuggingFace PEFT — Quantization 指南](https://huggingface.co/docs/peft/developer_guides/quantization) —— 与 QLoRA/GPTQ/AWQ/eetq 的集成方式。
- [HuggingFace bitsandbytes 文档](https://huggingface.co/docs/bitsandbytes/index) —— `BitsAndBytesConfig` 全部字段与硬件要求。
- [HuggingFace Transformers — Quantization 总览](https://huggingface.co/docs/transformers/main/en/quantization/overview) —— 各量化后端的横向对比。
- [bitsandbytes 官方仓库](https://github.com/bitsandbytes-foundation/bitsandbytes) —— requirements 与 GPU 兼容性矩阵。
- [GPTQ 官方仓库](https://github.com/AutoGPTQ/AutoGPTQ) 与 [AWQ 官方仓库](https://github.com/mit-han-lab/llm-awq)。

---

[⬅️ 返回本章目录](README.md)
