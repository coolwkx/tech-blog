> **一句话总结**：AI Agent = **LLM + 记忆 + 任务规划 + 工具使用**，它把软件架构从「面向过程」推向「面向目标」——不再由工程师把流程写死，而是由模型自己拆解目标、调用工具、观察结果并迭代，直到任务完成。
> **前置知识**：LLM 调用与提示工程（见《04-提示词工程》）、LangChain 组件与工具（见《08-LangChain基础》）、Python 函数与异常处理。
> **学完能做到**：1. 说清 Agent 的五大环节与三类 Agent 的区别；2. 用 CrewAI 搭出「多角色协作」的 Agent 应用；3. 实现自定义工具（写文件、发邮件）并交给 Agent 调用。

## 1. 核心概念

### 1.1 什么是 AI Agent

**AI Agent（Artificial Intelligence Agent）**：一种能够**感知环境、进行决策和执行动作**的智能实体。
它可以是物理实体（如机器人），也可以是虚拟实体（如软件程序）。

**与传统人工智能的关键区别**：Agent 具备通过**独立思考、调用工具**去逐步完成给定目标的能力。

**当下语境下的 AI Agent**：本质是一个**控制 LLM 来解决问题的代理系统**。

一个直观的例子——AutoGPT：只需为它提供一个 AI 名称、描述和五个目标，它就能自己完成项目。
例如「基于新浪娱乐电影网站的最新报道信息，抽取所有电影标题，并将标题保存到本地文档中」，
AutoGPT 会自主完成「访问网页 → 抽取标题 → 写文件」的全过程。

### 1.2 Agent 的构成公式

$$\text{AI Agent} = \text{LLM} + \text{记忆} + \text{任务规划} + \text{工具使用}$$

拆开看四块能力：

| 能力 | 说明 | 典型实现 |
|---|---|---|
| 记忆（Memory） | 保留当前用户输入内容、上下文信息、外部向量存储的知识库 | 对话历史、向量库 |
| 任务规划（Planning） | 对任务分解、思考执行、返回结果 | 子目标分解、反思与完善 |
| 工具使用（Tools） | 计算器、搜索、代码解释器、API | `load_tools`、自定义工具 |
| 行动（Action） | 执行具体操作 | 检索、推理、编程 |

### 1.3 Agent 的五大工作环节

| 环节 | 角色定位 | 说明 |
|---|---|---|
| ① Prompt 提示词 | Agent 接收的初始输入 | 描述角色范围、任务背景 |
| ② LLM 大模型 | Agent 进行任务规划和知识推理的重要工具 | 理解、识别、选择 |
| ③ Memory 记忆 | 保留当前用户输入内容、上下文信息、外部向量存储的知识库 | 支撑多轮与长期状态 |
| ④ Planning 规划 | 对任务的拆解、思考执行、返回 | 涉及任务分解、目标设定、搜索、路径规划 |
| ⑤ Action 行动 | 执行具体操作的过程 | 包含工具：计算器、代码解释器、API 等 |

### 1.6 AI Agent 与传统软件的区别

| 对比维度 | 传统软件 | AI Agent |
|---|---|---|
| 可解任务范围 | 只能解决**有限范围**的任务 | 可以解决**无限域**的任务 |
| 核心要素 | 软件工程师 | Agent |
| 机制 | 通过一系列**预定义的指令、逻辑、规则和启发式算法**将流程固定下来，以满足软件运行结果符合用户预期（用户按指令逻辑一步步操作达成目标） | 将原本由人类主导的功能开发**逐渐迁移为以 AI 为主要驱动力**；以大模型为技术基础设施，Agent 为核心产品形态，变成**目标导向的智能体自主生成** |
| 生产方式 | 人类为中心，AI 辅助 | AI 为中心，人类为辅助 |

**一句话总结这个范式迁移**：**AI Agent 将使软件架构的范式从「面向过程」迁移到「面向目标」。**

## 2. 关键机制

### 2.1 用一个例子理解 Agent 的运行机制

以「AI Agent 处理客户的退货请求」为例：

| 环节 | Agent 的动作 |
|---|---|
| 输入（Prompt） | 用户说「我想退货订单 #12345 的商品，因为有缺陷」 |
| LLM 理解 | 大语言模型解析请求，确定客户想退货，并识别出订单号和退货原因 |
| Memory 检索 | 检索订单 #12345 的信息，核对商品是否符合退货条件 |
| Planning 规划 | 生成退货标签，再通知仓库处理退货，最后反馈给客户 |
| Action 执行 | 按计划执行各项任务，处理客户的退货请求，并检查库存状态 |

**这个例子把「Agent 与传统软件」的差别讲透了**：传统软件需要事先写好「退货流程」的每一步分支；
Agent 只需要给目标（「处理这个退货请求并让客户满意」）和工具（查订单、生成标签、通知仓库、发消息），
由模型自己决定调用顺序与参数。

### 2.2 五环节的职责边界

理解这五个环节的分工，是设计 Agent 的关键——**不同环节出问题，修的位置完全不同**。

| 环节 | 负责什么 | 出问题的表现 | 修哪里 |
|---|---|---|---|
| Prompt | 角色、目标、边界、可用工具说明 | Agent 做无关的事、乱用工具 | 改 Prompt（角色/目标/约束） |
| LLM | 理解与决策 | 理解错任务、选错工具 | 换更强模型、降低 temperature、把工具描述写清楚 |
| Memory | 上下文与历史 | 忘记前文、重复问同样的问题 | 补记忆管理（窗口/摘要/向量库） |
| Planning | 任务分解与顺序 | 步骤混乱、漏步骤、死循环 | 明确 Process（如 `Process.sequential`）、拆细 Task |
| Action | 真正调用工具 | 工具调用失败、参数错 | 检查工具函数签名与错误处理、加超时 |

### 2.5 CrewAI：多角色 Agent 框架

**CrewAI** 是一个创新的**多角色 agent 框架**，专为角色扮演中的 AI 代理提供自动化设置。
它通过促进 AI 代理之间的合作，使这些代理能够共同解决复杂问题。

| 核心组件 | 职责 |
|---|---|
| **Agent（代理）** | 每个 Agent 都有自己独特的**个性、背景故事和技能**，专注的子任务 |
| **Task（任务）** | 每个任务都具有明确的目标和要求，并被分解成小的专注子任务 |
| **Tools（工具）** | 根据特定情况和任务要求定制化代理工具，以更好满足需求 |
| **Process（流程）** | 包括任务的分解、资源的分配、沟通协调 |
| **Crew（执行者）** | CrewAI 中代理人、任务和过程相结合的容器层，是任务**执行的实际场所** |

**Agent 的三个关键属性**（从代码可见）：

| 属性 | 作用 |
|---|---|
| `role` | 角色名（如「作家」「内容编辑」「寄信人」） |
| `goal` | 该角色要达成的目标，直接决定它的行为方向 |
| `backstory` | 背景故事，为角色提供「人设」与能力假设，显著影响输出风格与专业性 |

另有两个常用开关：`allow_delegation`（是否允许把任务委派给其他 Agent）、`verbose`（是否打印执行过程）。

**Process 的两种常见模式**：`Process.sequential`（按顺序执行，**上一个任务的结果作为附加内容传递给下一个任务**）
与层级式（由 manager 协调）。的写信项目使用 `Process.sequential`。

## 3. 可运行示例

### 3.1 依赖与项目结构

```bash
# 依赖：pip install openai langchain langchain-community crewai python-dotenv
# 需要 Python 3.10 - 3.11
# 环境变量（.env 文件）：
# OPENAI_API_KEY=sk-xxx
# OPENAI_BASE_URI=https://api.openai.com/v1 # 用国产模型时改这里
```

```text
Email_Generate/
├── main.py # 设计 AI Agent 与对应任务，完成主体功能
├── tools/
│ └── custom_tools.py # 自定义 Tools，供 Agent 使用
└── poie.txt # 生成的书信落盘位置
```

### 3.2 自定义工具：写文件 + 发邮件

```text
import os
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

from langchain.tools import tool


class CustomTools:
 """两个工具：把文本写到本地文档、把文档内容以邮件发出。"""

 @tool("将文本写入文档中")
 def store_poesy_to_txt(content: str) -> str:
 """将编辑后的书信文本内容自动保存到 txt 文档中"""
 filename = "./Email_Generate/poie.txt"
 try:
 with open(filename, "w", encoding="utf-8") as file:
 file.write(content)
 return f"文件已写入 {filename}。"
 except Exception:
 return "写入文件时出错。"

 @tool("发送文本到邮件")
 def send_message(self) -> str:
 """读取本地书信文件并以邮件发送（QQ 邮箱 SMTP：smtp.qq.com）"""
 smtp_srv = os.environ.get("SMTP_SERVER", "smtp.qq.com")
 from_addr = os.environ["SMTP_FROM_ADDR"]
 from_pwd = os.environ["SMTP_AUTH_CODE"] # 授权码，不是登录密码
 to_addr = os.environ["SMTP_TO_ADDR"]
 filename = "./Email_Generate/poie.txt"
 with open(filename, encoding="utf-8") as f:
 my_msg = f.read()
 msg = MIMEText(my_msg, "plain", "utf-8")
 msg["From"] = formataddr(["小可爱", from_addr])
 msg["Subject"] = "520 小情书"
 srv = smtplib.SMTP_SSL(smtp_srv.encode(), 465) # SSL 直连用 465
 try:
 srv.login(from_addr, from_pwd)
 srv.sendmail(from_addr, [to_addr], msg.as_string())
 return "信件已发送"
 finally:
 srv.quit()
```

**三个要点**：
① `@tool("描述")` 装饰器把普通函数变成 Agent 可调用的工具，**描述文本会进入 Prompt**，
因此要写成「做什么」而不是「怎么实现」；
② QQ 邮箱必须用**授权码**而不是登录密码；
③ 认证信息放环境变量——示例里出现了明文邮箱与授权码，这是必须修正的反面做法。

```python
# main.py —— 依赖：pip install crewai langchain-community python-dotenv
import os
from dotenv import load_dotenv, find_dotenv
from langchain_community.chat_models import ChatOpenAI
from crewai import Agent, Task, Crew, Process
from tools.custom_tools import CustomTools

load_dotenv(find_dotenv())
client = ChatOpenAI(model_name="gpt-3.5-turbo", base_url=os.environ["OPENAI_BASE_URI"])

# 1) 三个角色：各自的 role / goal / backstory 决定行为与风格
poet = Agent(role="作家", goal="根据用户需求创作情感丰富的文章（不超过 300 词）。",
backstory="你作为著名作家，拥有千万级粉丝，最擅长写情感类文章。",
llm=client, allow_delegation=False, verbose=True)
letter_writer = Agent(role="内容编辑", goal="对作家撰写的文章内容进行精心编辑。",
backstory="作为经验丰富的编辑，你在编辑书信方面有多年专业经验。",
llm=client, tools=[CustomTools.store_poesy_to_txt],
allow_delegation=False, verbose=True)
sender = Agent(role="寄信人", goal="将编辑好的书信以邮件的形式发送给心仪的人",
backstory="你是一名勤恳的信使，专注于将书信传递给每个人。",
llm=client, tools=[CustomTools.send_message],
allow_delegation=True, verbose=True)

# 2) 任务：描述里写死「完成判据」，避免 Agent 自称完成却未调用工具
content = "帮我写一份情书"
task1 = Task(description=f"用户需求:{content}。你最后给出的答案必须是一份富含爱情表示的情书。",
agent=poet)
task2 = Task(description="查找任何语法错误，进行编辑和格式化。并要求将内容保存在本地磁盘中。你最后的答案必须是信息是否已被存储在本地磁盘中。", agent=letter_writer)
task3 = Task(description="根据本次磁盘保存的书信内容，整理并发送邮件给心仪的人。你最后的答案一定要成功发送该邮件。", agent=sender)

# 3) 组队并按顺序执行：上一任务的结果作为附加内容传给下一任务
crew = Crew(agents=[poet, letter_writer, sender], tasks=[task1, task2, task3],
process=Process.sequential, verbose=2)
print(crew.kickoff())
```

## 4. 常见坑

| 坑 | 现象 | 原因 | 正确做法 |
|---|---|---|---|
| 工具描述写得像实现说明 | Agent 不调用或错用工具 | 工具描述会进入 Prompt，是模型选择工具的唯一依据 | 用「做什么」的自然语言描述，并写清参数含义 |
| 任务描述没有完成判据 | Agent 说「已完成」但没真正调用工具 | 缺少明确的终止条件 | 在 `description` 中写死验收标准（如「最后答案必须是文件已保存/邮件已发送」） |
| 给所有 Agent 都开放全部工具 | 误用工具、越权操作 | 工具集过大 | 按角色最小化分配工具，只给完成任务必需的 |
| SMTP 用登录密码 | 登录失败（QQ 邮箱） | 邮箱服务要求用**授权码** | 在邮箱设置里生成授权码，并放入环境变量 |
| 邮箱与授权码硬编码在代码里 | 凭据泄露 | 图省事写死在源码 | 用 `.env` + `os.environ`，并把 `.env` 加入 `.gitignore` |
| 发完邮件不断开连接 | 连接泄漏、偶发发送失败 | 异常路径未执行 `quit` | 用 `try/finally` 保证 `srv.quit` |
| 使用 `smtplib.SMTP_SSL` 端口写 25/587 | 连接报错 | SSL 直连通常用 465 | `SMTP_SSL(host, 465)`；若用 STARTTLS 则走 `SMTP` + `starttls` |
| Agent 陷入死循环 | 反复调用工具、迟迟不结束 | 目标模糊、工具返回无信息量 | 明确任务边界、让工具返回明确结果字符串、限制最大迭代次数 |
| 多 Agent 顺序错乱 | 编辑在写作之前执行 | 未指定或误用 `Process` | 用 `Process.sequential` 保证顺序，任务列表顺序即执行顺序 |
| 只在一个 Agent 上设置 `llm` | 报错找不到模型 | 每个 Agent 都需要可用的 LLM 实例 | 统一把 `llm=client` 传给所有 Agent |
| 忘了 `allow_delegation` 的语义 | 任务被推给别人或无人接手 | 该开关决定能否把任务委派出去 | 明确分工：执行者设 `False`，协调者设 `True` |
| 把 Agent 当「更聪明的聊天」用 | 效果不如直接写 Prompt | 用错了工具——简单任务不需要 Agent | 单步任务直接 Prompt/Chain；需要多步决策与工具调用才上 Agent |
| 无日志与追踪 | 出问题无法定位 | `verbose=False` | 调试期开 `verbose=True`（或 2），生产改为结构化日志 |

## 5. 面试问答

**Q1：什么是 AI Agent？它由哪几部分构成？与传统软件有什么本质区别？**

<details><summary>参考答案</summary>

AI Agent 是一种能够**感知环境、进行决策和执行动作**的智能实体，可以是物理实体（机器人）也可以是虚拟实体（软件程序）。
不同于传统人工智能，它具备通过**独立思考、调用工具**逐步完成给定目标的能力。
当下讨论的 Agent 本质是一个**控制 LLM 来解决问题的代理系统**。

构成公式：**Agent = LLM + 记忆 + 任务规划 + 工具使用**，
对应五个工作环节：Prompt（初始输入）→ LLM（理解与规划）→ Memory（上下文与知识库）→
Planning（任务拆解、目标设定、路径规划）→ Action（调用计算器/代码解释器/API 执行）。

与传统软件的本质区别：
① **任务范围**：传统软件只能解决有限范围的任务，Agent 可以解决无限域的任务；
② **机制**：传统软件靠预定义指令、逻辑、规则和启发式算法把流程固定下来，
Agent 把功能开发迁移为以 AI 为主要驱动力，以大模型为基础设施、以 Agent 为核心产品形态；
③ **范式**：从「面向过程」迁移到「面向目标」；
④ **生产方式**：从「人类为中心、AI 辅助」变为「AI 为中心、人类为辅助」。
</details>

**Q2：CrewAI 的核心组件有哪些？如何保证多 Agent 按预期协作？**

<details><summary>参考答案</summary>

五个核心组件：
- **Agent**：每个 Agent 有独特的个性、背景故事和技能，专注子任务（关键属性 `role`/`goal`/`backstory`）；
- **Task**：明确目标与要求，被分解成小的专注子任务；
- **Tools**：按任务定制的代理工具；
- **Process**：任务的分解、资源分配、沟通协调（如 `Process.sequential`）；
- **Crew**：代理人、任务和过程相结合的容器层，是任务执行的实际场所。

保证按预期协作的三条经验：
① **用 `Process.sequential` 明确执行顺序**，上一个任务的结果会作为附加内容传递给下一个任务；
② **任务描述里写死完成判据**（如「最后的答案必须是文件已保存到磁盘」「一定要成功发送邮件」），
否则 Agent 容易自称完成而实际没调用工具；
③ **工具按角色最小分配**——写文件的工具只给编辑，发邮件的工具只给信使，减少误用；
另外 `allow_delegation` 要按分工设置，执行者关掉、协调者打开。
</details>

**Q3：给 Agent 设计一个工具时要注意什么？**

<details><summary>参考答案</summary>

① **描述要面向「做什么」**：工具描述会进入 Prompt，是模型选择工具与填参数的唯一依据，
应写清用途与参数含义，而不是实现细节；
② **返回明确、可判断的结果字符串**：如成功返回「信件已发送」、失败返回「发送失败：<原因>」，
让模型能据此决定下一步，而不是收到含糊的空值；
③ **内部必须捕获异常**：工具报错不能让整个 Agent 流程崩溃，应把错误当信息返回给模型，让它调整策略；
④ **敏感信息走环境变量**：SMTP 账号、授权码、API Key 都不能硬编码（示例中的明文写法需要纠正）；
⑤ **资源要正确释放**：如 SMTP 用 `try/finally` 保证 `quit`；
⑥ **参数尽量简单且类型明确**：复杂结构容易导致模型构造错误；
⑦ **保持幂等或可重试**：Agent 可能因误判重复调用（例如重复发邮件），
高风险操作应加去重或人工确认。
</details>

## 6. 自测题

**1. 写出 AI Agent 的构成公式和五大工作环节。**

<details><summary>参考答案</summary>

构成公式：**AI Agent = LLM + 记忆 + 任务规划 + 工具使用**。

五大工作环节：
① **Prompt 提示词**——Agent 接收的初始输入，描述角色范围与任务背景；
② **LLM 大模型**——Agent 进行任务规划和知识推理的重要工具（理解、识别、选择）；
③ **Memory 记忆**——保留当前用户输入内容、上下文信息、外部向量存储的知识库；
④ **Planning 规划**——对任务的拆解、思考执行与返回，涉及任务分解、目标设定、搜索、路径规划；
⑤ **Action 行动**——执行具体操作，包含工具如计算器、代码解释器、API 等。
</details>

**2. AI Agent 的三类主要类别分别是什么？各举一个例子。**

<details><summary>参考答案</summary>

- **反应型 Agent**：根据当前环境状态做出直接反应。例：简单的温度调节器，根据当前温度调整加热或制冷。
- **目标导向型 Agent**：根据预设目标做决策，能够规划和执行序列动作以达成目标。
 例：自动驾驶汽车，以安全到达目的地为目标进行各种驾驶操作。
- **学习型 Agent**：能够基于过去的经验和数据学习，不断优化自身表现。例：基于用户反馈不断优化的聊天机器人。
</details>

**3. 的写信项目里，三个 Agent 分别是什么角色、各自负责什么任务？**

<details><summary>参考答案</summary>

| Agent | role | 任务 |
|---|---|---|
| 作家 | 作家（千万级粉丝，擅长情感类文章） | 写情书 Task：根据用户需求创作情感丰富的文章，最长不超过 300 词 |
| 内容编辑 | 内容编辑（多年书信编辑经验） | 编辑书信 Task：检查语法错误、编辑并格式化，**调用工具把内容保存到本地磁盘** |
| 寄信人 | 寄信人（勤恳的信使） | 寄信 Task：读取磁盘上的书信内容，**调用工具发送邮件** |

三者用 `Crew(agents=[...], tasks=[...], process=Process.sequential)` 组队，
`crew.kickoff` 启动，任务按顺序执行、上一任务结果作为附加内容传给下一任务。
工具按角色分配：编辑只有 `store_poesy_to_txt`，寄信人只有 `send_message`。
</details>

**4. 为什么要在任务描述里强调「你最后的答案必须是信息是否已被存储在本地磁盘中」这类话？**

<details><summary>参考答案</summary>

因为 Agent 的行为由 Prompt 与任务描述驱动，而 LLM 有「提前宣告成功」的倾向——
它可能在没有真正调用工具的情况下回答「已完成」，导致流程看起来成功但实际没有任何副作用（文件没写、邮件没发）。

在任务描述里写死**可验证的完成判据**，会产生三个效果：
① 把「是否完成」的判定从模型的自我感觉绑定到**具体的事实状态**（文件是否落盘、邮件是否发送成功）；
② 引导 Agent 主动调用工具去达成并确认该状态；
③ 让调试时有明确的对错标准。

这也是 Agent 工程化的通用原则：**把验收标准写进 Prompt，而不是事后靠人检查。**
</details>

**5. 什么时候不该用 Agent？**

<details><summary>参考答案</summary>

当任务**步骤固定、无需动态决策**时，用 Prompt / Chain / 工作流更划算：

① **单步任务**（分类、抽取、摘要、翻译）——一次 LLM 调用即可，用 Agent 只会增加延迟与不确定性；
② **流程完全确定的流水线**——用固定的 Chain 或 Flow 编排，可预测、可测试、成本更低；
③ **对延迟与成本极敏感的高并发场景**——Agent 的多次「思考—调用—观察」循环会成倍增加 token 与耗时；
④ **高风险且不可逆的操作**——让模型自主决定「是否发送/是否删除」风险过大，
应收窄为「模型给建议、人确认执行」，或只暴露幂等、可回滚的工具。

判断标准：**任务路径是否需要模型根据中间结果动态决定？** 需要才上 Agent。
</details>

## 7. 延伸阅读

- [ReAct: Synergizing Reasoning and Acting (arXiv:2210.03629)](https://arxiv.org/abs/2210.03629)
- [Reflexion (arXiv:2303.11366)](https://arxiv.org/abs/2303.11366)
- [LangChain 官方文档](https://python.langchain.com/docs/introduction/)
- [CrewAI GitHub](https://github.com/joaomdmoura/crewAI)
- [AutoGen GitHub](https://github.com/microsoft/autogen)
- [OpenAI Function Calling 指南](https://platform.openai.com/docs/guides/function-calling)

---

[⬅️ 返回本目录索引](README.md)
