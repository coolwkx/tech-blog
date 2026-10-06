---
article_id: kp-274d5561f7d18e3e
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-563344f304a7
learning_sourceId: 563344f304a7
learning_order: 6
learning_objective: 理解并验证：参数演示 + 流式输出
---

# 参数演示 + 流式输出

> **学习目标**：能够解释「参数演示 + 流式输出」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT 与 MLM 预训练目标（见《02-Transformer与注意力机制》）、Python 与 HTTP 基础、PyTorch 训练循环。
>
> **所属主题**：-大模型API与调用实践 · 可运行示例

## 本次只学这一点

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

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/06-提示工程/05-大模型API与调用实践.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「参数演示 + 流式输出」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/06-提示工程/05-大模型API与调用实践.md)
