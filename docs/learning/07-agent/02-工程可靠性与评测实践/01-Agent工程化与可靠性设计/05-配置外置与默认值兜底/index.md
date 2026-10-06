---
article_id: kp-d8a0aa188efc5e96
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-0ae5654d8e63
learning_sourceId: 0ae5654d8e63
learning_order: 4
learning_objective: 理解并验证：配置外置与默认值兜底
---

# 配置外置与默认值兜底

> **学习目标**：能够解释「配置外置与默认值兜底」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的工具协议与错误处理、[05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的状态持久化、[08-大宗商品价格监控Agent项目复盘](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md)。
>
> **所属主题**：-Agent工程化与可靠性设计 · 关键机制

## 本次只学这一点

`load_config()` 的双层设计：

```text
"""可靠的外部数据获取封装：多源降级 → 校验 → 退避重试 → 结构化日志。

依赖：仅标准库。
"""

import json
import logging
import random
import time
import urllib.error
import urllib.request

logging.basicConfig(
 level=logging.INFO,
 format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("price_fetcher")

MIN_VALID_PRICE = 200.0 # 低于该值视为解析异常
MAX_RETRY = 3
TIMEOUT = 15

def _parse_sina(text):
 parts = text.split(",")
 if len(parts) <= 3:
 raise ValueError("字段不足: %d" % len(parts))
 return float(parts[3])

def _parse_json_price(text):
 payload = json.loads(text)
 if not payload.get("success"):
 raise ValueError("接口返回 success=false")
 return float(payload["price"])

SOURCES = [
 {"name": "工银积存金-最新价", "url": "http://106.54.190.155:886/get_latest_price.php",
 "parser": _parse_json_price},
 {"name": "新浪财经-AU9999", "url": "http://hq.sinajs.cn/list=AU9999", "parser": _parse_sina},
]

def fetch_once(source):
 """抓取单个数据源，失败抛异常由上层处理"""
 request = urllib.request.Request(
 source["url"],
 headers={
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
 "Referer": "https://finance.sina.com.cn/",
 },
 )
 with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
 if response.status != 200:
 raise ValueError("HTTP 状态码 %d" % response.status)
 text = response.read().decode("utf-8", errors="ignore").strip()
 if not text or text.endswith('=""'):
 raise ValueError("响应为空")
 price = float(source["parser"](text))
 if price <= 0:
 raise ValueError("价格非正数: %s" % price)
 if price < MIN_VALID_PRICE:
 raise ValueError("价格低于有效阈值 %s: %s" % (MIN_VALID_PRICE, price))
 return price

def fetch_price_with_fallback(sources=None, max_retry=MAX_RETRY):
 """多源降级 + 每个源内部退避重试，全部失败返回 None"""
 sources = sources if sources is not None else SOURCES
 for source in sources:
 for attempt in range(1, max_retry + 1):
 try:
 price = fetch_once(source)
 logger.info("数据源 %s 成功，价格 %.2f", source["name"], price)
 return price
 except (urllib.error.URLError, ValueError, KeyError, json.JSONDecodeError) as exc:
 wait = min(2 ** attempt + random.random(), 10.0) # 指数退避 + 抖动
 logger.warning("数据源 %s 第 %d 次失败: %s（%.1fs 后重试）",
 source["name"], attempt, exc, wait)
 if attempt < max_retry:
 time.sleep(wait)
 logger.error("数据源 %s 重试耗尽，切换到下一个源", source["name"])
 logger.error("所有数据源均失败，本次抓取返回 None")
 return None

if __name__ == "__main__":
 print("最终获取到的价格:", fetch_price_with_fallback())
```

| 层次 | 作用 |
| --- | --- |
| 配置文件 | 运行期可调整（阈值、间隔、推送 Key），不必改代码 |
| 内置默认值 | 配置缺失/损坏时程序仍能启动，不会因一个 JSON 语法错误直接崩掉 |

配套的 `send_wechat_message()` 在 `sc_key` 为空时会打印「警告: 未配置 SCKEY，请在 config.json 中设置」并返回 `False`，而不是抛异常——**配置缺失属于预期内的运行态，不应作为崩溃处理**。

但这里也暴露了一个真实问题：`config.json` 里的 `sc_key` 是明文提交的（`"SCT<YOUR_SENDKEY>"`）。正确做法是把 `config.json` 加入 `.gitignore`，并提供一份 `config.example.json` 只含占位值。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「配置外置与默认值兜底」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md)
