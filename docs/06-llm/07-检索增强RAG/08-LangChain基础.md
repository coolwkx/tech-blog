---
article_id: "1043063b962d"
learning_kind: "reference"
learning_category: "06-llm"
---

# -LangChain基础


> **一句话总结**：LangChain 的价值不是「自己造大模型」，而是为各种 LLM 提供**统一接口**，并用 Models / Prompts / Chains / Memory / Indexes / Agents 六大组件把「模型 + 提示 + 外部数据 + 工具」串成可维护的应用流水线。
> **前置知识**：大模型 API 与消息角色（见《05-大模型API与调用实践》）、embedding 与向量检索（见《07-向量数据库与Milvus》）。
> **学完能做到**：1. 说清六大组件的职责并各写出一段最小代码；2. 用「加载 → 分割 → 向量化 → 检索」搭出 RAG 的检索侧；3. 识别语料中的旧版 API 并知道新版对应写法。

## 1. 核心概念

### 1.1 LangChain 是什么

| 项 | 说明 |
|---|---|
| 创建者与时间 | Harrison Chase 创建于 2022 年 10 月 |
| 定位 | 围绕 LLM 建立的**应用开发框架** |
| 语言实现 | 目前有 **Python** 和 **Node.js** 两个版本 |
| 核心理念 | 自身**不开发 LLM**，而是为各种 LLM 实现**通用接口**，把相关组件「链接」起来，降低开发难度 |

一句话类比：**LangChain 之于 LLM，类似 JDBC 之于数据库**——屏蔽不同厂商差异，让上层应用用统一方式调用、编排与扩展。

### 1.2 六大组件总览

| 组件 | 职责 | 典型类 | 解决什么问题 |
|---|---|---|---|
| Models | 各类模型与集成的统一封装 | `Ollama`、`ChatOllama`、`OllamaEmbeddings` | 不同厂商 API 不一致 |
| Prompts | 提示管理、优化、序列化 | `PromptTemplate`、`FewShotPromptTemplate` | 提示是散落字符串、难复用 |
| Chains | 一系列组件调用的编排 | `LLMChain`、LCEL | 单次调用不够，需多步串联 |
| Memory | 保存与模型交互的上下文状态 | `ChatMessageHistory` | 大模型**本身不保存上次交互内容** |
| Indexes | 结构化文档以便与模型交互 | `TextLoader`、`TextSplitter`、`VectorStore`、`Retriever` | 模型不知道你的私有文档 |
| Agents | 决定采取哪些行动、执行并观察直到完成 | `AgentType`、`Tool`、`AgentExecutor` | 模型不会查实时信息、算数不可靠 |

### 1.3 三类模型的输入输出

| 模型类型 | 输入 | 输出 | 用途 |
|---|---|---|---|
| LLMs | 文本字符串 | 文本字符串 | 单轮生成 |
| Chat Models | 聊天消息列表 | 聊天消息对象 | 多轮对话（推荐） |
| Embeddings | 文本 | 浮点数列表（向量） | 向量化、检索 |

## 2. 关键机制

### 2.1 Models：三类模型的用法差异

**LLMs**：`invoke` 传字符串、返回字符串。

```python
from langchain_community.llms import Ollama
model = Ollama(model="qwen2.5:7b")
print(model.invoke("请给我讲个鬼故事"))
```

**Chat Models**：按约定传入**消息对象**，返回的也是消息对象（取 `.content`）。

| 消息类 | 作用 |
|---|---|
| `SystemMessage` | 设置模型的行为方式和目标，可接收任意形式的值 |
| `HumanMessage` | 发送给 LLM 的提示信息 |
| `AIMessage` | 保存 LLM 的响应，以便下次请求把这些信息传回给 LLM |

```python
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

model = ChatOllama(model="qwen2.5:7b")
res = model.invoke([SystemMessage(content="现在你是一个著名的诗人"),
HumanMessage(content="给我写一首唐诗")])
print(res.content)
```

**Embeddings**：注意 **建库与查询用不同方法，且必须用同一个模型**。

```python
from langchain_community.embeddings import OllamaEmbeddings
emb = OllamaEmbeddings(model="nomic-embed-text", temperature=0)
q = emb.embed_query("这是第一个测试文档") # 查询向量
docs = emb.embed_documents(["这是第一个测试文档", "这是第二个测试文档"]) # 批量建库
```

### 2.2 Prompts：把提示模板化

| 模板 | 关键参数 | 用途 |
|---|---|---|
| `PromptTemplate` | `template`、`input_variables` | zero-shot 场景，把提示参数化复用 |
| `FewShotPromptTemplate` | `examples`、`example_prompt`、`prefix`、`suffix`、`input_variables`、`example_separator` | few-shot 场景，让模型理解更复杂的业务 |

```python
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate

prompt = PromptTemplate(template="我的邻居姓{lastname}，他生了个儿子，给他儿子起个名字",
input_variables=["lastname"])

examples = [{"word": "开心", "antonym": "难过"}, {"word": "粗", "antonym": "细"}]
example_prompt = PromptTemplate(input_variables=["word", "antonym"],
template="单词:{word}\n反义词:{antonym}")
few_shot = FewShotPromptTemplate(examples=examples, example_prompt=example_prompt,
prefix="给出每个单词的反义词", suffix="单词:{input}\n反义词:",
input_variables=["input"], example_separator="\n")
print(few_shot.format(input="高"))
```

### 2.3 Chains：把组件串起来

**旧写法（语料，基于 2023 年版本）**：

```python
from langchain.chains import LLMChain
chain = LLMChain(llm=llm, prompt=prompt)
print(chain.run("王"))
```

**`SimpleSequentialChain`**：把**前一条链的输出**直接作为**后一条链的输入**。

```python
from langchain.chains import LLMChain, SimpleSequentialChain
first = LLMChain(llm=llm, prompt=PromptTemplate(
template="我的邻居姓{lastname}，他生了个儿子，给他儿子起个名字", input_variables=["lastname"]))
second = LLMChain(llm=llm, prompt=PromptTemplate(
template="邻居的儿子名字叫{child_name}，给他起一个小名", input_variables=["child_name"]))
overall = SimpleSequentialChain(chains=[first, second], verbose=True)
print(overall.run("王")) # 只需传入第一个链的参数
```

**为什么要链**：多步任务需要传递中间结果、对齐变量名、可观测执行过程。链把「拼字符串 → 调用 → 再拼」的胶水代码收敛成声明式结构。

**新旧 API 对照（重要）**——LangChain 0.1 之后主推 **LCEL**，用管道符 `|` 组合 `Runnable`：

| 旧写法（语料） | 新写法（LCEL） |
|---|---|
| `LLMChain(llm=llm, prompt=p)` + `chain.run(x)` | `p \| llm` + `chain.invoke({"变量": x})` |
| `SimpleSequentialChain(chains=[a, b])` | `a \| b` |
| `ConversationChain(llm=llm)` | `RunnableWithMessageHistory` + `InMemoryChatMessageHistory` |
| `retriever.get_relevant_documents(q)` | `retriever.invoke(q)` |
| `from langchain.llms import Ollama` | `from langchain_ollama import OllamaLLM` |
| `from langchain.chat_models import ChatOpenAI` | `from langchain_openai import ChatOpenAI` |

LCEL 等价写法：

```python
chain = first_prompt | llm | (lambda name: {"child_name": name.strip()}) | second_prompt | llm
print(chain.invoke({"lastname": "王"}))
```

### 2.4 Memory：大模型没有记忆，需要显式回传

**关键认知**：大模型本身**不具备上下文的概念**，不保存上次交互的内容；ChatGPT 能对话是因为它**把历史记录回传给了模型**。

| 类型 | 含义 |
|---|---|
| 短期记忆 | 单一会话内传递数据 |
| 长期记忆 | 处理多个会话时获取和更新信息 |

```python
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import messages_to_dict, messages_from_dict

history = ChatMessageHistory
history.add_user_message("在吗？")
history.add_ai_message("有什么事?")
dicts = messages_to_dict(history.messages) # 可落 Redis/MySQL/文件（长期记忆）
restored = messages_from_dict(dicts) # 读回后还原成消息对象
```

**记忆的工程代价**：全量回传会让 token 随轮次线性增长，因此必须做**窗口截断或摘要压缩**。

### 2.6 Agents：让模型调用外部工具

**为什么需要**：大模型虽然强大但有局限——**不能回答实时信息、处理数学逻辑问题仍非常初级**，
因此需要借助第三方工具（搜索引擎、数据库、计算器）辅助。

| 角色 | 职责 |
|---|---|
| `Agent` | 制定计划和思考下一步需要采取的行动 |
| `Tool` | 解决问题的工具 |
| `Toolkit` | 一些集成好的工具包 |
| `AgentExecutor` | 把代理和工具列表包装在一起，**迭代运行代理的循环，直到满足停止目标** |

```python
from langchain.agents import AgentType, initialize_agent, load_tools
tools = load_tools(["llm-math"], llm=llm) # "serpapi" 为实时联网搜索工具
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
print(agent.run("解以下方程：3x+4(x+2)=84，其中 x 为 3，请问 y 是多少？"))
```

常见内置工具：`python_repl`（执行 Python）、`GoogleSearch`/`BingSearch`、
`GoogleSerperAPI`（从 Google 搜索提取数据）、`llm-math`、`wikipedia`、`arxiv`、`requests_get/post`。
可用 `get_all_tool_names` 列出全部工具名。

**Agent 的本质**：把模型输出从**文本**变成**动作**（调用哪个工具、传什么参数），
再把工具的**观察结果**塞回上下文循环——这正是《11-AI-Agent开发》与 Function Calling 的雏形。

## 3. 可运行示例

### 3.1 最小 RAG 链（检索 + 生成）

```python
# 依赖：pip install langchain langchain-community langchain-text-splitters langchain-ollama chromadb
# 前置：ollama pull qwen2.5:7b && ollama pull nomic-embed-text
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

raw_text = """北京大学创办于1898年，初名京师大学堂，是中国近代第一所国立综合性大学。
1912年更名为北京大学。学校位于北京市海淀区。"""

splitter = RecursiveCharacterTextSplitter(chunk_size=60, chunk_overlap=10,
separators=["\n\n", "\n", "。", ""])
chunks = splitter.split_text(raw_text)

embeddings = OllamaEmbeddings(model="nomic-embed-text")
store = Chroma.from_texts(chunks, embeddings, persist_directory="./chroma_demo")
retriever = store.as_retriever(search_kwargs={"k": 2})

prompt = ChatPromptTemplate.from_messages([
("system", "只依据下面提供的回答问题；本主题提及的内容回答「未提及」。\n\n：\n{context}"),
("human", "{question}"),
])
llm = ChatOllama(model="qwen2.5:7b", temperature=0)

rag_chain = (
{"context": retriever | (lambda docs: "\n\n".join(d.page_content for d in docs)),
"question": RunnablePassthrough}
| prompt | llm | StrOutputParser
)

print(rag_chain.invoke("北京大学什么时候创办的？"))
print(rag_chain.invoke("北京大学的食堂几点开门？")) # 应回答「未提及」
```

| 环节 | 组件 | 关键点 |
|---|---|---|
| 分割 | `RecursiveCharacterTextSplitter` | `chunk_size` 与 `chunk_overlap` 决定检索与生成质量 |
| 向量化 | `OllamaEmbeddings` | 建库与查询必须用同一个模型 |
| 存储检索 | `Chroma` + `as_retriever` | `k` 控制召回条数 |
| 生成 | `ChatPromptTemplate` + `ChatOllama` | 明确约束「只依据作答」 |

### 3.2 带记忆的多轮对话（新版写法）

```python
# 依赖：pip install langchain-core langchain-ollama
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

prompt = ChatPromptTemplate.from_messages([
("system", "你是一个说话简洁的助手。"),
MessagesPlaceholder(variable_name="history"),
("human", "{input}"),
])
chain = prompt | ChatOllama(model="qwen2.5:7b", temperature=0)

_store = {}
def get_history(session_id: str):
    if session_id not in _store:
        _store[session_id] = InMemoryChatMessageHistory()
        return _store[session_id]

    chat = RunnableWithMessageHistory(chain, get_history,
    input_messages_key="input", history_messages_key="history")
    cfg = {"configurable": {"session_id": "user-1"}}
    print(chat.invoke({"input": "小明有1只猫"}, config=cfg).content)
    print(chat.invoke({"input": "小刚有2只狗"}, config=cfg).content)
    print(chat.invoke({"input": "他们一共有几只宠物？"}, config=cfg).content) # 能利用上文
```

`RunnableWithMessageHistory` 相当于把「取历史 → 拼 prompt → 调用 → 写回历史」显式化，
`session_id` 对应会话隔离，便于换成持久化后端——这就替代了旧的 `ConversationChain`。

## 4. 常见坑

| 坑 | 现象 | 原因 | 正确做法 |
|---|---|---|---|
| 导入旧路径失败 | `ModuleNotFoundError` | 语料基于 2023 年版本，0.1 后包被拆分 | 社区集成从 `langchain_community` 导入、核心类型从 `langchain_core` 导入；Ollama 用 `langchain_ollama` |

## 5. 面试问答

**Q1：LangChain 的六大组件分别解决什么问题？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

| 组件 | 解决的问题 |
|---|---|
| Models | 各家 LLM 接口不同 → 统一接口；分 LLMs（文本→文本）、Chat Models（消息列表→消息）、Embeddings（文本→向量） |
| Prompts | 提示是散落字符串、难复用 → `PromptTemplate` / `FewShotPromptTemplate` 模板化与参数化 |
| Chains | 单次调用不足以完成任务 → 把多个组件调用编排成流程，中间结果自动传递 |
| Memory | 大模型**不保存上次交互内容**（ChatGPT 是靠回传历史实现的）→ 在应用侧维护短期/长期记忆 |
| Indexes | 模型不知道私有文档 → 加载器 + 分割器 + 向量存储 + 检索器，把外部知识接入 |
| Agents | 模型不能回答实时信息、数学逻辑弱 → 调用搜索引擎/计算器/数据库等工具，循环执行直到完成 |

一句话：LangChain 自身不训练模型，价值在于**统一接口 + 编排能力 + 可替换的组件生态**。

</details>

**Q2：为什么大模型「需要」Memory 组件？实现长对话有哪些工程手段？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

根因是**大模型无状态**：每次请求都是独立的，模型不保存上次交互内容。
我们感知到的「ChatGPT 记得上文」，其实是应用层把历史消息重新拼进 prompt 再发给模型。

Memory 组件做三件事：保存历史、按需拼进 prompt、把新消息写回历史。

工程手段（成本递增）：
① **全量回传**——实现最简单，但 token 随轮次线性增长，很快超上下文且成本高；
② **窗口截断**——只保留最近 K 轮，简单有效，代价是丢失远期信息；
③ **摘要压缩**——把早期对话总结成短文，兼顾长度与信息；
④ **持久化 + 检索**——历史写 Redis/MySQL，需要时按相关性检索相关历史片段（长期记忆）。

LangChain 中对应 `InMemoryChatMessageHistory`、`messages_to_dict/messages_from_dict`（序列化落库）、
`RunnableWithMessageHistory`（按 `session_id` 隔离）。

</details>

**Q3：请描述一个完整 RAG 流程中 LangChain 各组件的分工。**

<details markdown="1">
<summary markdown="1">参考答案</summary>

| 阶段 | 组件 | 说明 |
|---|---|---|
| 加载 | `TextLoader` / `UnstructuredFileLoader` / `PDF` | 把 txt/pdf/md/html 转成 `Document` |
| 分割 | `RecursiveCharacterTextSplitter` / `MarkdownTextSplitter` | 按语义边界切块，保留 `chunk_overlap` |
| 向量化 | `OllamaEmbeddings` / `OpenAIEmbeddings` | `embed_documents` 得到向量 |
| 存储 | `Chroma` / `Milvus` / `FAISS` | 建索引，支持 `similarity_search` |
| 检索 | `VectorStoreRetriever` 等 | `invoke` 返回 Top-K 文档 |
| 组提示 | `ChatPromptTemplate` + `MessagesPlaceholder` | 把检索结果作为 `context` 注入 |
| 生成 | `ChatOllama` / `ChatOpenAI` | 依据生成，约束「未提及就说未提及」 |
| 编排 | LCEL `\|` 或 `Chain` | 串成「检索 → 格式化 → 提示 → 模型 → 解析」 |
| 记忆（可选） | `RunnableWithMessageHistory` | 支持多轮追问 |

关键工程点：建库与查询必须用**同一个 embedding 模型**；prompt 必须显式约束「只依据作答」，
否则模型会用参数知识覆盖检索结果，导致幻觉与引用不一致。

</details>

## 6. 自测题

**1. 三类模型（LLMs / Chat Models / Embeddings）的输入输出分别是什么？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

| 模型类型 | 输入 | 输出 |
|---|---|---|
| LLMs | 文本字符串 | 文本字符串 |
| Chat Models | 聊天消息列表（`SystemMessage`/`HumanMessage`/`AIMessage`） | 聊天消息对象（取 `.content`） |
| Embeddings | 文本（单条或列表） | 浮点数列表（向量） |

Embeddings 是检索系统的地基：`embed_query` 处理查询、`embed_documents` 处理建库，
两者必须用同一个模型。

</details>

**2. 文本分割为什么不能简单按固定字符数切？两个关键参数是什么？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

因为硬切会**破坏语义单元**——一段代码或一个函数被割裂到两段就失去意义，
检索到也无法提供有效信息。正确原则是**把语义相关的文本片段放在一起**，
所以应使用语义友好分隔符（`\n\n`、句号、Markdown 标题）。

两个关键参数：`chunk_size`（切片最大长度，影响检索精度与上下文长度）、
`chunk_overlap`（相邻切片重叠，避免答案落在边界导致两边都不完整，通常取 `chunk_size` 的 10%~20%）。

</details>

**3. Agent 的四个组成部分是什么？为什么需要 Agent？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

原因：大模型**不能回答实时信息、处理数学逻辑问题仍非常初级**，
需要让它能访问搜索引擎、数据库、计算器等外部工具。

四个部分：`Agent`（制定计划、思考下一步行动）、`Tool`（解决问题的工具）、
`Toolkit`（集成好的工具包）、`AgentExecutor`（包装代理与工具列表，
**迭代运行代理的循环直到满足停止目标**）。

示例：`load_tools(["llm-math"], llm=llm)` 加载数学工具，
再用 `initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)` 构造并 `run`。

</details>

**4. 语料里的 `LLMChain`、`ConversationChain` 在新版中对应什么？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

新版主推 **LCEL**，用管道符组合 `Runnable`：

| 旧写法 | 新写法 |
|---|---|
| `LLMChain(llm, prompt)` + `chain.run(x)` | `prompt \| llm` + `chain.invoke({...})` |
| `SimpleSequentialChain(chains=[a, b])` | `a \| b` |
| `ConversationChain(llm=llm)` | `RunnableWithMessageHistory` + `InMemoryChatMessageHistory` |
| `retriever.get_relevant_documents(q)` | `retriever.invoke(q)` |

学习建议：**理解组件职责与数据流**比记 API 更重要——职责稳定，API 随版本演进。

</details>

## 7. 延伸阅读

- [LangChain 官方文档](https://python.langchain.com/docs/introduction/)
- [LangChain GitHub](https://github.com/langchain-ai/langchain)
- [Ollama 官方文档](https://docs.ollama.com/)

---

[⬅️ 返回本目录索引](README.md)
