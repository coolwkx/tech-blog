---
article_id: kp-3f7b45fc7d950a92
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-c24a4924b596
learning_sourceId: c24a4924b596
learning_order: 8
learning_objective: 理解并验证：解码：四步过滤出下一个 token
---

# 解码：四步过滤出下一个 token

> **学习目标**：能够解释「解码：四步过滤出下一个 token」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：因果语言模型与 `GPT2LMHeadModel`、多轮对话的上下文拼接、采样解码（temperature / top-k / top-p / repetition penalty）、Flask 模板渲染。
>
> **所属主题**：项目实战笔记 03：企业客服聊天机器人 · 核心实现

## 本次只学这一点

```python
def top_k_top_p_filtering(logits, top_k=0, filter_value=-float('Inf')):
    assert logits.dim == 1
    top_k = min(top_k, logits.size(-1)) # 安全检查
    if top_k > 0:
        # torch.topk(...)[0][..., -1, None] 取"第 k 大的值"，形状保持为 [1] 便于广播
        indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
        logits[indices_to_remove] = filter_value # 截断尾部：置 -inf
        return logits

    response = []
    for _ in range(pconf.max_len):
        logits = model(input_ids=input_ids).logits
        next_token_logits = logits[0, -1, :] # 只要最后一个位置的分布

        # ① 重复惩罚：已生成过的 token，概率压低
        for tid in set(response):
            next_token_logits[tid] /= pconf.repetition_penalty # 10.0

            # ② 屏蔽 [UNK]：绝不允许输出未知词
            next_token_logits[tokenizer.convert_tokens_to_ids('[UNK]')] = -float('Inf')

            # ③ top-k 过滤：只保留概率最高的 k 个
            filtered_logits = top_k_top_p_filtering(next_token_logits, top_k=pconf.topk) # 4

            # ④ 按概率采样（不是 argmax！）
            next_token = torch.multinomial(F.softmax(filtered_logits, dim=-1), num_samples=1)

            if next_token.item == tokenizer.sep_token_id: # 生成结束
                break
            response.append(next_token.item)
            input_ids = torch.cat((input_ids, next_token.unsqueeze(0)), dim=1)
```

**为什么必须用 `multinomial` 而不是 `argmax`**：`argmax` 是贪心解码，每一步都取概率最高的 token。它会稳定地生成"最安全"的句子，结果是回答干瘪、且极易陷入"我最喜欢…我最喜欢…"的循环。按概率采样则保留了多样性，配合 top-k 又不会抽到明显不合理的尾部 token。

**`set(response)` 而不是 `response`**：重复惩罚只关心"这个 token 出现过没有"，不关心出现几次。用 `set` 去重后遍历，避免对同一个 id 反复做除法（虽然结果一样，但语义更清晰、迭代更少）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/02-对话与生成系统/03-项目-企业客服聊天机器人.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「解码：四步过滤出下一个 token」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/02-对话与生成系统/03-项目-企业客服聊天机器人.md)
