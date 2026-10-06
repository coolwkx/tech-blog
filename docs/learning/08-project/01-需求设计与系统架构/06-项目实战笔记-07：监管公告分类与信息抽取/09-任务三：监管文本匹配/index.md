---
article_id: kp-e4bd10353ad61c81
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-5ddeeee1c909
learning_sourceId: 5ddeeee1c909
learning_order: 9
learning_objective: 理解并验证：任务三：监管文本匹配
---

# 任务三：监管文本匹配

> **学习目标**：能够解释「任务三：监管文本匹配」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：In-context Learning / Zero-shot / Few-shot 的基本概念、Chat 模型的 `messages` 结构（system / user / assistant）、JSON 与正则表达式、Ollama 本地模型调用。
>
> **所属主题**：项目实战笔记 07：监管公告分类与信息抽取 · 核心实现

## 本次只学这一点

```text
# regulatory_text_matching.py
from rich import print
import ollama

# 提供相似、不相似的语义匹配例子
examples = {
 '是': [
 ('某机构未按规定披露信息被处罚。', '该机构因信息披露违规被行政处罚。'),
 ],
 '不是': [
 ('监管部门发布行政处罚决定书。', '行业协会举办年度技术交流会。'),
 ('监管部门发布备案指引。', '某公司发布新款手机。')
 ]
}

def init_prompts:
 pre_history = [{"role": "system",
 "content": "现在你需要帮助我完成文本匹配任务，当我给你两个句子时，你需要回答我这两句话语义是否相似。只需要回答是否相似，不要做多余的回答。"}]

 for key, sentence_pairs in examples.items():
 for sentence_pair in sentence_pairs:
 sentence1, sentence2 = sentence_pair
 pre_history.append({"role": "user",
 "content": f'句子一: {sentence1}\n句子二: {sentence2}\n上面两句话是相似的语义吗？'})
 pre_history.append({"role": "assistant", "content": key})

 return {'pre_history': pre_history}

def inference(sentence_pairs: list, custom_settings: dict):
 for sentence_pair in sentence_pairs:
 sentence1, sentence2 = sentence_pair
 sentence_with_prompt = f'句子一: {sentence1}\n句子二: {sentence2}\n上面两句话是相似的语义吗？'
 response = ollama.chat(model="qwen2.5:7b",
 messages=[*custom_settings["pre_history"],
 {"role": 'user', "content": sentence_with_prompt}])
 print(f'sentence_pair:{sentence_pair}')
 print(f'inference answer: {response["message"]["content"]}')
```

**示例的分布设计值得注意**：`'是'` 给了 1 例，`'不是'` 给了 2 例。这种**非均衡的示例分布**会带来一个风险——模型可能偏向输出"不是"。

**Few-shot 的第二类坑：示例的类别分布会影响输出倾向。** 如果两个类别的示例数量差很多，或者某类示例的写法更有代表性，模型会偏向那一类。实践中应该：

- 让每个类别的示例数量尽量均衡（1:1 或 2:2）；
- 示例的顺序也建议打乱，避免"最后一组示例"对输出产生过强影响（这叫 **recency bias**，LLM 对 Prompt 尾部的信息更敏感）。

`sentence_with_prompt` 的拼接方式：

```python
f'句子一: {sentence1}\n句子二: {sentence2}\n上面两句话是相似的语义吗？'
```

注意这里用了 `\n` 而不是逗号分隔。**在 Prompt 里用换行做结构化分隔**（而不是把内容串成一行）是个好习惯：它让每一段信息在 token 层面更清晰，模型更容易分辨"哪部分是句子一、哪部分是句子二、哪部分是问题"。对于 `sentence1` 里本身可能含逗号/句号的中文文本，换行分隔尤其重要。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/03-文本分类系统/07-项目-监管公告分类与信息抽取.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「任务三：监管文本匹配」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/03-文本分类系统/07-项目-监管公告分类与信息抽取.md)
