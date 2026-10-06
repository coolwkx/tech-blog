---
article_id: kp-37686ea2f072c491
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-3dbf2b7f4206
learning_sourceId: 3dbf2b7f4206
learning_order: 4
learning_objective: 理解并验证：会话记忆：ChatMessageHistory
---

# 会话记忆：ChatMessageHistory

> **学习目标**：能够解释「会话记忆：ChatMessageHistory」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[03-LangChain与工具编排](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md) 的 Memory 组件、[06-RAG作为Agent的知识获取手段](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md) 的向量检索、[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的 messages 角色约定。
>
> **所属主题**：-Agent的记忆与知识管理 · 关键机制

## 本次只学这一点

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

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「会话记忆：ChatMessageHistory」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md)
