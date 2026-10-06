---
article_id: kp-ed53c2886d51a715
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-b7b8e8f583cb
learning_sourceId: b7b8e8f583cb
learning_order: 13
learning_objective: 理解并验证：SFT 训练循环与框架：可运行示例
---

# SFT 训练循环与框架：可运行示例

> **学习目标**：能够解释「SFT 训练循环与框架：可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：因果语言模型的训练目标；tokenizer 与特殊 token（BOS/EOS/PAD）；交叉熵损失；LoRA 的注入方式（见 [03 篇](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)）与显存账本（见 [02 篇](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)）。
>
> **所属主题**：SFT 训练循环与框架 · 可运行示例

## 本次只学这一点

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

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/05-SFT训练循环与框架.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「SFT 训练循环与框架：可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/05-SFT训练循环与框架.md)
