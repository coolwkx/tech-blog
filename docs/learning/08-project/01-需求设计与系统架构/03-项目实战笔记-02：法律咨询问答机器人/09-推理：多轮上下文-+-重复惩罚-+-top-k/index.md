---
article_id: kp-4c7df10370a80f1e
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-3e5bdcfe80e4
learning_sourceId: 3e5bdcfe80e4
learning_order: 9
learning_objective: 理解并验证：推理：多轮上下文 + 重复惩罚 + top-k
---

# 推理：多轮上下文 + 重复惩罚 + top-k

> **学习目标**：能够解释「推理：多轮上下文 + 重复惩罚 + top-k」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer Decoder 结构与自注意力、因果语言模型（CLM）的 shift 对齐损失、PyTorch 的 `Dataset / DataLoader / collate_fn`、HuggingFace `transformers` 的 `GPT2LMHeadModel` 与 `BertTokenizerFast`。
>
> **所属主题**：项目实战笔记 02：法律咨询问答机器人 · 核心实现

## 本次只学这一点

```python
# interact.py（精简）
history = [] # 每个元素是一条 utterance 的 token id 列表
while True:
    text = input("user:")
    history.append(tokenizer.encode(text, add_special_tokens=False))

    input_ids = [tokenizer.cls_token_id]
    for history_utr in history[-pconf.max_history_len:]: # 只保留最近 3 轮
        input_ids.extend(history_utr)
        input_ids.append(tokenizer.sep_token_id)

        input_ids = torch.tensor(input_ids, dtype=torch.long, device=device).unsqueeze(0)
        response = []
        for _ in range(pconf.max_len):
            logits = model(input_ids=input_ids).logits
            next_token_logits = logits[0, -1, :] # 只关心最后一个位置的分布

            # ① 重复惩罚：已生成过的 token，logit 除以惩罚系数 → 概率下降
            for tid in set(response):
                next_token_logits[tid] /= pconf.repetition_penalty

                # ② 屏蔽 [UNK]
                next_token_logits[tokenizer.convert_tokens_to_ids('[UNK]')] = -float('Inf')

                # ③ top-k 过滤：只保留概率最高的 k 个 token
                filtered_logits = top_k_top_p_filtering(next_token_logits, top_k=pconf.topk)

                # ④ 按概率采样（而非 argmax，避免输出死板）
                next_token = torch.multinomial(F.softmax(filtered_logits, dim=-1), num_samples=1)

                if next_token.item == tokenizer.sep_token_id: # 遇到 [SEP] = 回答结束
                    break
                response.append(next_token.item)
                input_ids = torch.cat((input_ids, next_token.unsqueeze(0)), dim=1)

                history.append(response)
                print("chatbot:" + "".join(tokenizer.convert_ids_to_tokens(response)))
```

`top_k_top_p_filtering` 的实现：

```python
def top_k_top_p_filtering(logits, top_k=0, filter_value=-float('Inf')):
    assert logits.dim == 1
    top_k = min(top_k, logits.size(-1))
    if top_k > 0:
        # torch.topk(...)[0][..., -1, None] 是第 k 大的那个值
        indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
        logits[indices_to_remove] = filter_value
        return logits
```

**`[SEP]` 一符两用的巧妙之处**：训练时它分隔问题与回答，推理时它就自然成了"回答结束标志"。不需要额外的 EOS token，也不用改词表。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/02-对话与生成系统/02-项目-法律咨询问答机器人.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「推理：多轮上下文 + 重复惩罚 + top-k」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/02-对话与生成系统/02-项目-法律咨询问答机器人.md)
