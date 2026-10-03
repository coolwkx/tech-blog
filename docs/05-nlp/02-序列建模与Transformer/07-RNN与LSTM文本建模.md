# RNN 与 LSTM 文本建模

> **一句话总结**：RNN 用「隐藏状态沿时间传递」建模序列，但连乘的梯度让它记不住长依赖——LSTM 用门控和一个近似恒等的细胞状态通道解决了这个问题。
> **前置知识**：第 04 篇词向量与 `nn.Embedding`、第 05 篇文本分类流水线、PyTorch `nn.Module` 与 `Dataset/DataLoader`、链式法则与反向传播。

> 1. 说清 RNN 的四种输入输出结构（N vs N / N vs 1 / 1 vs N / N vs M）及各自的应用场景。
> 2. 写出 LSTM 三个门与细胞状态的公式，并解释门控为什么能缓解梯度消失。
> 3. 用 `nn.RNN` / `nn.LSTM` / `nn.GRU` 搭一个人名（字符级短文本）分类器，并正确对齐张量维度。

## 1. 核心概念

### 1.1 RNN 是什么

循环神经网络（Recurrent Neural Network, RNN）接收一个**序列**作为输入，输出也是一个序列（或它的某种归约）。它擅长处理连续语言文本，典型应用：机器翻译、文本生成、文本分类、摘要生成。

核心思想：**在所有时间步共享同一套权重**，并用一个隐藏状态 $h_t$ 充当「记忆」，把历史信息向后传递。

$$
h_t = \tanh(W_{xh}x_t + W_{hh}h_{t-1} + b_h),\qquad o_t = W_{ho}h_t + b_o
$$

注意在一个时间步内，输出 $h_t$ 与 $o_t$ 的数值相同（$o_t$ 是 $h_t$ 的线性变换），工程实现里通常只暴露 $h_t$。

### 1.2 按输入输出结构分类

| 结构 | 输入 | 输出 | 典型应用 |
|------|------|------|----------|
| N vs N | 长度 $N$ 的序列 | 等长序列 | 对联生成、词性标注、NER |
| N vs 1 | 长度 $N$ 的序列 | 单个值 | 文本分类、情感分析、人名国别分类 |
| 1 vs N | 单个输入 | 长度 $N$ 的序列 | 图片描述生成（image captioning） |
| N vs M | 长度 $N$ 的序列 | 长度 $M$ 的序列 | 机器翻译、文本摘要（seq2seq） |

记忆方法：看「输入和输出哪个是单值」。**N vs 1 只需要最后一个时间步的输出**；**N vs M 需要编码器-解码器（seq2seq）结构**。

### 1.3 按内部结构分类

| 结构 | 说明 |
|------|------|
| 传统 RNN | 单门控（只有 tanh），结构最简单 |
| LSTM | 三个门 + 细胞状态，能记住长依赖 |
| Bi-LSTM | 不改变 LSTM 内部结构，把文本从左到右、从右到左各算一遍，输出拼接 |
| GRU | 两个门（更新门、重置门），参数约为 LSTM 的 2/3 |
| Bi-GRU | GRU 的双向版本 |

双向的道理很直白：语言理解需要左右两侧的上下文。"他**打开**了**门**」里判断「打开」的宾语要看右边。单向 RNN 在时刻 $t$ 只能看到 $x_1\dots x_t$，Bi-LSTM 把反向序列的输出拼到正向输出上，使每个位置同时获得左右信息。**代价是双向结构不能用于自回归生成**——生成时未来的 token 还不存在。

### 1.4 传统 RNN 的优缺点

| 优点 | 缺点 |
|------|------|
| 内部结构简单，资源消耗小 | 处理长序列时反向传播要连乘梯度，权重过大或过小都会导致**梯度爆炸或梯度消失** |
| 参数量与序列长度无关（权重共享） | 无法并行（时间步必须串行） |
| 天然能处理变长输入 | 长距离依赖实际学不好（信息被反复覆盖） |

### 1.5 LSTM 的设计动机

梯度问题的数学根源：反向传播时，梯度要沿时间步连乘

$$
\frac{\partial h_t}{\partial h_{t-1}} = W_{hh}^\top \operatorname{diag}\big(1-\tanh^2(\cdot)\big)
$$

连乘 $T$ 次后，若 $W_{hh}$ 的谱半径小于 1，梯度按指数衰减（消失）；大于 1 则指数增长（爆炸）。tanh 的导数最大为 1，也在持续衰减。

LSTM（Long Short-Term Memory, 1997）的思路是：**开一条几乎恒等的「高速公路」让梯度直通**，并用门控决定「写什么、忘什么、读什么」。这条通道就是细胞状态 $c_t$。

## 2. 方法细节

### 2.1 LSTM 的四个组成部分

| 组件 | 作用 | 一句话记忆 |
|------|------|-----------|
| 遗忘门 $f_t$ | 决定从细胞状态中**丢弃**多少旧信息 | 「忘掉多少过去」 |
| 输入门 $i_t$ | 决定**写入**多少新信息 | 「记住多少现在」 |
| 细胞状态 $c_t$ | 沿时间传递的主干记忆 | 「长期记忆」 |
| 输出门 $o_t$ | 决定**暴露**多少细胞状态作为隐状态 | 「说出多少」 |

### 2.2 完整公式

设 $x_t$ 是当前输入，$h_{t-1}$ 是上一时刻隐状态，$[h_{t-1}, x_t]$ 表示拼接：

$$
\begin{aligned}
f_t &= \sigma\big(W_f \cdot [h_{t-1}, x_t] + b_f\big) &&\text{遗忘门}\\
i_t &= \sigma\big(W_i \cdot [h_{t-1}, x_t] + b_i\big) &&\text{输入门}\\
\tilde{c}_t &= \tanh\big(W_c \cdot [h_{t-1}, x_t] + b_c\big) &&\text{候选细胞状态}\\
c_t &= f_t \odot c_{t-1} + i_t \odot \tilde{c}_t &&\text{更新细胞状态}\\
o_t &= \sigma\big(W_o \cdot [h_{t-1}, x_t] + b_o\big) &&\text{输出门}\\
h_t &= o_t \odot \tanh(c_t) &&\text{输出隐状态}
\end{aligned}
$$

其中 $\sigma$ 是 sigmoid（输出 0–1，充当「开关」），$\odot$ 是逐元素相乘。

**关键在第四条**：$c_t = f_t \odot c_{t-1} + i_t \odot \tilde{c}_t$。当 $f_t \approx 1$ 时，$c_t \approx c_{t-1}$，梯度沿这条路径近似恒等传播（$\partial c_t/\partial c_{t-1} \approx f_t$），不会被反复连乘衰减。这就是「门控缓解梯度消失」的数学本质——**它不是让梯度不衰减，而是给梯度提供了一条衰减更慢的路径**。

### 2.3 GRU：更精简的版本

GRU 把 LSTM 的三个门合并为两个，并把细胞状态与隐状态合并：

$$
\begin{aligned}
z_t &= \sigma\big(W_z \cdot [h_{t-1}, x_t]\big) &&\text{更新门}\\
r_t &= \sigma\big(W_r \cdot [h_{t-1}, x_t]\big) &&\text{重置门}\\
\tilde{h}_t &= \tanh\big(W \cdot [r_t \odot h_{t-1}, x_t]\big) &&\text{候选隐状态}\\
h_t &= (1 - z_t) \odot h_{t-1} + z_t \odot \tilde{h}_t &&\text{输出}
\end{aligned}
$$

| 对比项 | LSTM | GRU |
|--------|------|-----|
| 门数 | 3（遗忘 / 输入 / 输出） | 2（更新 / 重置） |
| 状态 | 隐状态 $h$ + 细胞状态 $c$ | 只有隐状态 $h$ |
| 参数量 | 基准 | 约为 LSTM 的 **2/3** |
| 训练速度 | 较慢 | 较快 |
| 小数据表现 | 略好（表达力更强） | 略好（参数少、不易过拟合） |
| 大数据表现 | 通常略优 | 接近，常打平 |

人名分类案例给出的结论与经验一致：**RNN 快但精度低，LSTM 精度高但慢，GRU 居中且大多数情况下与 LSTM 打平**。实践中建议三个都跑一遍看验证集曲线，不要预设答案（见小结中「优缺点」部分：GRU 相比 LSTM 结构更简单，同样能缓解梯度消失；但 RNN 系列都无法并行，数据量大时效率低）。

### 2.4 PyTorch 中的维度约定（最容易出错的地方）

`nn.RNN` / `nn.LSTM` / `nn.GRU` 的默认布局是 `batch_first=False`：

| 张量 | 形状 | 说明 |
|------|------|------|
| 输入 `input` | `(seq_len, batch, input_size)` | 默认；`batch_first=True` 时变为 `(batch, seq_len, input_size)` |
| 初始隐状态 `h0` | `(num_layers * num_directions, batch, hidden_size)` | 双向时第一维乘 2 |
| 初始细胞状态 `c0`（仅 LSTM） | 同 `h0` | — |
| 输出 `output` | `(seq_len, batch, hidden_size * num_directions)` | 每个时间步的隐状态 |
| 末状态 `hn` | `(num_layers * num_directions, batch, hidden_size)` | — |

**分类任务的取法**：N vs 1 结构要取**最后一个时间步**的输出。若 `batch_first=True`，写 `output[:, -1, :]`；若默认布局，写 `output[-1]`。代码里 `lstm_output[0][-1].unsqueeze(0)` 是在 `batch_size=1` 下的等价写法（先取第 0 个样本，再取最后一个时间步）——这种下标写法在 batch>1 时会出错，务必改用 `output[:, -1, :]`。

代码与在此处还有一处差异：用默认 `batch_first=False`，而实现统一设置了 `batch_first=True`，理由是 `DataLoader` 返回的 `x` 形状是 `(batch, seq_len, input_size)`，设为 True 可以直接承接，避免反复 `transpose`。

### 2.5 两个必须理解的等价关系

**（1）`log_softmax` + `NLLLoss` ≡ `CrossEntropyLoss`**

PyTorch 的 `CrossEntropyLoss` 内部就是 `log_softmax` + `NLLLoss`。因此两种写法等价：

```python
# 写法 A
criterion = nn.CrossEntropyLoss
loss = criterion(logits, y) # logits 是未归一化的输出

# 写法 B（等价）
criterion = nn.NLLLoss
log_prob = nn.LogSoftmax(dim=-1)(logits)
loss = criterion(log_prob, y)
```

为什么代码偏爱写法 B？因为 `log_softmax` 与 NLL 都工作在**对数域**，数值更稳定（避免先 softmax 得到 0 概率再取 log 变成 $-\infty$）。但要注意：**用了写法 B 就不能再在模型外做 softmax**，否则概率被归一化两次，损失完全错乱。这也是「输出层用了 softmax，又接 CrossEntropyLoss」成为高频 bug 的原因。

**（2）`sparse=True` 的 Embedding 需要稀疏优化器**

`nn.Embedding(vocab_size, dim, sparse=True)` 在反向传播时只更新被激活的行，词表大时能省大量内存与计算。但普通 `Adam` 不支持稀疏梯度，需要换 `SparseAdam` 或用 `Adagrad`（`torch.optim.SparseAdam`）。用错优化器会直接报错。

### 2.6 梯度问题的三种缓解手段

| 手段 | 做法 | 解决的 | 局限 |
|------|------|--------|------|
| 梯度裁剪 | `torch.nn.utils.clip_grad_norm_(params, max_norm=5)` | 梯度爆炸 | 对梯度消失无效 |
| 门控结构 | 换 LSTM / GRU | 梯度消失（长依赖） | 仍无法并行 |
| 残差 / 跳跃连接 | 把浅层表示加到深层 | 深度方向的退化 | 时间方向的依赖仍需门控 |
| 正交初始化 | 用正交矩阵初始化 $W_{hh}$ | 减缓谱半径偏离 1 | 只是初始化层面的缓解 |

工程实践：**梯度裁剪几乎是 RNN 训练的标配**，一行代码，代价可忽略。

## 3. 可运行示例

### 3.1 三个模型的维度对照实验

```python
# 依赖: pip install torch
import torch
import torch.nn as nn

batch, seq_len, input_size, hidden = 4, 10, 8, 6

for name, layer in [("RNN", nn.RNN(input_size, hidden, num_layers=1, batch_first=True)),
 ("LSTM", nn.LSTM(input_size, hidden, num_layers=1, batch_first=True)),
 ("GRU", nn.GRU(input_size, hidden, num_layers=1, batch_first=True))]:
 x = torch.randn(batch, seq_len, input_size)
 out = layer(x) # 不传初始状态时，PyTorch 自动初始化为 0
 output = out[0]
 state = out[1]
 print(f"{name:4s} output={tuple(output.shape)} state={type(state).__name__}"
 f" {tuple(state.shape) if torch.is_tensor(state) else [tuple(s.shape) for s in state]}")

# 双向 + 2 层
bi = nn.LSTM(input_size, hidden, num_layers=2, bidirectional=True, batch_first=True)
x = torch.randn(batch, seq_len, input_size)
output, (hn, cn) = bi(x)
print("双向2层 output:", tuple(output.shape)) # (4, 10, 12) = hidden*2
print("双向2层 hn :", tuple(hn.shape)) # (4, 4, 6) = num_layers*2
```

记住两条形状规律：**output 的最后一维 = `hidden_size × num_directions`**；**hn/cn 的第一维 = `num_layers × num_directions`**。

### 3.2 字符级短文本分类器（RNN / LSTM / GRU 三合一）

```python
# 依赖: pip install torch
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

# ---------- 1. 内联小数据集：字符级人名 -> 国别 ----------
raw = [("zhang", "Chinese"), ("wang", "Chinese"), ("liu", "Chinese"), ("chen", "Chinese"),
("smith", "English"), ("brown", "English"), ("jones", "English"), ("wilson", "English"),
("yuasa", "Japanese"), ("yuhara", "Japanese"), ("tanaka", "Japanese"), ("suzuki", "Japanese")]

classes = sorted({c for _, c in raw})
class2id = {c: i for i, c in enumerate(classes)}
chars = sorted({ch for name, _ in raw for ch in name})
char2id = {ch: i + 1 for i, ch in enumerate(chars)} # 0 留给 PAD

MAX_LEN = 10
n_chars = len(char2id) + 1

def name_to_tensor(name: str) -> torch.Tensor:
    """字符 -> id 序列，补齐或截断到 MAX_LEN"""
    ids = [char2id.get(ch, 0) for ch in name.lower()][:MAX_LEN]
    ids += [0] * (MAX_LEN - len(ids))
    return torch.tensor(ids, dtype=torch.long)

class NameDataset(Dataset):
    def __init__(self, data):
        self.x = [name_to_tensor(n) for n, _ in data]
        self.y = [class2id[c] for _, c in data]

        def __len__(self):
            return len(self.x)

        def __getitem__(self, idx):
            return self.x[idx], torch.tensor(self.y[idx], dtype=torch.long)

        # ---------- 2. 模型：Embedding + RNN/LSTM/GRU + 取最后时间步 ----------
        class NameClassifier(nn.Module):
            def __init__(self, rnn_type="lstm", vocab_size=n_chars, embed_dim=16,
            hidden_size=32, num_class=len(classes), num_layers=1):
                super.__init__
                self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
                # batch_first=True: 输入为 (batch, seq_len, embed_dim)
                rnn_cls = {"rnn": nn.RNN, "lstm": nn.LSTM, "gru": nn.GRU}[rnn_type]
                self.rnn = rnn_cls(embed_dim, hidden_size, num_layers, batch_first=True)
                self.fc = nn.Linear(hidden_size, num_class)
                self.log_softmax = nn.LogSoftmax(dim=-1)

                def forward(self, x):
                    emb = self.embedding(x) # (B, L, E)
                    output, _ = self.rnn(emb) # (B, L, H)
                    last = output[:, -1, :] # 取最后一个时间步 -> (B, H)
                    return self.log_softmax(self.fc(last)) # 配 NLLLoss 使用

                # ---------- 3. 训练与预测 ----------
                def train_model(rnn_type, epochs=80):
                    torch.manual_seed(0)
                    loader = DataLoader(NameDataset(raw), batch_size=4, shuffle=True)
                    model = NameClassifier(rnn_type=rnn_type)
                    criterion = nn.NLLLoss # 与模型内 log_softmax 配对
                    optimizer = optim.Adam(model.parameters(), lr=0.01)
                    # RNN 训练标配：梯度裁剪，防止梯度爆炸
                    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)

                    for epoch in range(epochs):
                        total_loss = 0.0
                        for x, y in loader:
                            out = model(x)
                            loss = criterion(out, y)
                            optimizer.zero_grad()
                            loss.backward()
                            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
                            optimizer.step
                            total_loss += loss.item
                            if (epoch + 1) % 20 == 0:
                                print(f" [{rnn_type}] epoch {epoch+1:3d} loss={total_loss/len(loader):.4f}")
                                return model

                            def predict(model, name):
                                model.eval
                                with torch.no_grad:
                                    out = model(name_to_tensor(name).unsqueeze(0)) # 加 batch 维
                                    prob = out.exp
                                    idx = int(prob.argmax(dim=-1))
                                    return classes[idx], float(prob[0, idx])

                                if __name__ == "__main__":
                                    for rnn_type in ["rnn", "lstm", "gru"]:
                                        m = train_model(rnn_type)
                                        acc = sum(predict(m, n)[0] == c for n, c in raw) / len(raw)
                                        print(f"{rnn_type.upper():4s} 训练集准确率: {acc:.3f} 预测('zhang')={predict(m, 'zhang')}")
```

要点说明：

- `padding_idx=0` 保证 PAD 的向量恒为 0 且不参与梯度更新。
- 取 `output[:, -1, :]` 得整句表示；**如果样本有 padding，最后一个时间步可能是 PAD**，此时应先按真实长度取 `output[i, len_i - 1, :]`（或使用 `pack_padded_sequence`）。本示例把名字统一补到 10 且 `names` 较短，影响有限，但真实项目必须处理。
- `clip_grad_norm_` 在 `step` 之前调用，且应在 `backward` 之后。

### 3.3 验证 LSTM 的长依赖能力（门控的直观效果）

```python
# 依赖: pip install torch
import torch
import torch.nn as nn

# 任务：序列末尾输出「开头那个 token 的 id」——需要记住 T 步之前的信息
def make_batch(batch=32, seq_len=60, vocab=10):
    x = torch.randint(1, vocab, (batch, seq_len))
    y = x[:, 0] # 标签 = 第一个 token
    return x, y

def run(rnn_type, seq_len=60, steps=300):
    torch.manual_seed(42)
    embed = nn.Embedding(10, 16, padding_idx=0)
    rnn_cls = {"rnn": nn.RNN, "lstm": nn.LSTM, "gru": nn.GRU}[rnn_type]
    rnn = rnn_cls(16, 32, batch_first=True)
    fc = nn.Linear(32, 10)
    params = list(embed.parameters()) + list(rnn.parameters()) + list(fc.parameters())
    opt = torch.optim.Adam(params, lr=0.01)
    crit = nn.CrossEntropyLoss

    for step in range(steps):
        x, y = make_batch(seq_len=seq_len)
        out, _ = rnn(embed(x))
        logits = fc(out[:, -1, :])
        loss = crit(logits, y)
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(params, 5.0)
        opt.step

        with torch.no_grad:
            x, y = make_batch(seq_len=seq_len)
            out, _ = rnn(embed(x))
            pred = fc(out[:, -1, :]).argmax(-1)
            acc = (pred == y).float.mean.item
            return acc

        for t in ["rnn", "lstm", "gru"]:
            for L in [10, 40]:
                print(f"{t:4s} seq_len={L:3d} 准确率={run(t, seq_len=L):.3f}")
```

预期现象：序列短（10）时三者都能学到；序列变长（40–60）时传统 RNN 的准确率明显掉到随机水平附近，而 LSTM / GRU 仍能保持较高准确率——这就是门控带来的长依赖能力差异。想更直观，可以把 `seq_len` 继续加大到 100 以上，观察 RNN 与 LSTM 的差距。

## 4. 常见坑

| 现象 | 原因 | 解决 |
|------|------|------|
| 报维度错误 "expected input of size (…)" | `batch_first` 与输入形状不匹配（RNN 默认 `batch_first=False`） | 统一设 `batch_first=True`，或在送入前 `transpose(0, 1)` |
| 分类准确率始终在随机水平 | 取了错误的时间步（如 `output[0]` 取的是 batch 维），或最后一步是 PAD | 取 `output[:, -1, :]`；有 padding 时按真实长度取最后有效步或用 `pack_padded_sequence` |
| loss 为 NaN / 训练发散 | RNN 梯度爆炸 | `clip_grad_norm_(..., max_norm=5)`，降低学习率，检查输入是否有异常值 |
| loss 不下降、梯度为 0 | 用了 `log_softmax` + `NLLLoss`，但又在外面套了 `softmax`（或反之） | 二选一：`logits + CrossEntropyLoss` 或 `log_softmax + NLLLoss` |
| 报错 "Adam does not support sparse gradients" | `nn.Embedding(sparse=True)` 配了普通 Adam | 换 `torch.optim.SparseAdam`，或把 `sparse` 设回 False |
| `hn` 形状与预期不符 | 忘记 `num_layers × num_directions` 是第一维 | `h0 = torch.zeros(num_layers * num_directions, batch, hidden)` |
| 双向模型用于生成任务时结果荒谬 | 双向结构在推理时能「看到」未来，训练/推理不一致 | 生成任务（翻译解码、语言模型）改用单向 |
| 长序列训练极慢、显存爆炸 | RNN 需保存所有时间步的中间激活用于反向传播 | 用截断 BPTT（`detach` 分段）、减小 `seq_len`、换 Transformer |
| 训练集准确率 1.0、验证集很差 | 模型把训练样本背下来了（参数远多于样本） | 减小 `hidden_size` / `num_layers`、加 dropout、早停 |
| GRU/LSTM 效果差很多但超参相同 | 两者最优超参不同（学习率、dropout、隐藏维度） | 分别调参后再对比，不要用一套超参横评 |

## 5. 面试问答

**Q1. LSTM 是怎么缓解梯度消失的？请从公式层面解释。**

<details markdown="1">
<summary markdown="1">参考答案</summary>

先看问题根源。传统 RNN 的隐状态递推为

$$h_t=\tanh(W_{xh}x_t+W_{hh}h_{t-1}+b_h)$$

反向传播时梯度要沿时间连乘

$$\frac{\partial h_t}{\partial h_{t-1}}=W_{hh}^\top\operatorname{diag}\big(1-\tanh^2(\cdot)\big)$$

连续 $T$ 步就是该矩阵的 $T$ 次幂。当 $W_{hh}$ 的谱半径小于 1 时梯度指数衰减（消失）；大于 1 时指数增长（爆炸）。tanh 的导数最大为 1，进一步加剧衰减。

LSTM 的关键在细胞状态的更新式

$$c_t=f_t\odot c_{t-1}+i_t\odot\tilde c_t$$

对 $c_{t-1}$ 求偏导得到

$$\frac{\partial c_t}{\partial c_{t-1}}=f_t$$

即**梯度沿细胞状态的传播只被一个门（遗忘门）逐元素缩放**，而不是被一个矩阵连乘。当 $f_t\approx1$ 时，$\partial c_t/\partial c_{t-1}\approx1$，形成一条近似恒等的「梯度高速公路」，梯度可以跨越很多时间步而不衰减。

准确表述要点（面试常在这里被追问）：

- LSTM **不是完全消除**梯度消失，而是提供了一条衰减更慢的路径；遗忘门长期小于 1 时仍然会衰减。
- 它同样**不能解决梯度爆炸**——那要靠梯度裁剪。
- 门控让模型能**学习**该记多久：$f_t$ 由当前输入和上一步隐状态决定，因此模型可以自适应地对不同信息设置不同的记忆时长。

</details>

**Q2. RNN、LSTM、GRU 应该怎么选？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

三个维度：数据量、任务对长依赖的需求、算力预算。

| 情况 | 推荐 | 理由 |
|------|------|------|
| 序列很短（< 10 步）、追求速度 | 传统 RNN | 参数量最少，短序列上梯度问题不显著，训练/推理最快 |
| 需要长依赖、数据量中等 | LSTM | 表达力最强，三个门对信息流的控制更精细，历史上在翻译/NER 上优势明显 |
| 需要长依赖、模型大小和速度敏感 | GRU | 参数约为 LSTM 的 2/3，训练更快；大量实验显示效果与 LSTM 接近甚至更好 |
| 需要双向上下文（分类、标注） | Bi-LSTM / Bi-GRU | 每个位置同时获得左右信息，通常比单向提升明显 |
| 需要自回归生成 | 单向 RNN/LSTM/GRU | 双向在推理时不可用 |
| 数据量非常大、可以上 GPU 集群 | 直接上 Transformer | RNN 系列无法并行，长序列训练效率被 Transformer 碾压 |

实践建议：**先跑 GRU 作为基线**（训练快、参数少），如果验证集不理想再试 LSTM；两者的最优超参不同，横评时要分别调参。另外一个重要判断依据是任务类型——如果任务是分类/标注而非生成，优先考虑双向；如果序列很长（>512），直接考虑 Transformer 或先用 CNN 降采样再做 RNN。

</details>

**Q3. 为什么 RNN 无法并行，而 Transformer 可以？这对训练效率影响多大？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

**RNN 无法并行的原因**是时间步之间存在**数据依赖**：$h_t$ 的计算需要 $h_{t-1}$，$h_{t-1}$ 又需要 $h_{t-2}$，因此必须逐步串行推进。整个序列的 $T$ 个时间步无法在一次矩阵运算中完成，GPU 的大量并行核心被空置。这对训练效率的影响是决定性的——序列越长，GPU 利用率越低，训练时间的增长接近线性而非饱和。

**Transformer 可以并行**的原因是把「逐时间步递归」换成了「一次矩阵乘法算完所有位置」：

$$\text{Attention}(Q,K,V)=\text{softmax}\Big(\frac{QK^\top}{\sqrt{d_k}}\Big)V$$

在这个公式里，每个位置的输出直接依赖于所有位置的 $K,V$，**不需要等待前一个位置算完**，因此整句可以一次性送入 GPU。位置信息由位置编码补回。

需要精确区分两点（面试常见追问）：

1. **结构层面**：Encoder 端可完全并行；Decoder 在**训练**时可并行（用 look-ahead mask 模拟自回归），但**预测**时仍必须逐 token 串行。
2. **算子层面**：self-attention 内部各 token 之间仍有计算依赖，之所以看起来并行，是因为用矩阵乘法把循环「展开」成了一次张量运算。

效率影响的具体量级：RNN 在序列长度 $T$ 上的训练时间是 $O(T)$ 个串行步骤；Transformer 的注意力计算是 $O(T^2 d)$ 的**并行**运算。当 $T$ 在 512 以内且 GPU 并行度高时，Transformer 的实际墙钟时间远小于 RNN；代价是显存与计算量随 $T^2$ 增长，这也是长文本（$T > 4096$）需要 FlashAttention、稀疏注意力等优化技术的原因。

</details>

## 6. 自测题

**1. 判断四个任务各属哪种 RNN 结构：① 词性标注；② 情感二分类；③ 英译法机器翻译；④ 看图生成一句描述。**

<details markdown="1">
<summary markdown="1">参考答案</summary>

| 任务 | 结构 | 理由 |
|------|------|------|
| 词性标注 | **N vs N** | 输入 $N$ 个词，输出 $N$ 个词性，等长 |
| 情感二分类 | **N vs 1** | 输入 $N$ 个词，输出一个标签；只需最后一个时间步的输出 |
| 英译法机器翻译 | **N vs M** | 输入输出长度不等，需要 Encoder-Decoder（seq2seq） |
| 看图生成描述 | **1 vs N** | 输入是单张图片的编码向量，输出是一个词序列 |

补充：NER 也属 N vs N；文本摘要属 N vs M；对联生成通常是 N vs N（上下联等长）。

</details>

**2. 设 `nn.LSTM(64, 128, num_layers=2, bidirectional=True, batch_first=True)`，输入为 `(8, 20, 64)`。写出 `output`、`hn`、`cn` 的形状。**

<details markdown="1">
<summary markdown="1">参考答案</summary>

- **output**：`(batch, seq_len, hidden_size × num_directions)` = `(8, 20, 256)`
- **hn**：`(num_layers × num_directions, batch, hidden_size)` = `(4, 8, 128)`
- **cn**：与 `hn` 同形 = `(4, 8, 128)`

两条记忆规律：

1. `output` 的最后一维**乘方向数**（双向把正反两向拼在一起），第一维是 batch（因为 `batch_first=True`）。
2. `hn`/`cn` 的第一维是 **层数乘方向数**，第二维是 batch，第三维是 `hidden_size`（不乘方向数，因为每个方向各自有一个末状态）。

如果 `batch_first=False`，则输入应为 `(20, 8, 64)`，`output` 为 `(20, 8, 256)`。

</details>

**3. 为什么分类任务取 `output[:, -1, :]` 可能有问题？正确做法是什么？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

**问题**：一个 batch 内的样本经过 padding 后长度被统一，但**真实长度不同**。如果统一取最后一个时间步 `output[:, -1, :]`，对那些真实长度较短的样本，取到的是 **PAD 位置的隐状态**，而不是最后一个真实 token 的隐状态。这会引入错误信息，尤其当 padding 比例很高时准确率明显下降。

正确做法有三种：

1. **按真实长度取**：用 `lengths` 张量，写 `output[torch.arange(B), lengths - 1, :]`，取出每个样本最后一个有效时间步。
2. **打包序列（推荐）**：用 `pack_padded_sequence` 让 RNN 完全跳过 PAD 位置（需先按长度降序排序），计算更快且更正确；LSTM 还要额外处理 `(h0, c0)` 的 `batch_sizes`。
3. **用 attention / max-pooling 池化**：对所有有效时间步做加权或取最大，而不是只取最后一步。这是很多分类模型的实际做法，对长文本更稳健。

注意 `padding="pre"`（前面补 PAD）时情况反过来了：最后一个时间步恰好是真实内容，此时 `output[:, -1, :]` 反而是合理的。所以关键是**明确 padding 方向并保持一致**。

</details>

**4. 一段代码 `out = model(x); loss = criterion(out, y)`，其中 `criterion = nn.CrossEntropyLoss` 且 `model` 内部最后一层是 `nn.Softmax(dim=-1)`。有什么问题？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

这是**双重归一化**错误，会导致训练效果严重变差（通常表现为 loss 下降极慢或卡住、准确率上不去）。

原因：`nn.CrossEntropyLoss` 内部已经包含 `log_softmax`，它期望的输入是**未归一化的 logits**。如果模型先做了 softmax，输出被压到 $[0,1]$ 且每行和为 1，再送入 CrossEntropyLoss 相当于在概率分布上又做一次 log_softmax，梯度被严重扭曲（概率值都很小，$\log$ 后的分布变得非常平缓，梯度信号被压扁）。

正确写法二选一：

```python
# 方案 A（推荐）：模型输出 logits，损失用 CrossEntropyLoss
def forward(self, x):
 return self.fc(...) # 不加 softmax
criterion = nn.CrossEntropyLoss

# 方案 B：模型输出 log_softmax，损失用 NLLLoss
def forward(self, x):
 return nn.LogSoftmax(dim=-1)(self.fc(...))
criterion = nn.NLLLoss
```

**唯一需要 softmax 的地方是推理阶段**——要把 logits 转成可读的概率（或计算置信度），此时用 `logits.softmax(-1)` 或对 `log_softmax` 输出取 `.exp`。训练时绝不要加。

</details>

**5. 在 60 步的长序列「记住第一个 token」任务上，RNN 准确率掉到随机水平而 LSTM 保持较高。请解释原因，并说明加大隐藏层维度能否救回 RNN。**

<details markdown="1">
<summary markdown="1">参考答案</summary>

**原因**：这个任务要求模型在最终时刻回忆起 $T-1$ 步之前的信息，本质考验**长距离梯度传播**。RNN 的梯度要连乘 $W_{hh}^\top\operatorname{diag}(1-\tanh^2)$ 共 $T-1\approx59$ 次；即便单步因子的谱半径接近 1，累积后梯度也会指数衰减到接近 0，导致早期时间步的权重几乎收不到有效梯度、学不到「把第一个 token 编码进记忆」这件事。LSTM 通过细胞状态通道 $c_t=f_t\odot c_{t-1}+\dots$ 使梯度传播近似恒等（$\partial c_t/\partial c_{t-1}=f_t\approx1$），因此信息能跨越几十步保留下来。

**加大隐藏层维度能部分救回，但不能根治**：

- 增大 $h$ 会提高模型的记忆容量，理论上能记住更多信息，实测会让准确率从随机水平往上抬一些。
- 但梯度消失的根源是**时间维度的连乘**，与维度无关——连乘 $T$ 次依然会让远端梯度消失。维度增大只是让「容量」变大，不改变「梯度能否传到远端」。
- 而且维度增大带来参数量 $O(h^2)$ 增长，小数据上会过拟合、训练变慢。

**真正有效的做法**：

1. 换 **LSTM / GRU**（门控提供恒等通道）——最直接。
2. 用 **梯度裁剪**（治爆炸）配合，避免换门控后反而爆梯度。
3. 换 **Transformer**（任意两位置路径长度 $O(1)$，从根本上绕开连乘问题）。
4. 加 **attention 机制**（第 08 篇）——让模型在解码时直接「回看」所有时间步，而不是依赖记忆。

这也正是 NLP 从 RNN 走向 Transformer 的核心动机之一。

</details>

## 7. 延伸阅读

- LSTM 原始论文《Long Short-Term Memory》(Hochreiter & Schmidhuber, 1997)：https://www.bioinf.jku.at/publications/older/2604.pdf
- GRU 原始论文《Learning Phrase Representations using RNN Encoder-Decoder for Statistical Machine Translation》(Cho et al., 2014)：https://arxiv.org/abs/1406.1078
- 序列学习经典综述《Sequence to Sequence Learning with Neural Networks》(Sutskever et al., 2014)：https://arxiv.org/abs/1409.3215
- 《Understanding LSTM Networks》（colah 的图解博客，门控最直观的解释）：https://colah.github.io/posts/2015-08-Understanding-LSTMs/
- PyTorch `nn.LSTM` / `nn.GRU` / `nn.RNN` 官方文档（维度约定与 `pack_padded_sequence`）：https://pytorch.org/docs/stable/generated/torch.nn.LSTM.html
- 《An Empirical Exploration of Recurrent Network Architectures》(Jozefowicz et al., 2015)（GRU 与 LSTM 的大规模对比实验）：https://proceedings.mlr.press/v37/jozefowicz15.html

---

[⬅️ 返回 NLP 目录](README.md)
