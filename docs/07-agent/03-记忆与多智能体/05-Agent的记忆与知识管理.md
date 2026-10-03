> **一句话总结**：大模型本身无状态、不保存上次交互的内容，Agent 的记忆全靠外部实现——**短期记忆**是会话内回传的 `messages`（对话历史），**长期记忆**是跨会话持久化的状态文件与向量知识库；三者共同决定了 Agent 能「记住多久、记住多少」。
> **前置知识**：[03-LangChain与工具编排](03-LangChain与工具编排.md) 的 Memory 组件、[06-RAG作为Agent的知识获取手段](06-RAG作为Agent的知识获取手段.md) 的向量检索、[02-Function-Calling与工具调用](../02-工具与规划/02-Function-Calling与工具调用.md) 的 messages 角色约定。
> **学完能做到**：
> 1. 区分短期记忆、长期状态记忆、外部知识记忆三类载体，并说出各自生命周期。
> 2. 用 `ChatMessageHistory` 与 `messages_to_dict` / `messages_from_dict` 做会话记忆的持久化与恢复。
> 3. 设计一个带滑动窗口截断的状态文件（如 `last_price` / `last_status` / `last_notify_time`），并解释为什么状态需要落盘才能实现「不重复提醒」。

---

## 1. 核心概念

### 1.1 为什么 Agent 需要记忆

给出的原因非常直接：

> 大模型本身不具备上下文的概念，它并不保存上次交互的内容，ChatGPT 之所以能够和人正常沟通对话，因为它**进行了一层封装，将历史记录回传给了模型**。

也就是说，所谓「对话记忆」并不是模型记住了什么，而是**每次请求都把历史重新拼进 prompt**。这带来两个直接后果：

1. **记忆是有成本的**：历史越长，每次请求的 token 越多，费用与延迟越高；
2. **记忆是有上限的**：模型的上下文窗口有限，超出就必须裁剪或压缩。

### 1.2 记忆的分类

这里把 Memory 分为两种类型：

| 类型 | 定义 | 载体 | 生命周期 |
| --- | --- | --- | --- |
| 短期记忆 | 单一会话时传递数据 | `messages` 列表 / token id 列表 | 进程内，会话结束即失 |
| 长期记忆 | 处理多个会话时获取和更新信息 | 数据库、文件、向量库 | 跨进程、跨会话 |

> **说明**：本小节超出本节范围，为通用知识补充。更细的工程分类是「四层记忆」：①工作记忆（当前 prompt 内的上下文）；②情景记忆（历史会话，对应短期记忆的持久化）；③语义记忆（结构化事实，如用户画像）；④程序性记忆（工具用法与固定流程）。

### 1.3 的四种记忆载体

| 载体 | 出现位置 | 存什么 | 读的方式 | 写的方式 |
| --- | --- | --- | --- | --- |
| `ChatMessageHistory` | LangChain Memory 组件 | `HumanMessage` / `AIMessage` 对象列表 | `history.messages` | `add_user_message` / `add_ai_message` |
| 消息字典 | `messages_to_dict` / `messages_from_dict` | 可 JSON 序列化的 dict 列表 | `messages_from_dict(dicts)` | `messages_to_dict(history.messages)` |
| token id 历史 | GPT2 医疗问诊机器人 | 每轮 utterance 的 token id 列表 | 拼进 `input_ids` 送模型 | `history.append(text_ids)` |
| JSON 状态 / 历史文件 | 黄金价格监控项目 | 上一次价格、状态、提醒时间；历史价格序列 | `load_state()` / `load_history()` | `save_state()` / `json.dump` |
| 向量库（外部知识） | RAG 系统 | 文档块向量 + 父块内容 | 混合检索 + 重排 | `upsert` 写入 |

注意第四行其实包含两类不同的东西：**状态**（key-value，只关心最新值）与**历史**（时间序列，关心趋势）——黄金项目把它们分成了 `gold_state.json` 与 `gold_history.json` 两个文件，这个划分值得学习。

### 1.4 记忆的三个基本操作

| 操作 | 说明 | 的例子 |
| --- | --- | --- |
| 写入（Write） | 把新信息加入记忆 | `history.add_user_message("在吗？")` |
| 读取（Read） | 取出记忆拼进 prompt | `history.messages` 回传给模型 |
| 遗忘（Forget） | 裁剪或压缩以控制长度 | `history[-max_history_len:]`、`history[-500:]` |

「遗忘」是初学者最容易忽略的一环，但它是记忆系统能否长期运行的决定因素——详见 2.4 与 2.5。

---

## 2. 关键机制

### 2.1 会话记忆：ChatMessageHistory

给出的最小示例：

```python
"""会话记忆的序列化与恢复（复刻 LangChain messages_to_dict 的结构）。

依赖：仅标准库。
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class BaseMessage:
    content: str
    additional_kwargs: Dict = field(default_factory=dict)
    type: str = "base"

    def to_dict(self):
        return {"type": self.type, "data": {"content": self.content,
    "additional_kwargs": self.additional_kwargs}}

    @dataclass
    class HumanMessage(BaseMessage):
        type: str = "human"

        @dataclass
        class AIMessage(BaseMessage):
            type: str = "ai"

            MESSAGE_CLASSES = {"human": HumanMessage, "ai": AIMessage}

            def messages_to_dict(messages: List[BaseMessage]) -> List[dict]:
                return [message.to_dict() for message in messages]

            def messages_from_dict(dicts: List[dict]) -> List[BaseMessage]:
                messages = []
                for item in dicts:
                    cls = MESSAGE_CLASSES.get(item["type"])
                    if cls is None:
                        raise ValueError("未知消息类型: %s" % item["type"])
                    messages.append(cls(content=item["data"]["content"],
                    additional_kwargs=item["data"].get("additional_kwargs", {})))
                    return messages

                class ChatMessageHistory:
                    """最小会话记忆容器"""

                    def __init__(self):
                        self.messages: List[BaseMessage] = []

                        def add_user_message(self, content):
                            self.messages.append(HumanMessage(content=content))

                            def add_ai_message(self, content):
                                self.messages.append(AIMessage(content=content))

                                def to_json(self):
                                    return json.dumps(messages_to_dict(self.messages), ensure_ascii=False)

                                @classmethod
                                def from_json(cls, payload):
                                    history = cls()
                                    history.messages = messages_from_dict(json.loads(payload))
                                    return history

                                if __name__ == "__main__":
                                    history = ChatMessageHistory()
                                    history.add_user_message("小明有1只猫")
                                    history.add_ai_message("小明有一只猫，那这只猫叫什么名字呢？")
                                    history.add_user_message("小刚有2只狗")

                                    payload = history.to_json()
                                    print("序列化结果:")
                                    print(payload)

                                    restored = ChatMessageHistory.from_json(payload)
                                    print("恢复后的消息条数:", len(restored.messages))
                                    for message in restored.messages:
                                        print("[%s] %s" % (message.type, message.content))
```

它的价值在于**把「维护一个 messages 列表」这件事变成有语义的 API**，并且维护了消息类型信息，方便直接回传给 Chat Models。

### 2.2 长期记忆：消息序列化

要把会话历史真正存下来（文件、Redis、数据库），不能直接存 Python 对象，需要先转成字典：

| 函数 | 方向 | 输入 | 输出 |
| --- | --- | --- | --- |
| `messages_to_dict(history.messages)` | 序列化 | 消息对象列表 | 可 JSON 化的 dict 列表 |
| `messages_from_dict(dicts)` | 反序列化 | dict 列表 | 消息对象列表 |

打印出的中间结构：

```text
[{'type': 'human', 'data': {'content': 'hi!', 'additional_kwargs': {}}},
 {'type': 'ai', 'data': {'content': 'whats up?', 'additional_kwargs': {}}}]
```

关键设计是 **`type` 与 `data` 分离**：`type` 决定反序列化时构造哪个消息类，`data` 承载内容。这保证了「存下来 → 读回来仍然是 `HumanMessage` / `AIMessage`」，而不是丢成纯文本。

### 2.3 ConversationChain：自动回传历史

用 `ConversationChain` 演示了记忆的自动化：

```text
llm = Ollama(model="qwen2.5:7b")
conversation = ConversationChain(llm=llm)
conversation.predict(input="小明有1只猫")
conversation.predict(input="小刚有2只狗")
conversation.predict(input="小明和小刚一共有几只宠物?")
# → 小明和小刚总共有3只宠物。小明有1只猫，小刚有2只狗。
```

第三轮能答对，说明 `ConversationChain` 在内部维护了一份 Memory，并在每次 `predict` 时把历史自动注入 prompt。对照 [03](03-LangChain与工具编排.md) 的 `conversational-react-description` 代理类型——后者正是「ReAct + 记忆」的组合，用于多轮对话中调用工具。

### 2.4 历史拼接与窗口截断（GPT2 医疗问诊机器人）

这套实现比 LangChain 更底层，能看清「记忆」的物理形态。**输入构造**（`interact.py`）：

```python
"""滑动窗口历史 + 状态记忆的最小实现（对应 gold_state.json / gold_history.json）。

依赖：仅标准库。
"""

import json
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "agent_state.json")
HISTORY_FILE = os.path.join(BASE_DIR, "agent_history.json")

MAX_HISTORY = 500 # 历史记忆上限（滑动窗口）
NOTIFY_INTERVAL = 3600 # 同类提醒最小间隔（秒）

def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, ValueError):
        return default

    def save_json(path, payload):
        with open(path, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)

            def load_state():
                return load_json(STATE_FILE, {"last_price": None, "last_status": "normal", "last_notify_time": 0})

            def save_state(state):
                save_json(STATE_FILE, state)

                def append_history(price):
                    """写入历史记忆，并做滑动窗口截断"""
                    history = load_json(HISTORY_FILE, [])
                    history.append({"time": time.strftime("%Y-%m-%d %H:%M:%S"), "price": price})
                    history = history[-MAX_HISTORY:] # 遗忘：只保留最近 500 条
                    save_json(HISTORY_FILE, history)
                    return history

                def get_price_change(current, last):
                    if not last:
                        return 0.0
                    return (current - last) / last * 100

                def decide_and_notify(price, buy_threshold=800, sell_threshold=900, now=None, notifier=print):
                    """决策：状态变化立即提醒；状态未变则按间隔限流提醒。"""
                    now = now if now is not None else time.time()
                    state = load_state()
                    change = get_price_change(price, state.get("last_price"))

                    if price < buy_threshold:
                        status, title = "buy", "黄金买入提醒"
                    elif price > sell_threshold:
                        status, title = "sell", "黄金卖出提醒"
                    else:
                        status, title = "normal", None

                        should_notify = False
                        if status != state.get("last_status") and title:
                            should_notify = True # 状态变化 → 立即提醒
                        elif title and now - state.get("last_notify_time", 0) > NOTIFY_INTERVAL:
                            should_notify = True # 状态未变但超时 → 周期提醒

                            if should_notify:
                                notifier("%s 当前价格 %.2f 元/克，相比上次 %.2f%%" % (title, price, change))
                                state["last_notify_time"] = now

                                state["last_price"] = price
                                state["last_status"] = status
                                save_state(state)
                                append_history(price)
                                return status, should_notify

                            if __name__ == "__main__":
                                print(decide_and_notify(780.0)) # 低于买入阈值 → 提醒
                                print(decide_and_notify(785.0)) # 状态仍为 buy 且未超时 → 不提醒
                                print(decide_and_notify(910.0)) # 状态变化 → 提醒
                                print("历史条数:", len(load_json(HISTORY_FILE, [])))
```

对应数据侧（`preprocess.py`）的拼接格式：

```text
[CLS] utterance1 [SEP] utterance2 [SEP] utterance3 [SEP]
```

三个设计要点：

| 要点 | 做法 | 作用 |
| --- | --- | --- |
| 轮次边界 | 每轮以 `[SEP]` 结尾 | 让模型区分「谁说的、说到哪了」 |
| 序列起点 | 以 `[CLS]` 开头 | 复用 BERT 风格的 tokenizer 约定，作为序列起始标志 |
| 长度控制 | `history[-max_history_len:]` | 滑动窗口，只保留最近 N 轮，防止序列无限增长 |
| 生成终止 | 生成到 `[SEP]` 即停 | `[SEP]` 同时充当「回复结束」标志 |

写入侧则是每轮结束后 `history.append(response)`，与用户输入 `history.append(text_ids)` 配对——**一问一答成对入栈**，模型下一轮就能同时看到上下文与自己的历史回答。

另外两个细节属于「记忆质量控制」：

- **重复惩罚**：`for id in set(response): next_token_logits[id] /= repetition_penalty`——对已生成的 token 降权，避免复读；
- **屏蔽 `[UNK]`**：`next_token_logits[unk_id] = -float('Inf')`，防止输出未知词，保证回复可读。

### 2.5 状态记忆与历史记忆的分离（黄金价格监控项目）

这个项目把「记忆」落成了两个 JSON 文件，是工程上非常典型的划分：

**`gold_state.json`（状态记忆：只关心最新值）**

```json
{
 "last_price": 888.71,
 "last_status": "normal",
 "last_notify_time": 0
}
```

| 字段 | 用途 | 为什么必须持久化 |
| --- | --- | --- |
| `last_price` | 计算相比上次的涨跌幅 `(current - last) / last * 100` | 进程重启后仍能算出变化率 |
| `last_status` | `normal` / `buy` / `sell`，用于判断状态是否变化 | 实现「状态变化才提醒」 |
| `last_notify_time` | 上次提醒的时间戳 | 实现提醒间隔限流，避免每分钟骚扰 |

`monitor_gold()` 里的判定逻辑正好对应这三个字段：

```python
if status != state.get("last_status"): # 状态变化 → 立即提醒
 send_wechat_message(...)
elif title and now - state.get("last_notify_time", 0) > notify_interval: # 状态未变但超时 → 周期提醒
 send_wechat_message(...)
else:
 print("状态未变化，无需重复提醒")
```

这就是「防重复提醒」的实现方式：**把决策所需的全部上下文写进状态文件**，而不是靠进程内变量。

**`gold_history.json`（历史记忆：关心趋势）**

```json
[
 {"time": "2026-07-08 23:40:48", "price": 888.71},
 {"time": "2026-07-08 23:44:11", "price": 888.71}
]
```

它是趋势分析（`ai_analysis.py` 取最近 12 条）、日报（按日期前缀过滤当天记录）与 Web 走势图的数据源。写入时做截断：

| 位置 | 截断策略 | 含义 |
| --- | --- | --- |
| `check_price_once()` | `history = history[-500:]` | 只保留最近 500 条 |
| `save_gold_history()` | `history = history[-20000:]` | 只保留最近 20000 条（注释说「只保存最近 90 天以内的数据量」） |

**这是一个真实存在的坑**：同一份数据在两条代码路径上有两种截断阈值，且一条用相对路径 `"gold_history.json"`、另一条用绝对路径 `HISTORY_FILE = os.path.join(os.path.dirname(__file__), "gold_history.json")`——如果工作目录不同，会写出两个不同的文件。详见第 4 节与 [08-实战-黄金价格监控Agent项目复盘](../05-前沿与面试/08-实战-黄金价格监控Agent项目复盘.md)。

### 2.6 外部知识记忆：向量库 + 父块压缩

RAG 系统里的记忆属于「体量远超上下文窗口」的那一类，因此不能整段回传，必须**按需检索**。它的压缩技巧是**父子块结构**（详见 [06](06-RAG作为Agent的知识获取手段.md)）：

| 存储内容 | 存哪里 | 检索用途 |
| --- | --- | --- |
| 子块（小，如 300 字） | Milvus 的 `text` 字段 + 向量 | 命中查询，精度高 |
| 父块内容（大） | Milvus 的 `parent_content` 字段（作为元数据冗余存储） | 命中后替换成完整上下文，给模型足够的语义 |

`_get_unique_parent_docs()` 的做法是：先用子块检索，再取 `parent_content` 并**按内容去重**，最后交给重排器打分。等价于「用小子块当索引，用大父块当记忆」——这是上下文预算与语义完整性之间的经典折中。

### 2.7 上下文预算管理

> **说明**：本小节超出本节范围，为通用知识补充。

三种主流策略（只覆盖了第一种）：

| 策略 | 做法 | 优点 | 风险 |
| --- | --- | --- | --- |
| **滑动窗口** | 只保留最近 K 轮（ `[-max_history_len:]`、`[-500:]` 即此） | 实现简单、成本可预估 | 早期关键信息被丢弃 |
| **摘要压缩** | 用 LLM 把旧对话压成摘要再接在最新几轮前 | 保留长期信息、token 可控 | 摘要失真、额外调用成本 |
| **向量召回** | 把历史存向量库，按当前问题检索相关片段 | 可扩展到极长历史 | 检索质量依赖 embedding 与切分 |

实践中的组合拳是：**最近 3–5 轮原文 + 更早历史的摘要 + 按需召回的相关片段**，再给总 token 设一个硬上限。

---

## 3. 可运行示例

### 3.1 会话记忆的序列化与恢复

下面的例子用纯标准库复刻 `messages_to_dict` / `messages_from_dict` 的结构，演示「存下来 → 读回来」的完整链路。**依赖：仅标准库。**

预期输出（要点）：

```text
序列化结果:
[{"type": "human", "data": {"content": "小明有1只猫", "additional_kwargs": {}}}, ...]
恢复后的消息条数: 3
[human] 小明有1只猫
[ai] 小明有一只猫，那这只猫叫什么名字呢？
[human] 小刚有2只狗
```

### 3.2 滑动窗口历史 + 状态文件（对应黄金监控项目的记忆设计）

**依赖**：仅标准库。

这段代码把与项目里的记忆机制压成一个可直接运行的闭环：**状态文件承载「决策所需的最新事实」，历史文件承载「趋势分析所需的时间序列」，滑动窗口负责遗忘**。

---

## 4. 常见坑

| 现象 | 原因 | 解决 |
| --- | --- | --- |
| 多轮对话「失忆」 | 只传了当前一轮 user 消息，历史没回传 | 维护 `messages` 列表并每轮整体回传；或使用 `ConversationChain` / Memory 组件 |
| 会话历史存了却读不回来（变成纯文本） | 存的时候只存了 `content`，丢了消息 `type` | 用 `messages_to_dict` / `messages_from_dict`，保留 `type` + `data` 结构 |
| 提示长度超限 / 成本失控 | 历史无限增长，没有遗忘机制 | 滑动窗口截断（`[-max_history_len:]`）、摘要压缩或向量召回 |
| 重启程序后「重复提醒」轰炸 | 状态只存在内存变量里，重启即丢 | 把 `last_status` / `last_notify_time` 落盘（如 `gold_state.json`） |
| 历史数据出现两份、趋势图混乱 | 同一份数据用不同路径与不同阈值写入（黄金项目即此情况：相对路径 `history_file` vs 绝对路径 `HISTORY_FILE`，`[-500:]` vs `[-20000:]`） | 统一为单一常量路径与单一截断阈值，所有写入走同一个函数 |
| 早期关键信息被窗口挤掉 | 滑动窗口只保留最近 N 轮 | 对窗口外的历史做摘要或存入向量库，按需召回 |
| RAG 检索回来的上下文太碎、模型答不完整 | 只用了小子块，缺少完整语义 | 采用父子块结构，命中子块后用 `parent_content` 替换（见 [06](06-RAG作为Agent的知识获取手段.md)） |
| 模型把 `[UNK]` 或重复词吐出来 | 生成阶段缺少约束 | 屏蔽 `[UNK]` 的 logits，对已生成 token 施加重复惩罚 |
| 记忆里的敏感信息被持久化 | 状态/历史文件明写用户数据 | 入盘前脱敏；对文件权限与加密做控制 |

---

## 5. 面试问答

<details><summary>参考答案</summary>

**Q1：大模型本身没有记忆，那 ChatGPT 是怎么「记住」上下文的？**

靠封装层的回传。每次请求都把之前的对话历史（用户消息与模型回答）重新拼进本次的 prompt 一起发送，模型看到的是「完整对话文本」，因此表现得像记得。这带来两个工程约束：一是历史越长 token 成本越高、延迟越大；二是模型上下文窗口有限，超出就必须裁剪、摘要或改用检索方式召回。所以「记忆」在工程上是一套读写与遗忘机制，而不是模型的能力。

</details>

<details><summary>参考答案</summary>

**Q2：短期记忆和长期记忆在实现上有什么不同？各举一个的例子。**

短期记忆指单一会话中传递的数据，实现上就是一份随请求回传的 `messages` 列表或 token id 列表，进程结束即丢失——GPT2 医疗问诊机器人用 `history` 列表保存每轮的 token id，并只取 `history[-max_history_len:]` 拼进输入，就是典型实现；LangChain 的 `ChatMessageHistory` 是同一思路的组件化封装。长期记忆指跨多个会话获取和更新的信息，必须落到进程之外，例如黄金监控项目的 `gold_state.json`（保存 `last_price` / `last_status` / `last_notify_time`，实现重启后仍能判断「是否需要提醒」）、`gold_history.json`（保存历史价格序列，用于趋势分析与日报），以及 RAG 系统的 Milvus 向量库（保存文档向量，供跨会话检索）。核心区别是：短期记忆是「回传」，长期记忆是「持久化 + 按需读取」。

</details>

<details><summary>参考答案</summary>

**Q3：为什么 `gold_state.json` 里需要 `last_notify_time` 而不只是 `last_status`？**

因为 `last_status` 只能回答「状态变了没有」，不能回答「该不该再提醒一次」。如果用户长期处于 `buy` 状态（价格持续低于买入线），只靠状态变化判断就会一直沉默；如果改成每轮都提醒，又会在检查间隔只有几秒时疯狂轰炸。`last_notify_time` 提供了第二个维度：状态未变化时可以按 `notify_interval_seconds`（默认 3600 秒）做周期提醒限流。二者组合出代码里的两段式判定——状态变化立即提醒、否则超时提醒、都不满足则跳过。本质上是把「一次决策所需的全部上下文」都持久化，使提醒行为与进程生命周期解耦。

</details>

---

## 6. 自测题

<details><summary>参考答案</summary>

**1. 这里把 Memory 分为哪两类？各自定义是什么？**

短期记忆：一般指单一会话时传递数据。长期记忆：处理多个会话时获取和更新信息。

</details>

<details><summary>参考答案</summary>

**2. `messages_to_dict` 输出里 `type` 与 `data` 各自的作用是什么？**

`type` 标识消息角色（如 `human` / `ai`），反序列化时据此决定构造哪个消息类；`data` 承载 `content` 与 `additional_kwargs` 等实际内容。二者分离才能保证「存下来、读回来」之后仍然是带类型语义的消息对象，而不是退化为纯文本。

</details>

<details><summary>参考答案</summary>

**3. GPT2 医疗问诊机器人的输入为什么要在每轮结尾加 `[SEP]`，并在最前面加 `[CLS]`？**

`[SEP]` 用来标记每一轮 utterance 的边界，使模型能区分多轮对话中「谁说到哪里」；生成阶段 `[SEP]` 又充当回复结束标志，模型吐出 `[SEP]` 即停止。`[CLS]` 作为整个输入序列的起点标志，与 tokenizer 的约定一致，为模型提供统一的序列起始信号。这是「记忆载体」的设计要点：边界标记让拼接后的长文本仍然可解析。

</details>

<details><summary>参考答案</summary>

**4. 黄金监控项目里，历史截断出现了 `history[-500:]` 与 `history[-20000:]` 两种写法，这会带来什么问题？**

同一份历史数据存在两条写入路径，截断阈值不一致：一条最多保留 500 条，另一条最多保留 20000 条，取决于哪条路径最后写入，历史长度会在两个上限之间反复跳变。更严重的是两条路径使用了不同的文件路径（相对路径 `"gold_history.json"` 与基于 `__file__` 的绝对路径），如果运行工作目录不同，会写出两个不同的文件，导致日报/趋势图读到的数据与实际记录不一致。修法是统一路径常量与截断阈值，并把写入收敛到唯一函数。

</details>

<details><summary>参考答案</summary>

**5. 除了滑动窗口，还有哪些控制记忆长度的方式？各自的代价是什么？**

摘要压缩：用 LLM 把较早的对话压成摘要，保留长期信息且 token 可控，代价是摘要可能失真，并增加一次额外调用；向量召回：把历史存向量库按需检索相关片段，可扩展到极长历史，代价是依赖 embedding 与切分质量，可能召回不到关键信息；结构化状态：只保留决策必需的字段（如黄金项目的 `last_price` / `last_status`），token 最省，但只适用于能事先确定「需要记住什么」的场景。实践中常组合使用：最近几轮原文 + 更早历史的摘要 + 按需召回 + 硬性 token 上限。

</details>

---

## 7. 延伸阅读

- LangChain Memory 组件文档 —— https://python.langchain.com/docs/how_to/#memory
- LangChain 消息与 `messages_to_dict` 接口 —— https://python.langchain.com/api_reference/core/messages.html
- MemGPT: Towards LLMs as Operating Systems（分层记忆管理） —— https://arxiv.org/abs/2310.08560
- Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks —— https://arxiv.org/abs/2005.11401
- ：《第五章：物流问答系统（RAG）_01-LangChain 基础知识入门》《第六章：基于 GPT2 搭建医疗问诊机器人》
- 项目源码：黄金价格监控 Agent（`gold_state.json` / `gold_history.json` 的状态与历史分离设计）

---

[⬅️ 返回本目录索引](README.md)
