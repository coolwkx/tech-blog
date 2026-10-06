---
article_id: kp-2aba1d0183a5bc68
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-314d719df758
learning_sourceId: 314d719df758
learning_order: 8
learning_objective: 理解并验证：PET：把自然语言模板解析成可填充的数据结构
---

# PET：把自然语言模板解析成可填充的数据结构

> **学习目标**：能够解释「PET：把自然语言模板解析成可填充的数据结构」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT 与 MLM（掩码语言模型）预训练目标、`[MASK]` token 的语义、`AutoModelForMaskedLM` 与 `AutoTokenizer`、HuggingFace `datasets.map(batched=True)`、PyTorch 训练循环与 `CrossEntropyLoss`。
>
> **所属主题**：项目实战笔记 06：电商评论分类（BERT+PET 与 BERT+P-Tuning） · 核心实现

## 本次只学这一点

```text
class HardTemplate(object):
 """硬模板，人工定义句子和 [MASK] 之间的位置关系。"""

 def __init__(self, prompt: str):
 self.prompt = prompt
 self.inputs_list = []
 self.custom_tokens = set(['MASK'])
 self.prompt_analysis

 def prompt_analysis(self):
 """'这是一条{MASK}评论：{textA}。'
 -> inputs_list = ['这','是','一','条','MASK','评','论','：','textA','。']
 custom_tokens = {'MASK', 'textA'}
 """
 idx = 0
 while idx < len(self.prompt):
 str_part = ''
 if self.prompt[idx] not in ['{', '}']:
 self.inputs_list.append(self.prompt[idx])
 if self.prompt[idx] == '{': # 进入自定义字段
 idx += 1
 while self.prompt[idx] != '}':
 str_part += self.prompt[idx]
 idx += 1
 elif self.prompt[idx] == '}':
 raise ValueError("Unmatched bracket '}', check your prompt.")
 if str_part:
 self.inputs_list.append(str_part)
 self.custom_tokens.add(str_part)
 idx += 1
```

**为什么不用正则**：模板里可能有任意多个自定义字段。手写字符级状态机行为完全可控，还能在遇到不匹配的 `}` 时立刻抛出明确错误。对"用户会自己改模板"的场景，**错误信息清晰**比代码简短更重要。

填充与编码：

```text
def __call__(self, inputs_dict, tokenizer, mask_length, max_seq_len=512):
 # ① 把模板里的占位符换成真实内容
 str_formated = ''
 for value in self.inputs_list:
 if value in self.custom_tokens:
 if value == 'MASK':
 str_formated += inputs_dict[value] * mask_length # 展开成 N 个 [MASK]
 else:
 str_formated += inputs_dict[value]
 else:
 str_formated += value

 # ② 编码成定长张量
 encoded = tokenizer(text=str_formated, truncation=True,
 max_length=max_seq_len, padding='max_length')
 outputs = {'text': ''.join(tokenizer.convert_ids_to_tokens(encoded['input_ids'])),
 'input_ids': encoded['input_ids'],
 'token_type_ids': encoded['token_type_ids'],
 'attention_mask': encoded['attention_mask']}

 # ③ 记录 [MASK] 位置——后续取 logits 的唯一依据
 mask_token_id = tokenizer.convert_tokens_to_ids(['[MASK]'])[0]
 outputs['mask_position'] = np.where(
 np.array(outputs['input_ids']) == mask_token_id)[0].tolist()
 return outputs
```

**`mask_position` 是整个 PET 的枢纽**。用 `np.where` 从 `input_ids` **反查**，而不是假设"模板里第 5 个字符是 MASK"——因为 tokenizer 可能按字切分（位置刚好对上），也可能对英文/数字做合并（位置偏移）。**从编码结果反查，永远不会错位。**

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/03-文本分类系统/06-项目-电商评论分类（BERT+PET与P-Tuning）.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「PET：把自然语言模板解析成可填充的数据结构」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/03-文本分类系统/06-项目-电商评论分类（BERT+PET与P-Tuning）.md)
