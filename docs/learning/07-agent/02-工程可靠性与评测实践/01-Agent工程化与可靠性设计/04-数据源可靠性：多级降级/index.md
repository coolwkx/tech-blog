---
article_id: kp-2f34ba76302535d1
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-0ae5654d8e63
learning_sourceId: 0ae5654d8e63
learning_order: 3
learning_objective: 理解并验证：数据源可靠性：多级降级
---

# 数据源可靠性：多级降级

> **学习目标**：能够解释「数据源可靠性：多级降级」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的工具协议与错误处理、[05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的状态持久化、[08-大宗商品价格监控Agent项目复盘](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md)。
>
> **所属主题**：-Agent工程化与可靠性设计 · 关键机制

## 本次只学这一点

`get_gold_price()` 里定义了三组数据源，逐级尝试：

| 级别 | 变量 | 数据源 | 解析方式 |
| --- | --- | --- | --- |
| 一级 | `apis` | 工银积存金 API（`get_stats.php`、`get_latest_price.php`）、新浪财经 AU9999 / AU(T+D) / AU100g | JSON 解析 `current_price` / `price`；`hq.sinajs.cn` 按逗号切分取第 4 个字段 |
| 二级 | `alt_apis` | 和讯大宗商品、中金在线、上海大宗商品交易所、Wind 财经、腾讯财经 | 正则提取 `"price":"xx"` 或 JSON 路径 `data.goldprice` |
| 三级 | `more_apis` | 新浪财经大宗商品页面、金融界、同花顺 | 正则匹配「大宗商品现货」「AU9999…价格」附近的数字 |

每一级内部都是同一个模式：

```text
for api in <level>:
 try:
 response = session.get(api["url"])
 if response.status_code != 200: continue # 非 200 直接换下一个
 response.encoding = "utf-8"
 text = response.text.strip()
 if not text or text.endswith('=""'): continue # 空响应（新浪接口的典型形态）
 price = api["parser"](text) # 每个源自带解析器
 if price and price > 0:
 if price < 200: continue # 有效性阈值：剔除明显异常值
 return price
 except Exception as e:
 print("数据源 %s 获取失败: %s" % (api["name"], e))
 continue # 任何异常都不中断整体流程
```

三个设计点值得单独记住：

1. **「解析器」作为数据源的一部分**。每个数据源用 lambda 自带 `parser`，把「怎么取 URL」与「怎么从响应里取数」绑在一起，新增数据源只需往列表里加一项——这是很好的可扩展设计。
2. **有效性校验必须显式写**。`if price < 200: continue` 这一行是在防「解析器抓到了响应里的其它数字」（比如时间戳、成交量）。没有这道校验，一次解析偏差就会触发错误的买卖提醒。
3. **异常必须就地消化**。`except Exception` 里不 raise，只打印并 `continue`，保证「某一个源坏掉」不会让整个监控进程退出。

此外 `session.timeout = 15` 与统一的 `headers`（含 `User-Agent`、`Referer`）也是必要的：前者防挂死，后者是很多财经接口的最低要求。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「数据源可靠性：多级降级」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md)
