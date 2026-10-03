> **一句话总结**：AI Agent 本质是「用 LLM 当大脑、用工具当手脚、用记忆当上下文、用规划当路线」的代理系统（`AIAgent = LLM + Memory + Planning + Tools`），软件范式因此从「面向过程」迁移到「面向目标」。
> **前置知识**：[../llm/05-大模型API与调用实践.md](../../06-llm/04-提示工程/05-大模型API与调用实践.md) 的消息角色与 API 调用、[../llm/04-提示词工程.md](../../06-llm/04-提示工程/04-提示词工程.md) 的 system prompt 用法、本目录 [02-Function-Calling与工具调用](../02-工具与规划/02-Function-Calling与工具调用.md)。
> **学完能做到**：
> 1. 用一句话说清 Agent 与传统软件、与普通聊天机器人的区别，并画出「感知 → 规划 → 行动 → 观察」闭环。
> 2. 说出 `Prompt / LLM / Memory / Planning / Action` 五要素各自在闭环里承担什么，以及 ReAct 的 Thought → Action → Observation 结构。
> 3. 写一个带终止条件、带工具注册表、带观察回填的最小 Agent 循环，并知道它会在哪些条件下失控。

---

## 1. 核心概念

### 1.1 什么是 AI Agent

给出的定义：

> AI Agent（Artificial Intelligence Agent）：一种能够**感知环境、进行决策和执行动作**的智能实体，可以是物理实体（如机器人）或虚拟实体（如软件程序）。

定义里有三个动词，缺一不可：

| 关键词 | 含义 | 对应工程实现 |
| --- | --- | --- |
| 感知（Perception） | 读取环境状态 | 用户输入、API 返回、数据库查询结果、传感器数据 |
| 决策（Decision） | 判断下一步做什么 | LLM 推理 + 规划 + 工具选择 |
| 执行（Action） | 真正改变世界 | 调用函数 / API / 写文件 / 发消息 |

区别于传统人工智能：传统 AI 是「输入 → 模型 → 输出」的单次映射；Agent 具备**通过独立思考、调用工具去逐步完成给定目标**的能力。的 AutoGPT 是最典型的早期例子：只给它一个 AI 名称、一段描述和五个目标，它就能自己完成一个项目（例如「基于新浪娱乐电影网站的最新报道信息，抽取出所有的电影标题，并将标题保存到本地文档中」）。

### 1.2 Agent 的三种主要类别

| 类别 | 行为特征 | 的例子 |
| --- | --- | --- |
| 反应型 Agent | 根据当前环境状态做出**直接反应**，不做长期规划 | 温度调节器：检测当前温度，决定加热还是制冷 |
| 目标导向型 Agent | 根据预设目标做决策，能够**规划和执行序列动作**以达成目标 | 自动驾驶汽车：以安全到达目的地为目标，执行各种驾驶操作 |
| 学习型 Agent | 基于过去的经验和数据学习，**不断优化自身表现** | 基于用户反馈不断优化的聊天机器人 |

这三类不是互斥的：当下的 LLM Agent 通常是「目标导向 + 可学习」的混合体——用 LLM 做规划（目标导向），用历史会话与反馈做上下文更新（学习）。

### 1.3 Agent 的能力公式

> **AIAgent = LLM + 记忆 + 任务规划 + 工具使用**

| 组成部分 | 作用 | 要点 |
| --- | --- | --- |
| LLM（大模型） | 推理、理解、识别、选择 | 「大模型是 Agent 进行任务规划和知识推理的重要工具」 |
| Memory（记忆） | 保存上下文与外部知识 | 「可以保留当前用户输入内容；上下文内容；外部向量存储的知识库；网页信息等」 |
| Planning（规划） | 拆解任务、设定目标、搜索解法 | 「利用 LLM 大模型对要完成的任务或解决的问题进行深入分析，生成可能的解决方案」 |
| Tools（工具使用） | 与真实世界交互 | 「包含工具：计算器、代码解释器、API 等」 |

一句话概括：LLM 提供通用推理能力，但**没有实时信息、没有私有数据、不会精确计算**；记忆和工具负责把这三种缺口补上，规划负责把「一个模糊目标」变成「一串可执行动作」。

### 1.4 Agent 的工作流程五要素

把 Agent 的工作流程拆成 5 个环节：

| 编号 | 环节 | 职责 | 输入 / 输出 |
| --- | --- | --- | --- |
| 01 | Prompt 提示词 | Agent 接收到的初始输入，包含角色范围、任务背景 | 输入：用户请求 → 输出：结构化的任务描述 |
| 02 | LLM 大模型 | 执行任务规划和知识推理 | 输入：提示词 → 输出：计划、判断、工具选择 |
| 03 | Memory 记忆 | 保存用户输入、上下文、外部知识库 | 输入：会话与检索结果 → 输出：可回填的上下文 |
| 04 | Planning 规划 | 任务分析、目标设定、搜索、路径规划 | 输入：任务与提示词 → 输出：子目标序列 |
| 05 | Action 行动 | 执行具体操作：查询、匹配、拆解、思考执行、返回 | 输入：规划结果 → 输出：工具调用与最终答复 |

注意 04 与 05 的关系：**Planning 决定「做什么」，Action 决定「怎么做」**。在工程实现上二者往往交织在一次 LLM 调用里（模型同时输出「我要调用哪个工具」和「参数是什么」），但排错时要把它们分开看——是做错了计划，还是执行计划时出了错。

### 1.5 完整例子：用 Agent 处理退货请求

用退货场景串起了五个环节，逐步展开如下：

| 步骤 | 环节 | 发生了什么 |
| --- | --- | --- |
| 1 | Prompt | 用户说：「我想退货订单 #12345 的商品，因为有缺陷」 |
| 2 | LLM | 解析请求，识别出订单号和退货原因 |
| 3 | Memory | Agent 检索订单 #12345 的历史信息，核对是否符合退货条件 |
| 4 | Planning | 验证订单、确定客户想退货、检查库存状态，规划出「生成退货标签 → 通知仓库 → 反馈客户」 |
| 5 | Action | 生成退货标签，通知仓库处理退货，最后把结果反馈给客户 |

这个例子的价值在于：**整个链路里没有一步是「预定义 if-else」**，每一步的判断都由 LLM 结合当前上下文产生。这就是 1.7 节「面向目标」的含义。

### 1.6 当前基于大模型的 Agent 呈现形式对比

| 形式 | 能力范围 | 有无规划 | 有无记忆 | 有无工具 | 代表来源 |
| --- | --- | --- | --- | --- | --- |
| Copilot 场景助理 | 文本 + 代码 | 无 | 无 | 无 | 大厂自研 |
| ChatGPT 对话式 | 文本、代码、网页 | 无 | 有（会话内） | 大模型自带 + 插件 | 小厂引入 / 大厂自研 |
| Flow 工作流 | 文本、代码、网页 | 有（人工编排的流程） | 有 | 大模型自带 + 插件 | 小厂引入 / 大厂自研 |
| Agent 自主智能体 | 文本、代码、网页 | **有（模型自主）** | 有 | 大模型自带 + 插件 + API + RPA | 小厂引入 / 大厂自研 |

这张表的读法是看「规划」一列：Flow 工作流的规划是**人**写的，Agent 的规划是**模型**生成的。所以「工作流 + 一堆节点」不等于 Agent。

### 1.7 Agent 与传统软件的区别

| 维度 | 传统软件 | AI Agent |
| --- | --- | --- |
| 任务范围 | 只能解决**有限范围**的任务 | 可以解决**无限域**的任务 |
| 核心要素 | 软件工程师 | Agent |
| 机制 | 通过预定义的指令、逻辑和启发式算法把流程固定下来 | 把原本由人类主导的功能开发，迁移为以 AI 为主要驱动力 |
| 生产方式 | 人类为中心，AI 辅助 | AI 为中心，人类辅助 |
| 产品形态 | 用户按指令逻辑一步步操作，结果符合预期 | 目标导向的智能体自主生成 |
| 技术基础设施 | 代码 + 数据库 | 大模型 + Agent 框架 |

一句话：**Agent 使软件架构的范式从「面向过程」迁移到「面向目标」**。用户不再描述步骤，而是描述目标；步骤由模型规划。这也解释了为什么 Agent 的可靠性问题比传统软件更难——它多了一层「计划」的不确定性。

### 1.8 常见实现工具与框架

| 工具 / 框架 | 类型 | 特点 | 地址 |
| --- | --- | --- | --- |
| AutoGPT | 自主 Agent | 给定名称、描述和若干目标即可自主完成项目 | https://github.com/Significant-Gravitas/AutoGPT |
| 百度 AgentBuilder | 平台 | 提供构建、训练和部署 Agent 的全流程支持 | https://agents.baidu.com/center |
| 字节扣子（Coze） | 平台 | 快速搭建基于大模型的问答 Bot 并发布到社交平台 | https://www.coze.cn/home |
| 天工 SkyAgents | 企业平台 | 集成大模型、知识库等模块，支持定制化 Agent | https://model-platform-skyagents.tiangong.cn/home/agent |
| AgentGPT | 开源工具 | 基于 GPT-4 的自动化机器人，浏览器中配置部署 | https://agentgpt.reworkd.ai/zh |
| LangChain | 开发框架 | Agents 模块提供 Agent 管理、记忆模块、工具集成 | https://github.com/langchain-ai/langchain |
| AutoGen | 多 Agent 框架 | 多个可定制、可对话的代理协作解决任务，允许人类参与 | https://github.com/microsoft/autogen |
| ChatDev | 多 Agent 框架 | 通过自然语言交互和多智能体协作实现软件开发全流程自动化 | https://github.com/OpenBMB/ChatDev |
| CrewAI | 多 Agent 框架 | 建立在 LangChain 之上，支持构建多 Agent 协作系统 | https://github.com/joaomdmoura/crewAI |

选型的一般顺序（**说明**：本小节超出本主题范围，为通用知识补充）：先用平台（Coze / AgentBuilder）验证业务可行性，再用框架（LangChain / CrewAI）落地私有逻辑，最后才考虑自研编排层。

### 1.9 应用场景

列举的行业场景：

| 行业 | 典型场景 |
| --- | --- |
| 电商 | 语音助手与购物：集成到智能音箱和手机应用，通过语音命令购物 |
| 教育 | 远程教育和在线学习：学习资源和辅导 |
| 旅游 | 旅游体验增强：AR / VR 提供沉浸式体验 |
| 制造 | 机器人自动化：控制工业机器人执行任务，提高生产自动化水平 |
| 金融 | 智能风控：精准风险评估和欺诈检测 |
| 医疗 | 医疗影像分析：辅助医生分析影像，提高诊断准确性和效率 |

共同点：都是「一个明确目标 + 需要多步操作 + 依赖外部信息或工具」的任务——这正是 Agent 相对单轮 LLM 调用的优势区间。

---

## 2. 关键机制

### 2.1 感知—决策—行动闭环

把五要素落成一个循环，就是 Agent 的运行骨架：

```text
 ┌──────────────────────────────────────────┐
 │ │
用户目标 ──> [Prompt] ──> [LLM 规划/推理] ──> [Action 工具调用]
 ↑ │
 │ ↓
 [Memory 上下文] <── [Observation 观察结果]
 ↑
 [外部知识库 / 环境状态]
```

循环的退出条件是 **Agent 认为目标已达成**（或达到最大步数 / 超时 / 需要人类介入）。在 Function Call 章节讲同一件事时用的是「是否需要调用外部信息」的判定节点——判定为「否」则直接输出，判定为「是」则选择 API、执行、再回到模型。

### 2.2 ReAct：把「想」和「做」交替进行

> **说明**：这里只在 LangChain 的 `zero-shot-react-description` 代理类型里提到「利用 ReAct 框架根据工具的描述来决定使用哪个工具」，未展开 ReAct 细节，本小节为通用知识补充。

ReAct（Reasoning + Acting，arXiv:2210.03629）的核心思想是让模型在**同一条轨迹里交替产出推理（Reasoning trace）与动作（Action）**，再用环境的反馈（Observation）纠正下一步推理。它的轨迹格式是：

```text
Thought: 我需要先知道北京今天的天气
Action: get_current_weather
Action Input: {"location": "北京"}
Observation: {"location": "北京", "temperature": "33℃", "type": "晴"}
Thought: 我已经拿到天气数据，可以回答用户了
Final Answer: 北京今天晴，最高 33℃，最低 17℃。
```

三个关键点：

1. **Thought 是给模型自己看的**，不执行，允许模型「打草稿」，这也是为什么重复推理能提升准确率；
2. **Action 的合法值来自工具描述（tool description）**，所以工具描述写得清楚，等于给模型限定了解空间；
3. **Observation 必须原样回填**，不能被模型改写——它是唯一的事实来源。

对比其它范式：

| 范式 | 特点 | 典型缺陷 |
| --- | --- | --- |
| Chain-of-Thought（CoT） | 只推理、不行动 | 无法获取外部信息，事实错误无法纠正 |
| Act-only | 只行动、不推理 | 动作选择盲目，容易连续调用错误工具 |
| **ReAct** | 推理与行动交替 | 轨迹变长，token 成本与延迟上升 |

### 2.3 ReAct 循环的伪代码（对照五要素）

```text
function run(goal):
 memory = [system_prompt, user(goal)]
 for step in 1..max_steps:
 thought, action, action_input = llm(memory, tools=TOOL_SCHEMAS)
 if action is None: # 模型认为可以直接回答
 return thought # 对应：Action 环节的「返回」
 observation = execute(action, action_input) # 观察环境
 memory.append(assistant(thought, action, action_input))
 memory.append(tool(observation)) # 对应：Memory 环节
 return "达到最大步数仍未完成"
```

这段伪代码里的每个符号都能对回：`llm(memory, tools=...)` 是 LLM + Prompt；`execute` 是 Action；`memory.append` 是 Memory；`for step in ...` 是 Planning 的展开形式。

### 2.4 从对话机器人到 Agent：医疗问诊机器人的位置

的 GPT2 医疗问诊机器人是一个**对话式 Agent 的雏形**：

- 数据处理把一轮对话拼成 `[CLS] 句子1 [SEP] 句子2 [SEP] …`（见 `data_preprocess/preprocess.py`），这就是最简单的记忆载体；
- 推理时把最近 `max_history_len` 轮历史依次拼进 `input_ids` 再送模型（见 [05-Agent的记忆与知识管理](../03-记忆与多智能体/05-Agent的记忆与知识管理.md)），这就是上下文记忆；
- 但它**没有工具、没有自主规划**，回复完全由模型的下一 token 概率决定。

对照 1.6 节的形式表，它落在「ChatGPT 对话式」那一栏：有记忆、无规划、无工具。理解这一点，就能明白 Agent 的两个增量到底是什么——**行动计划（Planning）**和**工具调用（Action）**。

### 2.5 终止条件设计

Agent 循环必须显式设置退出条件，否则会陷入「反复调用同一工具」的死循环。工程上常用的四道闸门：

| 闸门 | 做法 | 作用 |
| --- | --- | --- |
| 显式终态 | 定义 `Final Answer` / `finish` 动作 | 让模型有明确的「停止」出口 |
| 步数上限 | `max_iterations`（LangChain 默认有类似参数） | 兜底，防止无限循环 |
| 超时 | 整体 wall-clock 超时 | 防止单步工具卡死拖垮整条链路 |
| 重复检测 | 比较连续两步的 Action + Action Input | 检测原地打转，触发人工介入 |

---

## 3. 可运行示例

### 3.1 零依赖的最小 Agent 循环（可真实运行）

下面这个例子不依赖任何模型，用一个「脚本化的假 LLM」替代模型输出，把 Agent 的骨架跑通。**依赖：仅 Python 标准库（Python 3.8+）。**

```python
"""最小 Agent 循环示例：用脚本化的 planner 替代 LLM，演示 ReAct 结构。

依赖：仅标准库。
"""

import json
import re

TOOL_SCHEMAS = [
{
"name": "get_current_weather",
"description": "查询给定城市当前的天气情况",
"parameters": {
"type": "object",
"properties": {
"location": {"type": "string", "description": "城市名，例如 北京"}
},
"required": ["location"],
},
},
{
"name": "calculator",
"description": "执行四则运算，输入形如 '3*4+2' 的表达式",
"parameters": {
"type": "object",
"properties": {
"expression": {"type": "string", "description": "算术表达式"}
},
"required": ["expression"],
},
},
]

def get_current_weather(location):
    fake_db = {"北京": {"type": "晴", "high": 33, "low": 17}}
    return fake_db.get(location, {"error": "未知城市: %s" % location})

def calculator(expression):
    if not re.fullmatch(r"[0-9+\-*/(). ]+", expression):
        return {"error": "表达式包含非法字符"}
    return {"result": eval(expression)} # 仅演示，生产环境请改用 ast.literal_eval

TOOLS = {"get_current_weather": get_current_weather, "calculator": calculator}

class ScriptedLLM:
    """假 LLM：按预设脚本依次吐 Thought/Action，演示 ReAct 轨迹格式。"""

    def __init__(self, script):
        self.script = list(script)
        self.calls = 0

        def __call__(self, memory):
            if self.calls >= len(self.script):
                return "Final Answer: 北京今天晴，最高 33℃，最低 17℃。", None, None
            action, action_input = self.script[self.calls]
            self.calls += 1
            if action is None:
                return action_input, None, None
            return "需要调用工具 %s" % action, action, action_input

        def execute(action, action_input):
            if action not in TOOLS:
                return {"error": "未知工具: %s" % action}
            return TOOLS[action](**action_input)

        def run_agent(goal, llm, max_steps=5):
            memory = [{"role": "user", "content": goal}]
            for step in range(1, max_steps + 1):
                thought, action, action_input = llm(memory)
                print("[step %d] Thought: %s" % (step, thought))
                if action is None:
                    print("[step %d] Finish" % step)
                    return thought
                observation = execute(action, action_input)
                print("[step %d] Action: %s(%s)" % (step, action, json.dumps(action_input, ensure_ascii=False)))
                print("[step %d] Observation: %s" % (step, json.dumps(observation, ensure_ascii=False)))
                memory.append({"role": "assistant", "content": thought, "action": action})
                memory.append({"role": "tool", "content": json.dumps(observation, ensure_ascii=False)})
                return "达到最大步数仍未完成"

            if __name__ == "__main__":
                scripted = ScriptedLLM([
                ("get_current_weather", {"location": "北京"}),
                (None, "Final Answer: 北京今天晴，最高 33℃，最低 17℃。"),
                ])
                print(run_agent("今天北京的天气如何？", scripted))
```

运行后可以看到完整的 `Thought → Action → Observation → Final Answer` 轨迹——这正是 ReAct 的外形，只是「思考」由脚本而非模型产生。

### 3.2 换成真实模型的骨架（智谱 ChatGLM）

 Function Call 章节用的是智谱 `glm-4`。把上面的 `ScriptedLLM` 换成真实调用即可：

```text
"""真实模型版 Agent 骨架（需联网与 API Key）。

依赖：pip install zhipuai python-dotenv
环境变量：ZHIPU_API_KEY
"""

import json
import os

from zhipuai import ZhipuAI

from tools import TOOL_SCHEMAS, TOOLS # 复用 3.1 中定义的注册表

def chat_completion_request(client, messages, tools=None, tool_choice=None, model="glm-4"):
 try:
 return client.chat.completions.create(
 model=model, messages=messages, tools=tools, tool_choice=tool_choice
 )
 except Exception as exc: # 网络/额度/参数错误都收敛成日志，不中断循环
 print("Unable to generate ChatCompletion response")
 print("Exception: %s" % exc)
 return None

def run(goal, max_steps=5):
 client = ZhipuAI(api_key=os.environ["ZHIPU_API_KEY"])
 messages = [
 {"role": "system", "content": "你是一个助手，不确定的信息不要编造，必要时调用工具。"},
 {"role": "user", "content": goal},
 ]
 for _ in range(max_steps):
 response = chat_completion_request(client, messages, tools=TOOL_SCHEMAS, tool_choice="auto")
 if response is None:
 return "模型调用失败"
 message = response.choices[0].message
 messages.append(message.model_dump())
 if not message.tool_calls:
 return message.content
 for tool_call in message.tool_calls:
 name = tool_call.function.name
 args = json.loads(tool_call.function.arguments)
 result = TOOLS[name](**args) if name in TOOLS else {"error": "未知工具"}
 messages.append({
 "role": "tool",
 "tool_call_id": tool_call.id,
 "content": json.dumps(result, ensure_ascii=False),
 })
 return "达到最大步数仍未完成"

if __name__ == "__main__":
 print(run("今天北京的天气如何？"))
```

工具调用的协议细节（`tool_calls`、`tool_call_id`、`model_dump`）在 [02-Function-Calling与工具调用](../02-工具与规划/02-Function-Calling与工具调用.md) 里逐字段拆解。

---

## 4. 常见坑

| 现象 | 原因 | 解决 |
| --- | --- | --- |
| Agent 反复调用同一个工具，永不结束 | 缺少终止条件；工具返回值没有提供新信息 | 设置 `max_iterations`；在 system prompt 里要求「连续两次得到相同结果时必须给出 Final Answer」 |
| 模型「调用」了一个不存在的工具名 | 工具名只写在提示词散文里，没有结构化 schema | 用 tool schema 显式声明名称与参数（见 [02](../02-工具与规划/02-Function-Calling与工具调用.md)） |
| 模型编造工具返回结果（幻觉 Observation） | 把 Observation 也让模型生成，而不是真的执行工具 | Observation 必须由代码执行后原样回填，禁止模型改写 |
| 把聊天机器人当成 Agent 汇报 | 只有记忆、没有 Planning 和 Action | 对照 1.6 节的呈现形式表，先确认「规划是模型做的」 |
| 上下文越滚越长，超出模型窗口或成本飙升 | 每一步的 Thought/Action/Observation 都全量保留 | 对旧步骤做摘要压缩，或只保留最近 K 步（见 [05-Agent的记忆与知识管理](../03-记忆与多智能体/05-Agent的记忆与知识管理.md)） |
| 简单任务也走 Agent，结果又慢又贵 | 用 Agent 解决单轮调用就能做的事 | 先判断任务是否需要多步与外部工具；单轮能答的直接走 [../llm/05-大模型API与调用实践.md](../../06-llm/04-提示工程/05-大模型API与调用实践.md) |
| 工具执行报错后 Agent 直接崩溃 | 工具内部异常没有转换成 Observation | 工具函数内部 try/except，把错误信息作为 Observation 返回给模型，让模型自己纠错 |

---

## 5. 面试问答

<details><summary>参考答案</summary>

**Q1：AI Agent 和传统软件最本质的区别是什么？**

传统软件是「面向过程」的：工程师把流程写成预定义的指令、逻辑和启发式算法，任务范围因此被限定在有限域内，用户按步骤操作、结果符合预期。Agent 是「面向目标」的：用户只描述目标，由 LLM 完成任务分析、目标设定、路径规划和工具调用，因而可以处理无限域的任务。机制上，主导方从「软件工程师写逻辑」迁移为「模型生成逻辑」；生产方式从「人类为中心、AI 辅助」迁移为「AI 为中心、人类辅助」。代价是引入了「计划」这一层不确定性，可靠性设计因此成为工程重点。

</details>

<details><summary>参考答案</summary>

**Q2：AIAgent = LLM + 记忆 + 任务规划 + 工具使用，这四项各自解决什么问题？**

LLM 提供通用推理与语言理解能力，负责任务规划与知识推理；记忆解决「模型本身无状态」的问题，保存用户输入、会话上下文、外部向量知识库与网页信息；任务规划把模糊目标拆成可执行的子目标序列，负责任务分析、目标设定、搜索与路径规划；工具使用解决模型的三类硬伤——信息实时性（训练数据有截止日期）、数据局限性（无法覆盖医疗/法律等专业领域）、功能扩展性（不能精确计算、不能访问私有系统），通过调用计算器、代码解释器、API 等补齐能力。四者缺一：只有 LLM 是聊天机器人，只有工具没有规划是脚本，没有记忆则无法多轮推进。

</details>

<details><summary>参考答案</summary>

**Q3：ReAct 为什么要让推理和行动交替，而不是先想完再做？**

因为纯推理（CoT）无法获取外部信息，一旦前提错误就会一路错到底，且无法自我纠正；纯行动（Act-only）则动作选择盲目，容易连续调用错误工具、浪费步数。ReAct 把 Thought、Action、Observation 放在同一条轨迹里交替产生，每一次环境反馈都会成为下一步推理的新证据，从而形成「假设—验证—修正」的闭环。代价是轨迹变长，token 成本与延迟上升，因此工程上需要配合步数上限与历史压缩。另外 Thought 只对模型自己可见、不执行，起到了显式草稿（scratchpad）的作用，这本身也能提升推理质量。

</details>

---

## 6. 自测题

<details><summary>参考答案</summary>

**1. 判断：一个只会按顺序执行 RAG 检索、拼 prompt、调用模型的流程，算 Agent 吗？**

不算（至少不是自主 Agent）。它的「规划」是人预先编排的固定流程，落在 1.6 节表格里的 Flow 工作流一栏。要成为 Agent，需要模型根据当前状态**自主决定**下一步做什么、调用哪个工具。

</details>

<details><summary>参考答案</summary>

**2. 把 Agent 分成哪三类？各举一个例子。**

反应型（温度调节器：根据当前温度直接决定加热/制冷）、目标导向型（自动驾驶汽车：以安全到达为目标规划并执行序列动作）、学习型（基于用户反馈不断优化的聊天机器人：从过去经验中学习并优化表现）。

</details>

<details><summary>参考答案</summary>

**3. 在退货请求的例子中，Planning 和 Action 分别做了什么？**

Planning：验证订单、确定客户想退货、核对库存是否符合退货条件，并规划出「生成退货标签 → 通知仓库 → 反馈客户」的路径。Action：按规划实际执行——生成退货标签、通知仓库处理退货、把处理结果反馈给客户。一句话：Planning 决定做什么，Action 决定怎么做并真正改变外部状态。

</details>

<details><summary>参考答案</summary>

**4. Agent 循环可能失控的三种典型情况，以及对应的兜底手段？**

①原地打转（反复调用同一工具）→ 步数上限 + 连续两步 Action/Action Input 相同即触发人工介入；②超时或工具卡死 → 整体 wall-clock 超时 + 单次工具调用超时；③模型幻觉出不存在的工具或参数 → 用 tool schema 限定合法动作集合，执行前做参数校验。

</details>

<details><summary>参考答案</summary>

**5. 为什么说医疗问诊机器人是「对话式 Agent 的雏形」？**

因为它已经具备记忆的雏形：数据侧把多轮对话拼成 `[CLS] 句子1 [SEP] 句子2 [SEP] …`，推理侧把最近若干轮历史一起送入模型，实现了上下文延续。但它没有工具、也没有自主规划，回复完全由下一 token 概率决定，因此只覆盖了 Agent 五要素中的 Prompt/LLM/Memory 三项，缺 Planning 与 Action。

</details>

---

## 7. 延伸阅读

- ReAct: Synergizing Reasoning and Acting in Language Models —— https://arxiv.org/abs/2210.03629
- AutoGPT 项目仓库 —— https://github.com/Significant-Gravitas/AutoGPT
- LangChain Agents 官方文档 —— https://python.langchain.com/docs/how_to/#agents
- AutoGen（多 Agent 对话框架） —— https://github.com/microsoft/autogen
- CrewAI 官方文档 —— https://docs.crewai.com/
- Anthropic, Building Effective Agents —— https://www.anthropic.com/engineering/building-effective-agents
- ：《第十章：AI Agents 开发应用》

---

[⬅️ 返回本目录索引](README.md)
