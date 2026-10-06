---
article_id: kp-a0c8a1f91da5cae2
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-c24a4924b596
learning_sourceId: c24a4924b596
learning_order: 10
learning_objective: 理解并验证：模型加载：训练/推理共用的一套分支
---

# 模型加载：训练/推理共用的一套分支

> **学习目标**：能够解释「模型加载：训练/推理共用的一套分支」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：因果语言模型与 `GPT2LMHeadModel`、多轮对话的上下文拼接、采样解码（temperature / top-k / top-p / repetition penalty）、Flask 模板渲染。
>
> **所属主题**：项目实战笔记 03：企业客服聊天机器人 · 核心实现

## 本次只学这一点

```python
# test_model.py / train.py 共用逻辑
if params.pretrained_model:
 model = GPT2LMHeadModel.from_pretrained(params.pretrained_model) # 加载已有权重
else:
 model_config = GPT2Config.from_json_file(params.config_json) # 按 json 建结构
 model = GPT2LMHeadModel(config=model_config)
model = model.to(params.device)

# 词表尺寸必须与模型 config 对齐，否则 lm_head 维度对不上
assert model.config.vocab_size == tokenizer.vocab_size
```

`config/config.json` 关键字段：

```json
{
 "model_type": "gpt2",
 "n_ctx": 1024, "n_positions": 1024,
 "n_embd": 768, "n_head": 12, "n_layer": 12,
 "activation_function": "gelu_new",
 "attn_pdrop": 0.1, "embd_pdrop": 0.1, "resid_pdrop": 0.1,
 "layer_norm_epsilon": 1e-05,
 "vocab_size": 13317,
 "tokenizer_class": "BertTokenizer",
 "task_specific_params": {
 "text-generation": { "do_sample": true, "max_length": 400 }
 }
}
```

`assert` 那一行是**廉价但极其有效**的自检：词表文件和 config 不匹配是最高频的低级错误，让它在启动阶段就崩，比训到一半报形状错误好得多。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/02-对话与生成系统/03-项目-企业客服聊天机器人.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「模型加载：训练/推理共用的一套分支」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/02-对话与生成系统/03-项目-企业客服聊天机器人.md)
