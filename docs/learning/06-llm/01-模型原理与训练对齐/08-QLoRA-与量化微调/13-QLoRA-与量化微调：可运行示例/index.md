---
article_id: kp-d29e86814c4bdb28
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-b68d23b02557
learning_sourceId: b68d23b02557
learning_order: 12
learning_objective: 理解并验证：QLoRA 与量化微调：可运行示例
---

# QLoRA 与量化微调：可运行示例

> **学习目标**：能够解释「QLoRA 与量化微调：可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：LoRA 的前向公式与参数量推导（见 [03 篇](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)）；显存五大组成与"模型状态 16 B/参数"的来历（见 [02 篇](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)）；浮点数的指数/尾数表示。
>
> **所属主题**：QLoRA 与量化微调 · 可运行示例

## 本次只学这一点

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

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/04-QLoRA与量化微调.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「QLoRA 与量化微调：可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/04-QLoRA与量化微调.md)
