---
article_id: kp-d703482027b5f702
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-21a1347a1b81
learning_sourceId: 21a1347a1b81
learning_order: 7
learning_objective: 理解并验证：状态持久化
---

# 状态持久化

> **学习目标**：能够解释「状态持久化」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python `requests` 会话与超时、Web API 返回格式的解析技巧、简单的状态机与去重通知思想、Flask 路由与模板、`json` 文件持久化。
>
> **所属主题**：项目实战笔记 04：大宗商品价格监控 Agent · 核心实现

## 本次只学这一点

```text
STATE_FILE = os.path.join(os.path.dirname(__file__), "commodity_state.json")

def load_state:
 try:
 with open(STATE_FILE, "r", encoding="utf-8") as f:
 return json.load(f)
 except: # 文件不存在 / 内容损坏 → 用默认值
 return {"last_price": None, "last_status": "normal", "last_notify_time": 0}

def save_state(state):
 with open(STATE_FILE, "w", encoding="utf-8") as f:
 json.dump(state, f, ensure_ascii=False, indent=2)
```

```json
{ "last_price": 888.71, "last_status": "normal", "last_notify_time": 0 }
```

**为什么 `last_notify_time` 初始为 0**：`now - 0 > notify_interval` 恒成立，所以首次进入 buy/sell 状态时一定会触发通知（走的是"状态变化"分支，其实不影响）。这个默认值的选择让逻辑在任何状态下都不会"卡住不发"。

**为什么用 `except:` 宽异常**：状态文件是"可重建的派生数据"，读不到就从零开始，不应该因此让监控进程起不来。**但要区分清楚**：这是"缓存可丢"的场景；如果是用户的购买记录，就绝不能用裸 `except` 静默吞掉。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/04-Agent系统/04-项目-大宗商品价格监控Agent.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「状态持久化」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/04-Agent系统/04-项目-大宗商品价格监控Agent.md)
