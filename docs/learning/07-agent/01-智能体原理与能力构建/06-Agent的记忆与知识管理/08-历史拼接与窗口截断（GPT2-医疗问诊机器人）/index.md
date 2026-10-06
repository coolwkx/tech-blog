---
article_id: kp-53db6126c17f3b3f
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-3dbf2b7f4206
learning_sourceId: 3dbf2b7f4206
learning_order: 7
learning_objective: 理解并验证：历史拼接与窗口截断（GPT2 医疗问诊机器人）
---

# 历史拼接与窗口截断（GPT2 医疗问诊机器人）

> **学习目标**：能够解释「历史拼接与窗口截断（GPT2 医疗问诊机器人）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[03-LangChain与工具编排](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md) 的 Memory 组件、[06-RAG作为Agent的知识获取手段](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md) 的向量检索、[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的 messages 角色约定。
>
> **所属主题**：-Agent的记忆与知识管理 · 关键机制

## 本次只学这一点

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
                        status, title = "buy", "大宗商品买入提醒"
                    elif price > sell_threshold:
                        status, title = "sell", "大宗商品卖出提醒"
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

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「历史拼接与窗口截断（GPT2 医疗问诊机器人）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md)
