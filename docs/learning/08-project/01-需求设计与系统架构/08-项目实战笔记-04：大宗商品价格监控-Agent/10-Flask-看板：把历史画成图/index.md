---
article_id: kp-430f710f58b36d50
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-21a1347a1b81
learning_sourceId: 21a1347a1b81
learning_order: 9
learning_objective: 理解并验证：Flask 看板：把历史画成图
---

# Flask 看板：把历史画成图

> **学习目标**：能够解释「Flask 看板：把历史画成图」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python `requests` 会话与超时、Web API 返回格式的解析技巧、简单的状态机与去重通知思想、Flask 路由与模板、`json` 文件持久化。
>
> **所属主题**：项目实战笔记 04：大宗商品价格监控 Agent · 核心实现

## 本次只学这一点

```text
# dashboard.py（精简）
@app.route("/")
def index:
 history = load_json(HISTORY_FILE)
 config = load_json(CONFIG_FILE)

 if history:
 recent = history[-50:] # 只看最近 50 个点
 prices = [x["price"] for x in recent]
 current = prices[-1]

 status = ("🔴 高于卖出参考区域" if current > config.get("sell_threshold", 900) else
 "🟢 接近买入参考区域" if current < config.get("buy_threshold", 800) else
 "➡️ 正常波动区间")

 labels = [x["time"][11:16] for x in recent] # 只取 "HH:MM" 做横轴
 values = prices
 else:
 current, status, labels, values, recent = 0, "暂无数据", [], [], []

 return render_template_string(
 HTML,
 price=f"{current:.2f}",
 update=time.strftime("%Y-%m-%d %H:%M:%S"),
 status=status,
 history=reversed(recent[-10:]), # 最近 10 条倒序展示
 labels=json.dumps(labels), # 直接注入 JS 数组
 values=json.dumps(values),
 count=len(values),
 buy=config.get("buy_threshold", 800),
 sell=config.get("sell_threshold", 900),
 )
```

前端用 Chart.js 画三条线：真实价格折线 + 买入参考虚线 + 卖出参考虚线。

```javascript
new Chart(ctx, {
 type:'line',
 data:{
 labels: {{labels|safe}}, // Jinja2 的 safe：不过 HTML 转义
 datasets:[
 { label:'大宗商品价格', data:{{values|safe}}, tension:0.3 },
 { label:'买入参考', data:Array({{count}}).fill({{buy}}), borderDash:[5,5] },
 { label:'卖出参考', data:Array({{count}}).fill({{sell}}), borderDash:[5,5] }
 ]
 }
});
```

**`{{labels|safe}}` 是必需的**：`json.dumps([...])` 产出的是 `["09:30", "09:35"]` 这样的 JS 数组字面量。如果用 Jinja2 默认的转义，引号会变成 `&quot;`，JS 语法直接报错。这也是"把 JSON 注入模板"时的标准坑——**要么用 `|safe`，要么改用 `tojson` 过滤器**（后者更安全，会额外处理 `</script>` 注入）。

**用 `Array(count).fill(buy)` 画参考线**：Chart.js 要求每条 dataset 的数据长度与 labels 一致，无法直接给一个标量。用 `fill` 生成一个常数序列是最简做法。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/04-Agent系统/04-项目-大宗商品价格监控Agent.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Flask 看板：把历史画成图」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/04-Agent系统/04-项目-大宗商品价格监控Agent.md)
