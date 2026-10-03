> **一句话总结**：LangChain 用六大组件（Models / Prompts / Memory / Indexes / Chains / Agents）为 LLM 应用提供统一接口，其中 **Agent = LLM 决策 + Tool 执行 + AgentExecutor 循环控制**；再往上，CrewAI 用 Agent / Task / Crew / Process / Tools 五件套把单个 Agent 扩展成多角色协作系统。
> **前置知识**：[02-Function-Calling与工具调用](../02-工具与规划/02-Function-Calling与工具调用.md) 的工具协议、[01-Agent基础范式与ReAct循环](../01-基础范式/01-Agent基础范式与ReAct循环.md) 的 ReAct 结构、[../llm/08-LangChain基础.md](../../06-llm/05-检索增强RAG/08-LangChain基础.md)。
> **学完能做到**：
> 1. 说清 Agent、AgentExecutor、Tool、Toolkit 四者的分工，并选用 `zero-shot-react-description` / `conversational-react-description` 等代理类型。
> 2. 用 `load_tools` + `initialize_agent` 跑通一个带数学计算工具的代理，并用 `@tool` 注册自己的工具。
> 3. 用 CrewAI 的 Agent / Task / Crew 定义一条顺序执行的多角色流水线（写稿 → 编辑 → 寄信）。

---

## 1. 核心概念

### 1.1 LangChain 是什么

LangChain 由 Harrison Chase 创建于 2022 年 10 月，是围绕 LLM 建立的一个框架。核心定位：

> LangChain 自身并不开发 LLM，它的核心理念是为各种 LLM 实现**通用的接口**，把 LLM 相关的组件「链接」在一起，简化 LLM 应用的开发难度。

| 项目 | 值 |
| --- | --- |
| 语言实现 | Python、Node.js |
| 官方文档 | https://python.langchain.com/ |
| 基础安装 | `pip install langchain langchain_community` |
| 本地模型配套 | `pip install ollama`（配合 Ollama 使用 `Ollama` / `ChatOllama` / `OllamaEmbeddings`） |

### 1.2 六大组件

| 组件 | 英文 | 职责 | 在 Agent 中的位置 |
| --- | --- | --- | --- |
| 模型 | Models | 各种类型的模型和模型集成 | 决策大脑 |
| 提示 | Prompts | 提示管理、提示优化和提示序列化 | 决定 Agent 的行为约束 |
| 记忆 | Memory | 保存和模型交互时的上下文状态 | 轨迹存储（详见 [05](05-Agent的记忆与知识管理.md)） |
| 索引 | Indexes | 结构化文档，以便和模型交互 | 知识获取（详见 [06](06-RAG作为Agent的知识获取手段.md)） |
| 链 | Chains | 一系列对各种组件的调用 | 确定性流程编排 |
| 代理 | Agents | 决定模型采取哪些行动，执行并观察流程，直到完成 | 自主流程编排 |

**Chains 与 Agents 的分工是本节的关键**：

| 维度 | Chains | Agents |
| --- | --- | --- |
| 下一步由谁决定 | 开发者（写死在代码里） | LLM（根据输入动态选择） |
| 可否使用工具 | 通常不 | 是 |
| 可控性 | 高，路径固定 | 较低，路径依赖模型输出 |
| 适用场景 | 流程稳定的场景（RAG 问答、字段抽取） | 需要多步试探、动态选工具的场景 |

### 1.3 三类模型的输入输出

| 类型 | 输入 | 输出 | 典型用法 |
| --- | --- | --- | --- |
| LLMs | 文本字符串 | 文本字符串 | 纯文本补全 |
| Chat Models | 聊天消息（`SystemMessage` / `HumanMessage` / `AIMessage` / `ChatMessage`） | 聊天消息 | 对话应用、Agent |
| Embeddings Models | 文本（单个字符串或字符串列表） | 浮点数列表（向量） | 文本向量化、检索 |

| 消息类型 | 说明 |
| --- | --- |
| `SystemMessage` | 指定模型所处的环境和背景，如「作为一个代码专家」或「返回 json 格式」 |
| `HumanMessage` | 用户发送给 LLM 的提示信息，如「实现一个快速排序方法」 |
| `AIMessage` | AI 输出的消息，可以是针对问题的回答 |
| `ChatMessage` | 可接受任意角色的参数；大多数时候应使用上面三种 |

### 1.4 Agents 组件里的四个概念

| 概念 | 英文 | 职责 |
| --- | --- | --- |
| 代理 | Agent | 制定计划和思考下一步需要采取的行动；暴露接口接收用户输入 |
| 工具 | Tool | 解决问题的具体能力，第三方服务集成（计算、搜索、代码执行等） |
| 工具包 | Toolkit | 一些集成好了的代理包，例如 `create_csv_agent` 可以直接解读 csv 文件 |
| 代理执行器 | AgentExecutor | 将代理和工具列表包装在一起，负责**迭代运行代理的循环**，直到满足停止的标准；返回 `AgentAction` 或 `AgentFinish` |

`initialize_agent(tools, llm, agent=..., verbose=True)` 返回的就是 `AgentExecutor` 实例，`agent.run(prompt)` 触发这个循环。

### 1.5 Agent 类型（AgentType）

点名了三种（LangChain 实际提供的类型更多）：

| 类型 | 工具选择依据 | 输入形态 | 适用场景 |
| --- | --- | --- | --- |
| `zero-shot-react-description` | 利用 ReAct 框架，**单纯依靠工具的描述信息**选择工具，可使用多个工具 | 单一字符串 | 通用、无历史的多工具任务 |
| `structured-chat-zero-shot-react-description` | 同上，但可通过工具的**参数 schema** 构造结构化的动作输入 | 结构化 | 参数复杂的工具调用 |
| `conversational-react-description` | ReAct + **记忆功能保存对话历史** | 对话 | 多轮对话中调用工具 |

三者的递进关系是：`zero-shot-react-description` 是基线；`structured-chat-*` 解决「参数怎么传」；`conversational-*` 解决「对话上下文怎么带」。

### 1.6 LangChain 内置工具一览

通过 `get_all_tool_names()` 打印出全部工具名，按用途归类如下：

| 类别 | 工具名 |
| --- | --- |
| 搜索 | `google-search`、`bing-search`、`ddg-search`、`metaphor-search`、`searx-search`、`serpapi`、`google-serper`、`google-scholar`、`searchapi`、`wikipedia`、`arxiv`、`pubmed` |
| 代码与终端 | `python_repl`、`terminal`、`bash`（部分版本）、`wolfram-alpha` |
| HTTP 请求 | `requests`、`requests_get`、`requests_post`、`requests_patch`、`requests_put`、`requests_delete` |
| 计算 | `llm-math` |
| 天气 / 地理 | `openweathermap-api`、`open-meteo-api` |
| 多媒体与业务 | `dalle-image-generator`、`eleven_labs_text2speech`、`google_cloud_texttospeech`、`news-api`、`tmdb-api`、`podcast-api`、`sceneXplain` |
| 基础设施与协作 | `awslambda`、`graphql`、`human`、`memorize`、`sleep`、`golden-query`、`twilio`、`dataforseo-api-search` |

使用 `load_tools(["serpapi", "llm-math"], llm=llm)` 加载；其中 `llm-math` 内部依赖 LLM 来解析算式，所以必须把 `llm` 一并传入。使用 serpapi 需要申请 token、设置环境变量 `SERPAPI_API_KEY` 并安装 `google-search-results`。

---

## 2. 关键机制

### 2.1 AgentExecutor 的循环

AgentExecutor 把「思考 → 选工具 → 执行 → 观察」做成一个受控循环：

```text
user input
 │
 ▼
┌─────────────────────────────────────────────┐
│ Agent（LLM + prompt + tool descriptions） │
│ 输出：AgentAction(tool=..., tool_input=...)│
│ 或 AgentFinish(return_values=...) │
└─────────────────────────────────────────────┘
 │ AgentAction │ AgentFinish
 ▼ ▼
执行工具 → 得到 Observation ──▶ 回到 Agent 结束，返回结果
```

两个关键约束：

1. **工具描述就是提示词的组成部分**。`zero-shot-react-description` 完全依赖 description 挑选工具，所以描述含糊必然选错。
2. **循环必须有停止标准**（AgentFinish 或迭代上限），否则会不停调工具。

### 2.2 Chain 的两种基本形态

| 形态 | 作用 | 示例 |
| --- | --- | --- |
| `LLMChain(llm=..., prompt=...)` | 把提示模板与模型绑定，`chain.run("王")` 直接执行 | 起名示例 |
| `SimpleSequentialChain(chains=[chain1, chain2], verbose=True)` | 把上一条链的输出直接作为下一条链的输入，只需传入第一个参数 | 起名 → 起小名 |

`SimpleSequentialChain` 的价值在于省掉了手工接线：`catchphrase = overall_chain.run("王")` 一句就能跑完整条流水线。

> **说明**：本小节超出本节范围，为通用知识补充。新版 LangChain 已用 LCEL（`prompt | model | parser`）取代 `LLMChain`，`SimpleSequentialChain` 也对应 `RunnableSequence`。概念上不变：链是「把组件按数据流串起来」，`|` 是更简洁的写法。

### 2.3 自定义工具：从 `llm-math` 到 `@tool`

内置工具覆盖不到业务逻辑时，需要注册自己的工具。在 CrewAI 项目中用 LangChain 的 `@tool` 装饰器实现（`custom_tools.py`）：

| 装饰器写法 | 注册出来的工具名 |
| --- | --- |
| `@tool("将文本写入文档中")` | `将文本写入文档中` |
| `@tool("发送文本到邮件")` | `发送文本到邮件` |

注意示例的一个细节：装饰器写在方法上时，`tools=[CustomTools.store_poesy_to_txt]` 这样按类属性引用，而不是 `CustomTools().store_poesy_to_txt`——因为 `@tool` 已经把函数对象转成了 BaseTool 实例。

### 2.4 多 Agent 编排：CrewAI 的五件套

第十章用 CrewAI 实现「自动写情书并发送邮件」。CrewAI 是一个**多角色 agent 框架**，为角色扮演中的 AI 代理提供自动化设置，通过促进代理之间的合作共同解决复杂问题。

| 组件 | 英文 | 职责（原文要点） |
| --- | --- | --- |
| 代理 | Agent | 每个 Agent 都有自己独特的个性、背景故事和技能 |
| 任务 | Task | 每个任务都有明确的目标和要求，并被分解成小而专注的子任务 |
| 执行容器 | Crew | 代理人、任务和过程相结合的容器层，是任务执行的实际场所 |
| 流程 | Process | 任务的分解、资源的分配、沟通协调 |
| 工具 | Tools | 根据特定情况和任务要求定制化代理工具 |

项目流水线：

```text
用户输入「帮我写一份情书」
 │
 ├─ 作家 Agent（role=作家，goal=创作情感丰富的文章，最长 300 词）──▶ 写情书 Task
 ├─ 内容编辑 Agent（tools=[store_poesy_to_txt]）──────────────▶ 编辑书信 Task（保存到磁盘）
 └─ 寄信人 Agent（tools=[send_message]）─────────────────────▶ 寄信 Task（发送邮件）
 process = Process.sequential
```

三个 Agent 的关键参数对比：

| Agent | role | goal | tools | allow_delegation |
| --- | --- | --- | --- | --- |
| poet | 作家 | 根据用户需求创作情感丰富的文章（最长 300 词） | 无 | False |
| letter_writer | 内容编辑 | 对作家撰写的文章内容进行精心编辑 | `store_poesy_to_txt` | False |
| sender | 寄信人 | 将编辑好的书信以邮件形式发送 | `send_message` | True |

`backstory` 字段用来给角色注入人设（如「你作为一名著名的作家，拥有千万级别的粉丝」），本质上是一段 system prompt。

### 2.5 Process：顺序执行与委派

| 概念 | 取值 | 含义 |
| --- | --- | --- |
| `Process.sequential` | 顺序 | 按 tasks 列表顺序执行，**上一个任务的结果会作为附加内容传递给下一个任务** |
| `allow_delegation` | True/False | 该 Agent 是否可以把子任务委派给其他 Agent |
| `verbose` | True / 1 / 2 | 是否打印执行过程（排查多 Agent 协作问题时必开） |

`crew.kickoff()` 启动整条流水线，返回值是最终结果。顺序流程的信息传递依赖 Task 的 `description` + 上一步输出，因此在 Task 描述里明确写「你最后的答案必须是……」这类输出契约非常重要——三个 Task 的 description 都写了输出要求。

---

## 3. 可运行示例

### 3.1 用 Agent 解方程（`agents_apply.py`）

**依赖**：`pip install langchain langchain-community ollama`；本地需先 `ollama pull qwen2.5:7b`。`llm-math` 工具还需要 `pip install numexpr`。

```python
"""LangChain Agent 示例：让代理自行选择数学工具解方程。

依赖：pip install langchain langchain-community ollama numexpr
前置：ollama pull qwen2.5:7b
"""

from langchain.agents import AgentType, initialize_agent
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_community.llms import Ollama

# 实例化大模型
llm = Ollama(model="qwen2.5:7b")

# 设置工具："serpapi" 实时联网搜索工具、"llm-math" 数学计算工具
tools = load_tools(["llm-math"], llm=llm)

# 实例化代理 Agent：返回 AgentExecutor 类型的实例
agent = initialize_agent(
 tools,
 llm,
 agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
 verbose=True,
 handle_parsing_errors=True, # 本地模型格式不稳定时的必备兜底
)

prompt_template = """解以下方程：3x + 4(x + 2) - 84 = y; 其中x为3，请问y是多少？"""

result = agent.run(prompt_template)
print("result-->", result)
```

`verbose=True` 会打印完整的 ReAct 轨迹（Thought / Action / Action Input / Observation），这是排查「代理为什么选了错的工具」的第一手材料。

### 3.2 自定义工具 + Agent（推荐写法）

**依赖**：`pip install langchain langchain-community`（`@tool` 来自 `langchain_core.tools`）。

```python
"""用 @tool 注册自定义工具，交给 Agent 编排。

依赖：pip install langchain langchain-community
"""

from langchain.agents import AgentType, initialize_agent
from langchain_community.llms import Ollama
from langchain_core.tools import tool

@tool("查询本地商品库存")
def query_stock(sku: str) -> str:
 """输入商品 SKU，返回当前库存数量。SKU 形如 'A1001'。"""
 fake_db = {"A1001": 12, "A1002": 0, "A1003": 47}
 if sku not in fake_db:
 return "未找到 SKU: %s" % sku
 return "SKU %s 当前库存 %d 件" % (sku, fake_db[sku])

@tool("按单价与数量计算总价")
def calc_total(price: float, quantity: int) -> str:
 """输入单价与数量，返回总价（保留两位小数）。"""
 return "总价：%.2f 元" % (price * quantity)

llm = Ollama(model="qwen2.5:7b")
tools = [query_stock, calc_total]

agent = initialize_agent(
 tools,
 llm,
 agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
 verbose=True,
 handle_parsing_errors=True,
)

if __name__ == "__main__":
 print(agent.run("A1003 还有多少库存？如果单价 19.9 元，全部买下要多少钱？"))
```

`@tool` 装饰器的第一个参数是**工具名**，函数 docstring 是**工具描述**——两者都会进入提示词，所以 docstring 要写清楚「输入是什么、返回什么、格式要求」。

### 3.3 用 CrewAI 编排三 Agent 流水线（Chapter 10 项目）

**依赖**：`pip install crewai langchain langchain-community openai python-dotenv`；环境变量 `OPENAI_API_KEY`（或通过 `base_url` 指向兼容端点）。

```python
"""CrewAI 多 Agent 编排：作家 → 编辑 → 寄信人。

依赖：pip install crewai langchain-community python-dotenv
环境变量：OPENAI_API_KEY
"""

import os

from crewai import Agent, Crew, Process, Task
from langchain_community.chat_models import ChatOpenAI
from langchain_core.tools import tool

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)

@tool("将文本写入文档中")
def store_poesy_to_txt(content: str) -> str:
 """将编辑后的书信文本内容自动保存到 txt 文档中，返回保存状态。"""
 filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "poie.txt")
 with open(filename, "w", encoding="utf-8") as file:
 file.write(content)
 return "File written to %s." % filename

@tool("发送文本到邮件")
def send_message() -> str:
 """读取本地书信文件，并以邮件的形式发送到指定的邮箱地址。

 为保证示例可运行，这里只打印动作而不真正发信；
 生产实现可参考 custom_tools.py 的 smtplib.SMTP_SSL 版本。
 """
 filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "poie.txt")
 if not os.path.exists(filename):
 return "错误：本地书信文件不存在，请先保存内容。"
 return "邮件已发送（示例模式）。"

poet = Agent(
 role="作家",
 goal="根据用户需求，创作出情感丰富的文章（最长字数不超过300个词）。",
 backstory="你作为一名著名的作家，拥有千万级别的粉丝，最擅长写情感类型的文章。",
 llm=llm,
 allow_delegation=False,
 verbose=True,
)

letter_writer = Agent(
 role="内容编辑",
 goal="对作家撰写的文章内容进行精心编辑。",
 backstory=(
 "作为一名经验丰富的编辑，你在编辑书信方面有多年的专业经验，"
 "你需要将作家写的文章内容整理编排成书信的样式，并将书信内容存储在本地磁盘上。"
 ),
 tools=[store_poesy_to_txt],
 llm=llm,
 allow_delegation=False,
 verbose=True,
)

sender = Agent(
 role="寄信人",
 goal="将编辑好的书信以邮件的形式发送给心仪的人",
 backstory="你是一名勤恳的信使，专注于将书信传递给每个人。",
 tools=[send_message],
 llm=llm,
 allow_delegation=True,
 verbose=True,
)

def build_crew(content):
 task1 = Task(
 description="用户需求:%s。你最后给出的答案必须是一份富含爱情表示的情书。" % content,
 agent=poet,
 )
 task2 = Task(
 description=(
 "查找任何语法错误，进行编辑和格式化（如果需要），并要求将内容保存在本地磁盘中。"
 "将内容保存到本地非常重要，你最后的答案必须是信息是否已被存储在本地磁盘中。"
 ),
 agent=letter_writer,
 )
 task3 = Task(
 description=(
 "根据本次磁盘保存的书信内容，你将整理并发送邮件给心仪的人，这个很重要。"
 "你最后的答案一定要成功发送该邮件。"
 ),
 agent=sender,
 )
 return Crew(
 agents=[poet, letter_writer, sender],
 tasks=[task1, task2, task3],
 process=Process.sequential, # 上一任务结果作为附加内容传给下一个任务
 verbose=2,
 )

if __name__ == "__main__":
 crew = build_crew("帮我写一份情书")
 result = crew.kickoff()
 print(result)
```

三点工程说明：

1. **工具失败要变成可读的返回文本**，而不是抛异常——`send_message` 里对文件不存在的处理就是范例；Agent 会把这段文本当作 Observation 继续推理。
2. **Task 的 description 承担输出契约**：三个 Task 都以「你最后的答案必须是……」结尾，这不是修辞，是在约束 AgentFinish 的内容。
3. 真实发信请使用 `custom_tools.py` 的 `smtplib.SMTP_SSL(smtp_srv.encode(), 465)` 写法，并且**凭证从环境变量读取**，不要写进源码。

---

## 4. 常见坑

| 现象 | 原因 | 解决 |
| --- | --- | --- |
| `ValueError: Could not parse LLM output` | 本地模型（如 qwen2.5:7b）没有严格遵循 ReAct 格式 | `initialize_agent(..., handle_parsing_errors=True)`；或换成指令遵循更好的模型 |
| Agent 不调用工具，直接瞎答 | 工具描述太笼统，或 `llm-math` 这类工具没传 `llm` | 写清工具名与 docstring；`load_tools([...], llm=llm)` 必须带 llm 参数 |
| `Agent stopped due to iteration limit` | 循环达到上限仍未给出 AgentFinish | 调大 `max_iterations` 的同时检查工具是否返回了有效信息 |
| `LLMChain` / `initialize_agent` 导入报弃用警告或失败 | 新版 LangChain 拆分到 `langchain_core` / `langchain_community`，`LLMChain` 逐步被 LCEL 取代 | 按新版导入路径调整：`langchain_core.prompts`、`langchain_community.agent_toolkits.load_tools`；或改用 LCEL |
| `@tool` 定义的方法无法作为工具传入 | 直接传了绑定方法 / 调用结果 | 传函数对象本身：`tools=[query_stock]`，不要写 `query_stock()` |
| CrewAI 里后续 Task 拿不到上一步内容 | 顺序流程依赖 `Process.sequential` 与任务顺序 | 设 `process=Process.sequential` 并保证 tasks 列表顺序与依赖一致 |
| Agent 之间互相委派导致踢皮球 | 多个 Agent 同时 `allow_delegation=True` | 只给确实需要转派的 Agent 打开委派 |
| 工具在写文件/发信时用相对路径，结果写到别处 | CrewAI / LangChain 运行目录不确定 | 用 `os.path.dirname(os.path.abspath(__file__))` 拼绝对路径 |

---

## 5. 面试问答

<details><summary>参考答案</summary>

**Q1：LangChain 里 Chain 和 Agent 的本质区别是什么？什么时候该用哪个？**

区别在于「下一步做什么由谁决定」。Chain 的调用顺序由开发者写死在代码里，数据流是确定的，因此可预测、易测试、成本可控；Agent 把下一步的决策权交给 LLM，由模型根据当前上下文输出 `AgentAction`（选哪个工具、传什么参数）或 `AgentFinish`，AgentExecutor 负责把工具执行结果作为 Observation 回填并再次调用模型，直到模型宣布结束。选型上：流程稳定、路径唯一的任务（字段抽取、RAG 问答、固定格式转换）用 Chain；需要多步试探、动态选工具、失败后自行换路线的任务用 Agent。实践中常见做法是「外层 Agent 做路由 + 内层 Chain 做确定性处理」，兼顾灵活性与可控性。

</details>

<details><summary>参考答案</summary>

**Q2：AgentExecutor 在循环里扮演什么角色？它如何避免死循环？**

AgentExecutor 是把 Agent（决策器）与工具列表（执行器）包装起来的驱动器，负责迭代运行代理循环，并把每一步的 Observation 回填到下一次调用中；它还负责把 Agent 的输出解析成 `AgentAction` 或 `AgentFinish` 两种类型，前者触发工具执行，后者终止循环并返回结果。防止死循环的手段主要有：最大迭代次数（`max_iterations`）、解析失败时的错误处理策略（`handle_parsing_errors`，把解析失败信息回灌给模型让它自我纠正）、以及 `early_stopping_method`。此外工程上还应加上整体超时和重复动作检测，因为模型可能在参数微变的情况下反复调用同一个工具。

</details>

<details><summary>参考答案</summary>

**Q3：多 Agent 协作（CrewAI）相比单 Agent 加了哪些东西？代价是什么？**

加的是一层「角色化的任务分解」：CrewAI 用 Agent（个性、背景故事、技能）、Task（明确目标、可分解为子任务）、Crew（Agent + Task + Process 的容器）、Process（任务分解、资源分配、沟通协调）、Tools（定制化工具）五个组件把一个大目标拆给多个角色。收益是每个 Agent 的 system prompt 更聚焦、工具集更小，从而降低单 Agent 面对大工具集时的选择错误率，也便于并行与专业化。代价主要有四：token 成本与延迟随对话轮数放大；错误会沿链路传播（上游写错、下游照做）；调试需要开 `verbose` 看完整对话流；不同 Agent 的上下文不天然共享，靠 Task 描述显式传递，容易丢信息。

</details>

---

## 6. 自测题

<details><summary>参考答案</summary>

**1. `zero-shot-react-description`、`structured-chat-zero-shot-react-description`、`conversational-react-description` 三者的区别是什么？**

都基于 ReAct 框架选择工具。第一个只用单一字符串输入、单纯依靠工具的描述信息选工具；第二个通过工具的参数 schema 构造结构化的动作输入，适合参数复杂的场景；第三个专为对话场景设计，使用对话性提示词，并用记忆功能保存对话历史，因此适合多轮会话中调用工具。

</details>

<details><summary>参考答案</summary>

**2. CrewAI 的五个核心组件各是什么？`Process.sequential` 的含义？**

Agent（代理，有独特个性、背景故事和技能）、Task（任务，有明确目标并分解为小而专注的子任务）、Crew（执行者，代理人/任务/过程相结合的容器层）、Process（流程，负责任务分解、资源分配与沟通协调）、Tools（工具，按特定情况和任务定制）。`Process.sequential` 表示按顺序执行任务，**上一个任务的结果会作为附加内容传递给下一个任务**。

</details>

<details><summary>参考答案</summary>

**3. 为什么 `load_tools(["llm-math"], llm=llm)` 必须传 `llm`？**

因为 `llm-math` 不是纯计算器：它内部需要借助一个 LLM 来理解并解析自然语言形式的算式，再交给 `numexpr` 求值。不传 `llm` 时工具无法初始化，会直接报错。

</details>

<details><summary>参考答案</summary>

**4. 自定义工具时，工具名和工具描述分别来自哪里？为什么要写规范？**

使用 `@tool` 装饰器时，装饰器的参数（如 `@tool("发送文本到邮件")`）是工具名，函数 docstring 是工具描述；不使用装饰器时则由 `Tool(name=..., description=..., func=...)` 显式指定。它们会直接进入 Agent 的提示词，是模型选择工具与填写参数的唯一依据，所以必须写清「能做什么、输入什么格式、返回什么、什么时候不该用」。

</details>

<details><summary>参考答案</summary>

**5. 同一个 `SimpleSequentialChain` 中，第二条链为什么只需要声明自己的输入变量？**

因为 `SimpleSequentialChain` 约定把前一条链的输出直接作为后一条链的输入，接线由框架完成。所以执行时只需传入第一条链的参数（`overall_chain.run("王")`），第二条链的 `input_variables`（如 `child_name`）由前一步的输出自动填充，不需要调用方提供。

</details>

---

## 7. 延伸阅读

- LangChain 官方文档 —— https://python.langchain.com/
- LangChain Agents 使用指南 —— https://python.langchain.com/docs/how_to/#agents
- LangChain 内置工具清单 —— https://python.langchain.com/docs/integrations/tools/
- Crafting a custom tool（`@tool` 用法） —— https://python.langchain.com/docs/how_to/custom_tools/
- CrewAI 官方文档 —— https://docs.crewai.com/
- ：《第五章：物流问答系统（RAG）_01-LangChain 基础知识入门》《第十章：AI Agents 开发应用》

---

[⬅️ 返回本目录索引](README.md)
