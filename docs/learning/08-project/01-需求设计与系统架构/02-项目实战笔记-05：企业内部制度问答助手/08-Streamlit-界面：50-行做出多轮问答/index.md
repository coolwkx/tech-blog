---
article_id: kp-c668ff56db82e95d
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-bbd88f00e6f8
learning_sourceId: bbd88f00e6f8
learning_order: 8
learning_objective: 理解并验证：Streamlit 界面：50 行做出多轮问答
---

# Streamlit 界面：50 行做出多轮问答

> **学习目标**：能够解释「Streamlit 界面：50 行做出多轮问答」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 基础、向量检索的基本概念（Embedding / 相似度 / Top-K）、`pip` 环境管理、Streamlit 的最简用法。
>
> **所属主题**：项目实战笔记 05：企业内部制度问答助手 · 核心实现

## 本次只学这一点

```text
# web_qa.py
from local_qa import *
from langchain.chains import ConversationalRetrievalChain
import streamlit as st

st.set_page_config(page_title="企业内部制度问答助手", layout="wide")
st.title("企业内部制度问答助手")

chat_history = [] # 传给 Chain 的 (question, answer) 列表

def new_retrival:
 """创建带历史感知的问答链"""
 chain = ConversationalRetrievalChain.from_llm(
 llm=Ollama(model="qwen2.5:7b"),
 retriever=db.as_retriever,
 )
 return chain

def main:
 # ① 会话状态保存聊天记录（用于界面展示）
 if "messages" not in st.session_state:
 st.session_state.messages = []

 # ② 回放历史消息
 for message in st.session_state.messages:
 with st.chat_message(message["role"]):
 st.markdown(message["content"])

 # ③ 接收输入
 if prompt := st.chat_input("请输入你的问题:"):
 st.session_state.messages.append({"role": "user", "content": prompt})
 with st.chat_message("user"):
 st.markdown(prompt)

 # ④ 生成回答
 with st.chat_message("assistant"):
 message_placeholder = st.empty
 full_response = ""

 chain = new_retrival
 result = chain.invoke({"question": prompt, "chat_history": chat_history})
 chat_history.append((prompt, result["answer"]))
 assistant_response = result["answer"]

 # ⑤ 模拟流式输出：逐词追加显示
 for chunk in assistant_response.split():
 full_response += chunk + ""
 message_placeholder.markdown(full_response + "▌")
 message_placeholder.markdown(full_response)

 st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
 main
```

**两个 `history` 的区别，容易混**：

| 变量 | 类型 | 用途 |
| --- | --- | --- |
| `st.session_state.messages` | `[{role, content}]` | 给**界面**回放聊天记录用 |
| `chat_history` | `[(question, answer)]` | 给 **Chain** 做 question condensation 用 |

它们内容重叠但格式不同，不能合并。而且 `chat_history` 是模块级变量，**在多用户场景下会串号**——Streamlit 每个会话有独立的脚本执行上下文，但模块级变量在多会话下未必隔离（取决于运行方式）。正确做法是把 `chat_history` 也放进 `st.session_state`。这是一个很典型的"demo 能跑，多人用就串"的坑。

**关于"模拟流式"**：这段代码是先把完整答案拿到，再按空格切分逐词渲染，加一个 `▌` 光标制造打字机效果。**这不是真流式**——用户看到第一个字的延迟和看到最后一个字的延迟差不多（只是视觉上分散了）。真流式要用 `chain.stream` 或 `llm.stream`，配合 `st.write_stream`。这个区别在面试里常被追问"你的流式是真流式吗"，要能分清楚。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/01-问答与RAG系统/05-项目-企业内部制度问答助手.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Streamlit 界面：50 行做出多轮问答」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/01-问答与RAG系统/05-项目-企业内部制度问答助手.md)
