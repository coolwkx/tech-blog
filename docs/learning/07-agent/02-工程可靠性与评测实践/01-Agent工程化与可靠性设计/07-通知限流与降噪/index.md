---
article_id: kp-853139e41103273b
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-0ae5654d8e63
learning_sourceId: 0ae5654d8e63
learning_order: 6
learning_objective: 理解并验证：通知限流与降噪
---

# 通知限流与降噪

> **学习目标**：能够解释「通知限流与降噪」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的工具协议与错误处理、[05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的状态持久化、[08-大宗商品价格监控Agent项目复盘](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md)。
>
> **所属主题**：-Agent工程化与可靠性设计 · 关键机制

## 本次只学这一点

`monitor_gold()` 的双条件判定是「降噪」的标准范式：

```text
"""工具包装器：统一超时、重试、异常转结构化 Observation、调用统计。

依赖：仅标准库。
"""

import functools
import json
import logging
import time

logger = logging.getLogger("tool")

class ToolError(Exception):
 """工具级错误，会被包装成可读 Observation 返回给模型"""

def resilient_tool(max_retry=2, timeout_hint=10, retry_on=(ToolError,)):
 """装饰器：失败重试；最终失败时返回 {"error": ...} 而不是抛异常。"""

 def decorator(func):
 @functools.wraps(func)
 def wrapper(*args, **kwargs):
 last_error = None
 for attempt in range(1, max_retry + 1):
 started = time.time()
 try:
 result = func(*args, **kwargs)
 logger.info("tool=%s attempt=%d cost=%.3fs ok",
 func.__name__, attempt, time.time() - started)
 return result
 except retry_on as exc:
 last_error = exc
 logger.warning("tool=%s attempt=%d 可重试失败: %s",
 func.__name__, attempt, exc)
 time.sleep(0.5 * attempt)
 except Exception as exc: # 不可重试：立即收敛成 Observation
 last_error = exc
 logger.error("tool=%s 不可重试失败: %s", func.__name__, exc)
 break
 return json.dumps({"error": "%s 执行失败: %s" % (func.__name__, last_error)},
 ensure_ascii=False)

 wrapper.timeout_hint = timeout_hint
 return wrapper

 return decorator

@resilient_tool(max_retry=3)
def query_stock(sku):
 """查询库存（演示：SKU 以 '9' 开头时模拟瞬时故障）"""
 if sku.startswith("9"):
 raise ToolError("库存服务临时不可用")
 database = {"A1001": 12, "A1002": 0}
 if sku not in database:
 raise ValueError("未知 SKU: %s" % sku) # 业务错误，不重试
 return json.dumps({"sku": sku, "stock": database[sku]}, ensure_ascii=False)

if __name__ == "__main__":
 print(query_stock("A1001")) # 正常
 print(query_stock("A9999")) # 业务错误，一次失败即返回 error
 print(query_stock("90001")) # 重试 3 次后返回 error
```

| 条件 | 语义 | 防的是什么 |
| --- | --- | --- |
| A：`status != last_status` | 事件驱动，状态刚变化 | 漏报（该提醒的时候没提醒） |
| B：`now - last_notify_time > notify_interval` | 时间驱动，兜底周期提醒 | 长期停留在同一状态时的信息沉默 |
| 都不满足 | 静默 | 高频轮询下的重复轰炸 |

`config.json` 中 `check_interval_seconds` 为 5、`notify_interval_seconds` 为 3600，正好体现了「检查频率」与「打扰频率」解耦的设计：可以高频检查，但不能高频打扰。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「通知限流与降噪」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md)
