---
article_id: kp-4f1479c0e6be6b42
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-0dcba0cdfdde
learning_sourceId: 0dcba0cdfdde
learning_order: 9
learning_objective: 理解并验证：金融文本分类（few-shot + 严格输出词表）
---

# 金融文本分类（few-shot + 严格输出词表）

> **学习目标**：能够解释「金融文本分类（few-shot + 严格输出词表）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：大模型基本概念、In-context learning（见《01-大模型基础与演进》）、Python 字符串格式化与 JSON 解析。
>
> **所属主题**：-提示词工程 · 可运行示例

## 本次只学这一点

```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
LABELS = ["新闻报道", "公司公告", "财务公告", "分析师报告"]
SYSTEM = ("现在你是一个金融文本分类器，你需要按照要求将我给你的句子分类到："
f"{LABELS} 类别中。只输出一个类别名称。")

FEW_SHOT = [
("新闻报道", "今日，股市经历了一轮震荡，投资者密切关注政策调整。"),
("公司公告", "本公司宣布成功完成最新一轮并购交易。"),
("财务公告", "本公司年度财务报告显示，去年实现稳步增长的盈利。"),
("分析师报告", "最新的行业分析报告指出，科技公司的创新将成为未来增长的主要推动力。"),
]


def build_messages(sentence: str):
    msgs = [{"role": "system", "content": SYSTEM}]
    for label, example in FEW_SHOT: # 用「类别：样例」给出参考示例
        msgs.append({"role": "user", "content": f"<User>：{example}"})
        msgs.append({"role": "assistant", "content": label})
        msgs.append({"role": "user", "content": f"<User>：{sentence}"})
        return msgs


    def classify(sentence: str) -> str:
        resp = client.chat.completions.create(
        model="gpt-4o-mini", messages=build_messages(sentence),
        temperature=0, max_tokens=16,
        )
        label = resp.choices[0].message.content.strip()
        return label if label in LABELS else f"非法输出：{label!r}" # 必须校验


    for t in ["今日，央行发布公告宣布降低利率，以刺激经济增长。",
    "公司资产负债表显示，公司偿债能力强劲，现金流充足。"]:
        print(f"[{classify(t)}] {t[:24]}...")
```

**要点**：`temperature=0` 保证稳定；把类别放进系统提示形成**封闭词表**；
输出用 `label in LABELS` 做校验（模型偶尔会输出「类别：新闻报道」这类多余文字）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/06-提示工程/04-提示词工程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「金融文本分类（few-shot + 严格输出词表）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/06-提示工程/04-提示词工程.md)
