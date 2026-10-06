---
article_id: kp-16b8a8bb99279641
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-90fdb3fa96e7
learning_sourceId: 90fdb3fa96e7
learning_order: 9
learning_objective: 理解并验证：四种调用方式（同一个问题）
---

# 四种调用方式（同一个问题）

> **学习目标**：能够解释「四种调用方式（同一个问题）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：命令行基础、环境变量概念、HTTP/REST 基础、Python 与虚拟环境。
>
> **所属主题**：-本地部署与Ollama · 可运行示例

## 本次只学这一点

```python
# ========== 方式 1：官方 ollama 库（最简）==========
# 依赖：pip install ollama
import ollama

response = ollama.chat(
 model="qwen2:1.5b",
 messages=[{"role": "user", "content": "为什么天空是蓝色的？"}],
)
print(response["message"]["content"])

# 生成式（非对话）接口：
# response = ollama.generate(model="qwen2:1.5b", prompt="为什么天空是蓝色的？")

# ========== 方式 2：Client 指定主机（可远程调用）==========
from ollama import Client

client = Client(host="http://127.0.0.1:11434") # 远程示例：http://192.168.1.100:11434
resp = client.chat(model="qwen2:1.5b", messages=[
 {"role": "user", "content": "为什么天空是蓝色的？"},
])
print(resp["message"]["content"])

# ========== 方式 3：流式输出（生成器）==========
stream = ollama.chat(
 model="qwen2:1.5b",
 messages=[{"role": "user", "content": "为什么天空是蓝色的？"}],
 stream=True,
)
for chunk in stream:
 print(chunk["message"]["content"], end="", flush=True)
print
```

```python
# ========== 方式 4：requests 直连 REST ==========
# 依赖：pip install requests
import requests

host, port = "127.0.0.1", "11434"
url = f"http://{host}:{port}/api/chat"
data = {
"model": "qwen2:1.5b", # 模型选择
"options": {
"temperature": 0.0, # 0 表示不让模型自由发挥，输出相对固定
"num_ctx": 4096,
},
"stream": False, # 流式输出开关
"messages": [ # 对话列表
{"role": "system", "content": "你是一个简洁的科普助手。"},
{"role": "user", "content": "为什么天空是蓝色的？"},
],
}
response = requests.post(url, json=data, headers={"Content-Type": "application/json"}, timeout=60)
response.raise_for_status
print(response.json["message"]["content"])
```

```python
# ========== 方式 5：LangChain 集成 ==========
# 依赖：pip install langchain langchain_community
# 注意：新版 LangChain 推荐 from langchain_ollama import OllamaLLM
from langchain_community.llms import Ollama

host, port = "127.0.0.1", "11434" # 默认端口 11434
# 如果本地系统已有 ollama 服务，可以省略 base_url
llm = Ollama(base_url=f"http://{host}:{port}", model="qwen2:1.5b", temperature=0)
print(llm.invoke("你是谁"))
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/05-推理与部署/06-本地部署与Ollama.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「四种调用方式（同一个问题）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/05-推理与部署/06-本地部署与Ollama.md)
