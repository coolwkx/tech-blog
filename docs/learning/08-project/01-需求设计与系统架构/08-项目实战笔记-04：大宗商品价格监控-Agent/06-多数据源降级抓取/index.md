---
article_id: kp-8b140b8fe638b36c
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-21a1347a1b81
learning_sourceId: 21a1347a1b81
learning_order: 5
learning_objective: 理解并验证：多数据源降级抓取
---

# 多数据源降级抓取

> **学习目标**：能够解释「多数据源降级抓取」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python `requests` 会话与超时、Web API 返回格式的解析技巧、简单的状态机与去重通知思想、Flask 路由与模板、`json` 文件持久化。
>
> **所属主题**：项目实战笔记 04：大宗商品价格监控 Agent · 核心实现

## 本次只学这一点

```text
# main_monitor.py（精简）
def get_commodity_price:
 headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ... Chrome/120.0.0.0 Safari/537.36",
 "Referer": "https://finance.sina.com.cn/",
 "Accept": "*/*", "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
 "Accept-Encoding": "gzip, deflate", "Connection": "keep-alive",
 }
 session = requests.Session
 session.timeout = 15 # 统一超时，防止某个源把循环卡死
 session.headers.update(headers)

 apis = [
 {"name": "工银积存金 API",
 "url": "http://106.54.190.155:886/api/get_stats.php",
 "parser": lambda t: float(json.loads(t)["current_price"])
 if json.loads(t).get("success") else None},
 {"name": "新浪财经 AU9999",
 "url": "http://hq.sinajs.cn/list=AU9999",
 "parser": lambda t: float(t.split(',')[3]) if len(t.split(',')) > 3 else None},
 # ... AUTD / AU100G / get_latest_price.php ...
 ]

 # 三级数据源，结构完全一致，逐级降级
 for source_group in (apis, alt_apis, more_apis):
 for api in source_group:
 try:
 print("尝试数据源: %s" % api["name"])
 response = session.get(api["url"])
 if response.status_code != 200:
 continue

 response.encoding = "utf-8" # 中文站点必须显式指定编码
 text = response.text.strip()
 if not text or text.endswith('=""'): # 新浪接口无数据时返回空串
 print("响应为空")
 continue

 price = api["parser"](text)
 if price and price > 0:
 # 关键：合理性校验，挡住"抓到了别的数字"
 if price < 200:
 continue
 return price
 else:
 print("解析失败")
 except Exception as e:
 print("数据源 %s 获取失败: %s" % (api["name"], e))
 continue

 print("错误: 所有数据源均失败，无法获取大宗商品价格")
 return None
```

**这段代码里有四个值得单独拿出来讲的设计**：

1. **`session.timeout = 15` 而不是依赖默认值**：`requests` 默认**没有超时**，一个卡住的源会让整个循环永久挂起。定时任务里这是致命问题。
2. **每个源独立 `try/except` 并 `continue`**：一个源的解析异常绝不能中断整轮降级。
3. **`if price < 200: continue`** 这条"魔法数字"校验：不同数据源返回的可能是"元/吨"，也可能是"元/千克"或股票价格（比如 `qt.gtimg.cn/q=sh600019` 返回的是宝钢股份的**股价**，不是钢价！）。用一个数量级下限把明显不合理的值挡掉，是**最便宜的防错手段**。更好的做法是按数据源分别设合理区间，而不是一个全局数字。
4. **`text.endswith('=""')`**：新浪 `hq.sinajs.cn` 在标的无数据时会返回 `var hq_str_AU9999="";`。不判断这一点，`t.split(',')[3]` 会抛 `IndexError`——虽然被 try 接住了，但会白白消耗一次请求。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/04-Agent系统/04-项目-大宗商品价格监控Agent.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「多数据源降级抓取」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/04-Agent系统/04-项目-大宗商品价格监控Agent.md)
