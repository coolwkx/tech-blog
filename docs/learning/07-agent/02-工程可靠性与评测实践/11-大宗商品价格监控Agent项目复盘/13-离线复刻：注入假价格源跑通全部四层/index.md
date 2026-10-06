---
article_id: kp-024138fe86e98cc2
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-4cd0a37cb105
learning_sourceId: 4cd0a37cb105
learning_order: 12
learning_objective: 理解并验证：离线复刻：注入假价格源跑通全部四层
---

# 离线复刻：注入假价格源跑通全部四层

> **学习目标**：能够解释「离线复刻：注入假价格源跑通全部四层」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的五要素、[05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的状态与历史分离、[07-Agent工程化与可靠性设计](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md) 的降级与限流。
>
> **所属主题**：-大宗商品价格监控Agent项目复盘 · 可运行示例

## 本次只学这一点

**依赖**：仅标准库（把网络抓取替换为可注入的价格序列，便于本地验证决策逻辑）。

```text
"""把大宗商品监控的决策层升级为 LLM Agent（保留原有感知/记忆/行动）。

依赖：pip install zhipuai python-dotenv
环境变量：ZHIPU_API_KEY
"""

import json
import os
from zhipuai import ZhipuAI

# 复用 3.1 中的记忆层与行动层：load_state / save_state / append_history / send_wechat_message

SYSTEM_PROMPT = """你是一名大宗商品行情监控助手。
你会收到当前价格、近期价格序列、用户的买入/卖出参考阈值，以及上一轮的判断状态。
请判断本轮应该处于哪种状态（normal / buy / sell），并给出不超过 80 字的分析。
必须基于给定的数据，不得编造未提供的行情信息。
只输出 JSON，格式为：
{"status": "normal|buy|sell", "reason": "简短分析", "suggest_notify": true|false}
"""

def build_user_prompt(price, history, config, last_status):
 recent = [item["price"] for item in history[-12:]]
 return json.dumps({
 "current_price": price,
 "recent_prices": recent,
 "buy_threshold": config["buy_threshold"],
 "sell_threshold": config["sell_threshold"],
 "last_status": last_status,
 "note": "阈值仅为参考线，若价格只是轻微越过阈值且近期无趋势，可建议不通知。",
 }, ensure_ascii=False)

def llm_decide(price, history, config, last_status, model="glm-4"):
 client = ZhipuAI(api_key=os.environ["ZHIPU_API_KEY"])
 messages = [
 {"role": "system", "content": SYSTEM_PROMPT},
 {"role": "user", "content": build_user_prompt(price, history, config, last_status)},
 ]
 try:
 response = client.chat.completions.create(
 model=model, messages=messages, temperature=0.1,
 response_format={"type": "json_object"},
 )
 payload = json.loads(response.choices[0].message.content)
 status = payload.get("status")
 if status not in ("normal", "buy", "sell"):
 raise ValueError("非法状态: %s" % status)
 return status, payload.get("reason", ""), bool(payload.get("suggest_notify", False))
 except Exception as exc: # 模型侧失败 → 回退到规则决策，保证系统可用
 print("LLM 决策失败，回退到规则决策: %s" % exc)
 return rule_fallback(price, config)

def rule_fallback(price, config):
 if price < config["buy_threshold"]:
 return "buy", "价格低于买入参考价（规则兜底）", True
 if price > config["sell_threshold"]:
 return "sell", "价格高于卖出参考价（规则兜底）", True
 return "normal", "价格处于正常区间（规则兜底）", False
```

预期输出（要点）：

```text
=== 价格 880.00 ===
状态未变化，无需重复提醒
=== 价格 795.00 ===
[推送] 🟡 大宗商品买入提醒
=== 价格 790.00 ===
状态未变化，无需重复提醒 # 状态仍是 buy，未到 notify_interval，不重复推送
=== 价格 912.00 ===
[推送] 🔴 大宗商品卖出提醒 # 状态变化，立即推送
```

第三轮不推送正是「防重复提醒」生效的证据。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「离线复刻：注入假价格源跑通全部四层」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md)
