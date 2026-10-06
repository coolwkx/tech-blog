---
article_id: kp-f5e0434385b087ec
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-c24a4924b596
learning_sourceId: c24a4924b596
learning_order: 12
learning_objective: 理解并验证：Flask 服务：注意重资源只加载一次
---

# Flask 服务：注意重资源只加载一次

> **学习目标**：能够解释「Flask 服务：注意重资源只加载一次」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：因果语言模型与 `GPT2LMHeadModel`、多轮对话的上下文拼接、采样解码（temperature / top-k / top-p / repetition penalty）、Flask 模板渲染。
>
> **所属主题**：项目实战笔记 03：企业客服聊天机器人 · 核心实现

## 本次只学这一点

```python
# flask_predict.py（模块级，不在请求函数内）
pconf = ParameterConfig
device = 'cuda' if torch.cuda.is_available else 'cpu'
tokenizer = BertTokenizerFast(vocab_file=pconf.vocab_path,
sep_token="[SEP]", pad_token="[PAD]", cls_token="[CLS]")
model = GPT2LMHeadModel.from_pretrained('./save_model/epoch97').to(device)
model.eval

def model_predict(text):
    history = [tokenizer.encode(text, add_special_tokens=False)]
    input_ids = [tokenizer.cls_token_id]
    for utr in history[-pconf.max_history_len:]:
        input_ids.extend(utr); input_ids.append(tokenizer.sep_token_id)
        input_ids = torch.tensor(input_ids).long.to(device).unsqueeze(0)
        # ... 同 interact.py 的生成循环 ...
        return "".join(tokenizer.convert_ids_to_tokens(response))
```

```text
# app.py
app = Flask(__name__)

@app.route('/')
def index:
 return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask:
 user_input = request.form['user_input']
 response = model_predict(user_input)
 return render_template('index.html', user_input=user_input, answer=response)

if __name__ == '__main__':
 app.run(debug=True)
```

**两个必须知道的细节**：

- `flask_predict.py` 里的 `model_predict` 每次调用都会新建 `history = []`，所以**Web 端实际上是无状态的单轮对话**——用户在网页上感受不到多轮记忆。真正的多轮能力在 `interact.py` 的 CLI 里（它把 `history` 保存在循环外）。如果要给 Web 加多轮，需要按 `session_id` 在服务端维护 `history` 字典，或用 Redis 存。
- `app.run(debug=True)` 只适合开发。生产环境 `debug=True` 会暴露源码与调试器（Werkzeug 调试控制台可执行任意代码），必须关掉。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/02-对话与生成系统/03-项目-企业客服聊天机器人.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Flask 服务：注意重资源只加载一次」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/02-对话与生成系统/03-项目-企业客服聊天机器人.md)
