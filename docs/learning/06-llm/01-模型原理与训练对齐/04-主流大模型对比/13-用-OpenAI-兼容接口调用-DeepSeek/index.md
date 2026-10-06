---
article_id: kp-c1fb6f47dff20aa8
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-eeaa40388b15
learning_sourceId: eeaa40388b15
learning_order: 12
learning_objective: 理解并验证：用 OpenAI 兼容接口调用 DeepSeek
---

# 用 OpenAI 兼容接口调用 DeepSeek

> **学习目标**：能够解释「用 OpenAI 兼容接口调用 DeepSeek」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer 与注意力机制（见《02-Transformer与注意力机制》）、模型参数量与显存的基本换算、量化概念。
>
> **所属主题**：-主流大模型对比 · 可运行示例

## 本次只学这一点

```python
# 依赖：pip install openai>=1.0
# 环境变量：export DEEPSEEK_API_KEY=sk-xxx（DeepSeek 开放平台申请）
import os
from openai import OpenAI

client = OpenAI(
api_key=os.environ["DEEPSEEK_API_KEY"],
base_url="https://api.deepseek.com", # OpenAI 兼容端点
)

resp = client.chat.completions.create(
model="deepseek-chat", # deepseek-chat=通用对话；deepseek-reasoner=推理模型
messages=[
{"role": "system", "content": "你是一位严谨的技术助教，回答控制在三句话内。"},
{"role": "user", "content": "为什么大模型大多采用 decoder-only 架构？"},
],
temperature=0.3,
top_p=0.9,
max_tokens=512,
stream=False,
)

print(resp.choices[0].message.content)
print("--- token 用量 ---")
print(resp.usage) # prompt_tokens / completion_tokens / total_tokens
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/03-主流大模型对比.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「用 OpenAI 兼容接口调用 DeepSeek」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/03-主流大模型对比.md)
