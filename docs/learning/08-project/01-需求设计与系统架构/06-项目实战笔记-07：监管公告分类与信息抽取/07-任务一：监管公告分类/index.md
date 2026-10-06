---
article_id: kp-bdab94b6343f5d1a
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-5ddeeee1c909
learning_sourceId: 5ddeeee1c909
learning_order: 7
learning_objective: 理解并验证：任务一：监管公告分类
---

# 任务一：监管公告分类

> **学习目标**：能够解释「任务一：监管公告分类」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：In-context Learning / Zero-shot / Few-shot 的基本概念、Chat 模型的 `messages` 结构（system / user / assistant）、JSON 与正则表达式、Ollama 本地模型调用。
>
> **所属主题**：项目实战笔记 07：监管公告分类与信息抽取 · 核心实现

## 本次只学这一点

```text
# regulatory_classify.py
from rich import print
from rich.console import Console
import ollama

# 提供所有类别以及每个类别下的样例
class_examples = {
 '处罚': '监管部门发布行政处罚决定书，某公司因信息披露违规被处以罚款，并责令限期整改。',
 '许可': '监管部门作出准予行政许可的决定，同意该机构开展相关业务，许可事项与条件一并公示。',
 '备案': '该机构已完成产品备案，备案信息在监管平台公示，备案材料齐全有效。',
 '指引': '监管部门发布行业指引，明确业务操作规范与信息披露要求，供各机构参照执行。',
}

def init_prompts:
 """初始化前置 prompt，便于模型做 in-context learning。"""
 class_list = list(class_examples.keys())
 # ① system：定义角色 + 列出全部类别
 pre_history = [{"role": "system",
 "content": f"现在你是一个文本分类器，你需要按照要求将我给你的句子分类到：{class_list}类别中。"}]

 # ② 用"每个类别一条样例"构造 few-shot 对
 for _type, example in class_examples.items():
 pre_history.append({"role": "user",
 "content": f'"{example}"是 {class_list} 里的什么类别？'})
 pre_history.append({"role": "assistant", "content": _type})

 return {'class_list': class_list, 'pre_history': pre_history}

def inference(sentences: list, custom_settings: dict):
 """推理函数。"""
 for sentence in sentences:
 with console.status("[bold bright_green] Model Inference..."):
 # ③ 待推理输入的句式必须与示例完全一致（这是少样本能生效的前提）
 sentence_with_prompt = f""{sentence}"是 {custom_settings['class_list']} 里的什么类别？"
 response = ollama.chat(
 model='qwen2.5:7b',
 messages=[*custom_settings['pre_history'],
 {"role": 'user', "content": sentence_with_prompt}])
 response = response["message"]["content"]
 print(f'>>> [bold bright_red]sentence: {sentence}')
 print(f'>>> [bold bright_green]inference answer: {response}')
 print('*' * 80)
```

**这段代码里最容易被忽略、却最关键的一点**：待推理的句式

```text
f""{sentence}"是 {class_list} 里的什么类别？"
```

与示例里的句式**逐字一致**。

```text
示例 ： "监管部门发布行政处罚决定书…"是 [...] 里的什么类别？
待推理 ： "监管部门发布备案通知…"是 [...] 里的什么类别？
```

模型是靠"模式匹配"来续写的。如果示例是"是 [...] 里的什么类别？"而待推理写成"请判断以下文本属于哪一类："，模型可能就不知道该怎么接——它没在这个句式上被"演示"过。

**这是 Few-shot 的第一条铁律：示例的输入格式必须与真实输入格式严格一致。** 很多"我加了 few-shot 但没效果"的问题就出在这里。

**第二条铁律：示例的 `assistant` 输出必须只包含答案本身。** 这里 `"content": _type` 就是干净的类别名，没有"这句话属于处罚类"，因为……"。如果示例里带了推理过程，模型就会学着输出一堆解释，下游解析就麻烦了。（反过来说，如果任务**需要**推理过程——比如复杂的风险判断——那就应该在示例里带上解析，这是**Chain-of-Thought** 的用法。要不要带，取决于你要不要那个推理过程。）

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/03-文本分类系统/07-项目-监管公告分类与信息抽取.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「任务一：监管公告分类」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/03-文本分类系统/07-项目-监管公告分类与信息抽取.md)
