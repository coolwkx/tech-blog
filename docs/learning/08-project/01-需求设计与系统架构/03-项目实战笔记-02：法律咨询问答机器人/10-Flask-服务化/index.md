---
article_id: kp-cb7915faa4384fbc
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-3e5bdcfe80e4
learning_sourceId: 3e5bdcfe80e4
learning_order: 10
learning_objective: 理解并验证：Flask 服务化
---

# Flask 服务化

> **学习目标**：能够解释「Flask 服务化」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer Decoder 结构与自注意力、因果语言模型（CLM）的 shift 对齐损失、PyTorch 的 `Dataset / DataLoader / collate_fn`、HuggingFace `transformers` 的 `GPT2LMHeadModel` 与 `BertTokenizerFast`。
>
> **所属主题**：项目实战笔记 02：法律咨询问答机器人 · 核心实现

## 本次只学这一点

```text
# flask_predict.py（精简）
app = Flask(__name__)

@app.route('/', methods=['GET'])
def index:
 return render_template('index.html') # 加载聊天页面

@app.route('/chat', methods=['POST'])
def chat:
 text = request.form['text']
 return model_predict(text) # 内部即 interact.py 的生成循环
```

注意工程细节：**模型必须在模块加载时初始化一次**（`model = GPT2LMHeadModel.from_pretrained(...)` 写在函数外），而不是每次请求都加载——否则每个请求都要读几百 MB 权重，响应时间从毫秒级退化到十秒级。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/02-对话与生成系统/02-项目-法律咨询问答机器人.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Flask 服务化」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/02-对话与生成系统/02-项目-法律咨询问答机器人.md)
