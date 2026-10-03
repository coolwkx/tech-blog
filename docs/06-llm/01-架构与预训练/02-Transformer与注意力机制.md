> **一句话总结**：Transformer 用 self-attention 取代循环结构实现并行建模，再由它分化出自编码（encoder-only）、自回归（decoder-only）与序列到序列（encoder-decoder）三大类架构；今天的大模型几乎都选择 decoder-only，因为它在同等参数量与推理成本下效率最高。
> **前置知识**：矩阵乘法与张量维度、softmax、点积的几何含义、PyTorch/NumPy 基础。
> **学完能做到**：1. 画出 Transformer 的整体结构并说明每层作用；2. 用代码从零实现缩放点积注意力与多头注意力，说清每个张量的形状；3. 对比 BERT/GPT/T5 的架构、预训练目标与适用任务，并解释 RoPE、RMSNorm、GQA 为什么要这样改。

## 1. 核心概念

### 1.1 从原始 Transformer 到三类 LLM

2017 年《Attention Is All You Need》提出原始 Transformer，它同时包含 encoder 与 decoder。基于这一框架，
后续模型按「用了哪一部分」分成三类：

| 类别 | 英文 | 代表模型 | 注意力可见性 | 擅长任务 |
|---|---|---|---|---|
| 自编码模型 | AutoEncoder (AE), encoder-only | BERT | 双向（可见全句） | 自然语言理解 NLU：分类、情感分析、抽取式问答 |
| 自回归模型 | AutoRegressive (AR), decoder-only | GPT 系列、LLaMA、Qwen、ChatGLM | 单向（只能看左侧上文） | 自然语言生成 NLG：摘要、翻译、对话、续写 |
| 序列到序列模型 | Sequence-to-Sequence, encoder-decoder | T5、BART | encoder 双向 + decoder 因果 | 机器翻译、文本到文本的统一转换 |

### 1.2 三类架构的预训练目标对比

| 模型 | 架构 | 预训练目标 | 关键设计 |
|---|---|---|---|
| BERT | Encoder-only | MLM（Masked LM）+ NSP（Next Sentence Prediction） | 双向 Transformer，输入含 Token/Segment/Position 三种 embedding |
| GPT-1 | Decoder-only | 单向语言模型（自回归 next-token prediction） | 12 层 Decoder Block，去掉第二个 encoder-decoder attention 子层 |
| T5 | Encoder-Decoder | 自监督（因果语言建模 + 填空任务） | 把所有 NLP 任务统一为 text-to-text |

> 补充：GPT-1 论文主张「生成式预训练 + 判别式微调」，而 BERT 论文主张「双向预训练 + 特征表示」。
> 结论是 GPT 更擅长 NLG，BERT 更擅长 NLU——这也是两类架构最本质的差异来源。

### 1.3 大模型时代为什么统一到 Decoder-only

| 理由 | 说明 |
|---|---|
| 训练效率与工程实现 | 单一堆叠结构、无需设计 encoder/decoder 之间的交叉注意力，易于扩展与并行 |
| 同等条件下的性价比 | 同等参数量、同等推理成本下，Decoder-only 是最优选择；Encoder-Decoder 表现更好往往只是因为它多了参数 |
| 双向注意力对生成无实质收益 | 生成任务只需要左侧上文，引入双向注意力在理论上可能因低秩问题削弱表达能力 |
| 与 in-context learning 契合 | 自回归范式天然支持 prompt 拼接与 few-shot，无需为每个任务改结构 |

### 1.4 GPT 系列的演进（架构与训练目标）

| 模型 | 时间 | 参数规模 | 数据集 | 核心思想 | 关键变化 |
|---|---|---|---|---|---|
| GPT-1 | 2018.06 | 1.17 亿 | BooksCorpus（约 5GB，7400 万句） | 无监督预训练 + 有监督微调 | 12 层 / 12 head / 768 维 |
| GPT-2 | 2019.02 | 最大 15 亿 | WebText（约 800 万篇、40GB） | **zero-shot**：无监督多任务学习 | Pre-LayerNorm、最后一层后加 LN、序列长度 512→1024 |
| GPT-3 | 2020.05 | 最大 1750 亿 | 约 45TB 文本（清洗后 570GB） | **few-shot / in-context learning** | 引入 sparse attention、最大版本 96 层，head size 96，向量维度 12288，文本长度 2048 |
| ChatGPT | 2022.11 | 未公开 | — | 用人类反馈强化学习（RLHF）对齐 | SFT → RM → PPO 三步 |

GPT-3 的数据配比（训练 token 数）：

| 数据集 | tokens | 占比 |
|---|---|---|
| CommonCrawl (filtered) | 4100 亿 | 60% |
| WebText2 | 190 亿 | 22% |
| Books1 | 120 亿 | 8% |
| Books2 | 550 亿 | 8% |
| Wikipedia | 30 亿 | 2% |

### 1.5 Zero-shot / One-shot / Few-shot 的区别

以「英译法」为例：

| 方式 | 做法 | 效果（GPT-3 论文结论） |
|---|---|---|
| Zero-shot | 只给任务描述，直接给测试数据 | 最差 |
| One-shot | 任务描述 + 1 个示例 | 次之 |
| Few-shot | 任务描述 + N 个示例 | 最佳 |

**In-context learning（ICL，情境学习/提示学习）** 与 fine-tuning 的核心区别：

| 对比项 | Fine-tuning | In-context learning |
|---|---|---|
| 是否更新参数 | 更新（有梯度回传） | **不更新**，只做前向推理 |
| 需要数据量 | 大（任务相关标注集） | 小（约 10~100 条示例） |
| 新任务适应 | 需重新训练、每个任务一套权重 | 改 prompt 即可 |
| 本质 | 把任务知识写进参数 | 让模型从上下文「读出」任务模式 |

## 2. 关键机制

### 2.1 Transformer 的整体结构

原始 Transformer = encoder 堆叠 + decoder 堆叠，每个 block 由「注意力子层 + 前馈子层」再加残差与归一化构成。

| 模块 | 组成 | 作用 |
|---|---|---|
| Encoder Block | Multi-Head Self-Attention + Feed Forward | 双向编码输入序列 |
| Decoder Block | Masked Multi-Head Self-Attention + Cross-Attention + Feed Forward | 因果生成，并参考 encoder 输出 |

**GPT 对 Decoder Block 的裁剪**：取消了第二个 encoder-decoder attention 子层，只保留
Masked Multi-Head Attention 与 Feed Forward。GPT-1 用了 12 个 Decoder Block（原始 Transformer 用 6 个）。

**BERT 的三大模块**：

| 模块 | 说明 |
|---|---|
| Embedding 模块 | Token Embeddings + Segment Embeddings + Position Embeddings，三者**直接相加**；首 token 是 `[CLS]`，可用于分类 |
| 双向 Transformer | 只使用经典 Transformer 的 Encoder 部分，完全舍弃 Decoder；两个预训练任务都体现在这里 |
| 预微调模块 | 按任务调整：句级分类直接取 `[CLS]` 的最后一层隐状态加全连接层后 softmax |

（BERT-Base 关键参数：12 层、12 个 head、特征维度 768、总参数量 1.15 亿；训练数据为
BooksCorpus（800M words）+ English Wikipedia（2500M words）。）

### 2.2 BERT 的两个预训练任务

| 任务 | 做法 | 细节 |
|---|---|---|
| Masked LM | 随机抽取 15% 的 token 参与预测 | 其中 **80%** 替换为 `[MASK]`、**10%** 替换为随机词、**10%** 保持不变 |
| Next Sentence Prediction | 输入句子对 (A, B)，预测 B 是否为 A 的下一句 | **50%** 是真实下一句（IsNext），**50%** 是随机句（NotNext） |

为什么要做 80/10/10 而不是全部替换成 `[MASK]`？因为下游任务里根本不会出现 `[MASK]`，
全量替换会造成预训练与微调之间的**输入噪声差异**；留 10% 原词、10% 随机词可以让模型对
「token 不可信」这一情况保持鲁棒。

### 2.3 缩放点积注意力与张量形状

给定输入序列长度 $n$、模型维度 $d_{model}$、注意力头数 $h$，每个头的维度 $d_k=d_v=d_{model}/h$。

| 张量 | 形状 | 说明 |
|---|---|---|
| 输入 $X$ | $(n, d_{model})$ | 一个 batch 内的一条序列 |
| $W_Q, W_K, W_V$ | $(d_{model}, d_{model})$ | 线性投影参数 |
| $Q, K, V$ | $(n, d_{model})$ | 投影结果 |
| 按头切分并转置 | $(h, n, d_k)$ | 每个头独立计算 |
| 注意力分数 $QK^{\top}$ | $(h, n, n)$ | 每个 token 对所有 token 的相似度 |
| 注意力输出 | $(h, n, d_k)$ | 加权求和结果 |
| 拼接 + 输出投影 | $(n, d_{model})$ | 多头结果合并 |

**缩放点积注意力公式**：

$$\mathrm{Attention}(Q,K,V)=\mathrm{softmax}\!\left(\frac{QK^{\top}}{\sqrt{d_k}}\right)V$$

**为什么要除以 $\sqrt{d_k}$**：当 $d_k$ 较大时，$Q\cdot K$ 的点积方差随维度线性增长（约等于 $d_k$），
softmax 的输入会落入梯度极小的饱和区，导致梯度消失、训练不稳定。除以 $\sqrt{d_k}$ 把方差拉回 1 附近，
使 softmax 保持在梯度良好的区间。

**Multi-Head 为什么有效**：单头只能学到一种「相似度视角」；多头把表示空间切成 $h$ 份分别做注意力，
不同头可以分别关注语法依赖、指代、位置邻近等不同模式，最后拼接再投影，等价于在多个子空间并行做关系建模，
表达力显著强于单头（且总计算量与单头同维时基本相当）。

**Mask 的两种类型**：

| 类型 | 作用 | 使用场景 |
|---|---|---|
| Padding mask | 屏蔽补齐到同一长度的无效 pad token | 所有 batch 训练 |
| Causal mask（因果/上三角 mask） | 遮掉未来位置，只允许看到左侧上文 | decoder-only 生成模型 |
| 交叉 mask | decoder 只能关注 encoder 的有效位置 | encoder-decoder |

### 2.4 GPT 的训练目标与似然函数

给定句子 $U=[u_1,u_2,\dots,u_n]$，GPT-1 的预训练目标是最大化：

$$L_1(U)=\sum_{i}\log P(u_i \mid u_{i-k},\dots,u_{i-1};\Theta)$$

其中 $k$ 是上文的窗口大小——$k$ 越大，模型可获取的上文信息越充足，能力越强（但计算成本上升）。
输入经过 embedding（$W_e$ 形状 $[vocab\_size, embedding\_dim]$）加位置编码（$W_p$ 形状 $[max\_seq\_len, embedding\_dim]$）
得到 $h_0$，再经多层 Decoder Block 得到 $h_t$，最后用语言模型头预测下一个词。

微调阶段则是把下游任务的输入改造成 token 序列 $[x_1,\dots,x_n]$，用最后一层隐状态 $h_t$ 接一个输出层 $W_y$ 预测标签 $y$：

$$L_2(C)=\sum_{(x,y)}\log P(y\mid x_1,\dots,x_n)$$

**最终优化目标是两者加权和**；适配下游任务分两步：① 按任务定义不同的输入构造方式；② 为不同任务增加不同的分类层。

### 2.5 位置编码：从绝对到 RoPE

| 方案 | 代表模型 | 特点 |
|---|---|---|
| 可学习绝对位置编码 | GPT-1/2、BERT | 实现简单，但外推性差，超出训练长度即失效 |
| 相对位置编码 | BLOOM | 建模相对距离，外推性更好 |
| 简化版相对位置编码（标量加到 logits） | T5 | 各层共享位置编码，同层不同头独立学习 |
| 旋转位置编码 RoPE | LLaMA、Qwen、Baichuan、ChatGLM | 对 Q/K 向量按「两两一组」做旋转变换，通过内积天然编码相对位置 |

RoPE 的计算流程：对序列中每个 token 的 embedding 先算出 query 和 key 向量，为每个位置计算对应的旋转位置编码，
再对 query/key 向量的元素**两两一组**应用旋转变换，最后计算 query 与 key 的内积得到 self-attention 结果。
RoPE 具有更好的**外推性**，是目前大模型应用最广的相对位置编码方案之一。

### 2.6 归一化与激活函数的演进

| 方案 | 相比前代的变化 | 为什么 |
|---|---|---|
| LayerNorm | 在每个样本的特征维度上计算均值/方差并标准化，含可学习参数 $\gamma,\beta$ | 训练稳定，不依赖 batch 大小 |
| Pre-LayerNorm | 把 LN 放到 Self-Attention 与 Feed Forward **之前**（GPT-2 起） | 随层数加深，梯度消失/爆炸风险增大，前置 LN 减小层间方差波动，梯度更稳 |
| RMSNorm | 去掉减去均值的部分，只用均方根归一化 | 计算更高效；不去除均值成分，更好保留信号 |
| DeepNorm | 残差连接加缩放因子 $\alpha>1$：`LayerNorm(αx + Sublayer(x))` | 专为极深 Transformer 设计，平衡残差以提升训练稳定性 |
| ReLU → GELU | 引入高斯分布特性，负输入处更平滑 | 提升性能与训练效率 |
| GLU 系列：GeGLU / SwiGLU | 在 GLU 门控结构上把激活换成 GELU / Swish(βx) | 门控 + 平滑激活，提升表达能力，主流大模型普遍采用 |

### 2.7 注意力的稀疏化与 KV Cache

**Sparse Attention（GPT-3 引入）**：传统 self-attention（dense attention）每个 token 两两计算，复杂度 $O(n^2)$；
sparse attention 让每个 token 只与部分 token 计算，复杂度 $O(n\log n)$。具体做法是：除相对距离不超过 $k$、
以及相对距离为 $k,2k,3k,\dots$ 的 token 外，其余全部置 0。好处是：① 契合「局部紧密相关、远程稀疏相关」的语言特性；
② 降低注意力层计算复杂度，节约显存与耗时，从而处理更长输入。

**KV Cache**：只存在于自回归 decoder 中（BERT 没有）。生成第 $n+1$ 个 token 时，前面的
$\{x_i^l \mid 1\le i\le n\}$ 与上一次计算完全相同，因此可以复用，避免重复计算 K/V。
实测在 Tesla T4 上生成 1000 个 token，用 KV cache 约 11 秒，不用则约 56 秒。
使用 `transformers` 时可通过 `generate(..., use_cache=True)` 控制。

**MHA / MQA / GQA**：这是减少 KV cache 开销的关键手段。

| 方案 | 结构 | 特点 |
|---|---|---|
| MHA | 每个 query 都有自己的一套 key/value 参数 | 效果最好，但参数量与 KV cache 最大 |
| MQA | 所有 query 共享**一套** key/value | 参数量、显存最省，效果略降 |
| GQA | 把 query 分组，共享 **N 套** key/value | MHA 与 MQA 的折中：保留速度，效果接近 MHA |

### 2.8 T5 的架构与训练

T5 的模型结构与原始 Transformer 基本一致，仅做了几处改动：
- 采用简化版 LayerNorm：去除了 LayerNorm 的 bias，并把 LayerNorm 放在**残差连接外面**；
- 位置编码采用简化版相对位置编码（标量加到 logits 上参与注意力权重计算），各层共享位置编码，同一层内不同头独立学习。

T5 的核心目的是**构建任务统一框架**：把所有 NLP 任务都视为「文本到文本」的转换，
从而用同样的模型、同样的损失函数、同样的训练/解码过程完成所有任务。预训练阶段使用类似 BERT 和 GPT 的
大规模自监督策略，但统一以 text-to-text 格式处理，预训练任务包括因果语言建模与填空任务两类；
此外还可利用不同任务的标注数据做有监督多任务预训练（如 SQuAD 问答、机器翻译）。
（T5-Base：24 层、12 head、768 维、2.2 亿参数；数据来自过滤后的 CommonCrawl → C4 数据集。）

## 3. 可运行示例

### 3.1 用 NumPy 从零实现缩放点积注意力与多头注意力

```python
import numpy as np

np.random.seed(0)


def softmax(x, axis=-1):
    e = np.exp(x - x.max(axis=axis, keepdims=True)) # 减最大值，防止溢出
    return e / e.sum(axis=axis, keepdims=True)


def scaled_dot_product_attention(Q, K, V, mask=None):
    """Q: (..., n_q, d_k) K: (..., n_k, d_k) V: (..., n_k, d_v)"""
    d_k = Q.shape[-1]
    scores = Q @ K.swapaxes(-2, -1) / np.sqrt(d_k) # (..., n_q, n_k)
    if mask is not None:
        scores = np.where(mask, scores, -1e9) # 屏蔽位置给极小值
        return softmax(scores, axis=-1) @ V, scores


    def multi_head_attention(X, n_heads, mask=None):
        """X: (n, d_model) -> 输出 (n, d_model)"""
        n, d_model = X.shape
        assert d_model % n_heads == 0, "d_model 必须能被 n_heads 整除"
        d_k = d_model // n_heads

        W = np.random.randn(d_model, 3 * d_model) * 0.02 # 可学习投影的替身
        QKV = X @ W # (n, 3*d_model)
        Q, K, V = np.split(QKV, 3, axis=-1)

        def split(t): # (n, d_model) -> (n_heads, n, d_k)
            return t.reshape(n, n_heads, d_k).transpose(1, 0, 2)

        Q, K, V = split(Q), split(K), split(V)
        out, scores = scaled_dot_product_attention(Q, K, V, mask) # (n_heads, n, d_k)
        out = out.transpose(1, 0, 2).reshape(n, d_model) # 拼接多头
        return out, scores


    n, d_model, n_heads = 4, 8, 2
    X = np.random.randn(n, d_model)
    causal = np.tril(np.ones((n, n), dtype=bool)) # 位置 i 只能看到 j <= i
    out, scores = multi_head_attention(X, n_heads, mask=causal)

    print("输入 X 形状 :", X.shape)
    print("注意力分数形状 :", scores.shape, "= (n_heads, n_q, n_k)")
    print("输出形状 :", out.shape)
    print("第 0 个头的分数矩阵 :\n", np.round(scores[0], 3))
```

**要观察的三件事**：① `scores` 的形状是 `(n_heads, n_q, n_k)`，说明每个头各自有一张注意力矩阵；
② 因果 mask 下，第 $i$ 行只在 $j\le i$ 的位置有权重；③ 去掉 `/ np.sqrt(d_k)` 后分数绝对值会明显变大，
softmax 输出会更「尖锐」甚至饱和——这就是缩放的作用。

## 4. 常见坑

| 坑 | 现象 | 原因 | 正确做法 |
|---|---|---|---|
| 忘记除以 $\sqrt{d_k}$ | 训练 loss 不下降或剧烈震荡 | 点积方差过大，softmax 饱和、梯度消失 | 缩放点积：$QK^{\top}/\sqrt{d_k}$ |
| 多头维度不整除 | reshape 报错 | `d_model % n_heads != 0` | 保证整除（如 512/8、768/12），或改用能整除的配置 |
| 多头切分时维度顺序写错 | 结果与单头不一致 | `view` 后需要 `transpose` 才能按头聚合 | `(B,T,C) → (B,T,h,d_k) → transpose → (B,h,T,d_k)` |
| 混淆 padding mask 与 causal mask | 生成时看到未来信息 / 训练时 pad 参与注意力 | 两种 mask 用途不同 | 生成必须用下三角 causal mask；变长 batch 另加 padding mask |
| 不加 mask 直接 softmax | 模型「作弊」，验证集指标异常好 | 看到未来 token | 因果任务一律传 `is_causal=True` 或自建上三角 mask |
| 认为 KV cache 对所有模型都适用 | 在 BERT 上找 KV cache | KV cache 只存在于自回归 decoder | BERT 是双向编码，没有增量生成的复用需求 |
| 把 MQA/GQA 当成精度优化 | 期待效果提升 | 它们本质是**用少量效果换显存与速度** | GQA 用于推理加速与省 KV cache，不是提精度手段 |
| 提高零样本能力靠「改结构」 | 改半天结构无效 | GPT-2/3 的能力来自数据与规模 + ICL | 优先改 prompt（few-shot）与数据，结构改进收益有限 |
| 认为 GPT-3 是单一模型 | 引用参数时前后矛盾 | GPT-3 是**一个模型系列** | 明确说「最大版本 175B」等具体口径 |
| 把 fine-tuning 当作 few-shot | 概念混用 | ICL 不更新参数 | few-shot/one-shot/zero-shot 属于 ICL，无梯度回传；fine-tuning 要更新参数 |

## 5. 面试问答

**Q1：请解释 self-attention 的计算过程，以及为什么需要 multi-head 和 $\sqrt{d_k}$ 缩放。**

<details>
<summary>参考答案</summary>

计算过程：输入 $X\in\mathbb{R}^{n\times d_{model}}$ 经三个线性投影得到
$Q=XW_Q,\ K=XW_K,\ V=XW_V$；用 $QK^{\top}$ 计算每个位置与其他所有位置的相似度，除以 $\sqrt{d_k}$，
经 softmax 归一化成注意力权重，再对 $V$ 加权求和，最后拼接多头结果并做输出投影。

multi-head 的作用：把表示空间切成 $h$ 个子空间并行做注意力，不同头可以捕捉不同类型的关系
（语法依赖、指代、局部邻近等），拼接后表达力强于单头，而总计算量与单头同维时基本相当。

缩放的作用：$Q\cdot K$ 的点积方差随 $d_k$ 线性增长，$d_k$ 较大时 softmax 输入进入饱和区，
梯度接近 0、训练不稳定；除以 $\sqrt{d_k}$ 把方差归一到 1 附近，保持梯度健康。

</details>

**Q2：GPT 与 BERT 的架构、训练目标、适用任务有什么不同？为什么现在的大模型几乎都是 decoder-only？**

<details>
<summary>参考答案</summary>

| 维度 | GPT | BERT |
|---|---|---|
| 架构 | Decoder-only，单向（只看左侧上文） | Encoder-only，双向 |
| 训练目标 | 自回归语言模型（预测下一个词） | MLM（15% token，80/10/10 替换）+ NSP |
| 擅长 | 自然语言生成 NLG：摘要、翻译、对话 | 自然语言理解 NLU：分类、情感分析、抽取式问答 |
| 微调方式 | 早期需为每个任务加分类层，GPT-3 起改为 ICL | 取 `[CLS]` 接分类层 |

统一到 decoder-only 的原因：① 训练效率与工程实现更简单，单一堆叠结构易扩展并行；
② 同等参数量与推理成本下 Decoder-only 性价比最高，encoder-decoder 的优势往往只是多了参数；
③ 生成任务只需要左侧上文，双向注意力并无实质收益，理论上还可能因低秩问题削弱表达能力；
④ 自回归天然适配 prompt / few-shot 的 in-context learning 使用方式。

</details>

**Q3：什么是 KV Cache？它为什么能加速，又为什么催生了 MQA/GQA？**

<details>
<summary>参考答案</summary>

KV Cache 缓存历史 token 在每层计算出的 key/value 张量。自回归生成第 $n+1$ 个 token 时，
前 $n$ 个 token 的 K/V 与上一次完全相同，因此无需重算，只需计算新 token 的 Q 并与缓存的 K/V 做注意力。
它只对自回归 decoder 有效（BERT 无此需求）。实测生成 1000 个 token，开启后约 11s，关闭约 56s。

代价：显存占用随「序列长度 × 层数 × 头数 × $d_k$ × 2(K和V)」线性增长，长上下文时成为瓶颈。
MQA 让所有 query 共享一套 K/V，最省显存但效果略降；GQA 把 query 分组共享 N 套 K/V，是 MHA 与 MQA 的折中，
在保留速度的同时让效果接近 MHA。Qwen2、Llama 3 等均在 8B/70B 规模上采用 GQA。

</details>

## 6. 自测题

**1. 原始 Transformer 的 Decoder Block 有哪三个子层？GPT 做了哪一处裁剪？**

<details>
<summary>参考答案</summary>

三个子层：① Masked Multi-Head Self-Attention；② encoder-decoder cross-attention；③ Feed Forward。
GPT 取消了第二个 cross-attention 子层，只保留 Masked Multi-Head Attention 与 Feed Forward，
因此不再需要独立的 encoder，成为纯 decoder-only 架构（GPT-1 堆叠 12 个这样的 block）。

</details>

**2. BERT 的 MLM 任务为什么要用 80%/10%/10% 的替换策略？**

<details>
<summary>参考答案</summary>

若把 15% 被选中的 token 全部替换为 `[MASK]`，预训练输入会大量出现 `[MASK]`，
而下游任务从未见过该符号，造成预训练与微调之间的**输入分布不一致（输入噪声）**。
改为 80% `[MASK]`、10% 随机词、10% 保持不变后，模型无法简单依赖 `[MASK]` 判断目标位置，
必须真正结合上下文，同时提升了对噪声输入的鲁棒性。

</details>

**3. 给定 $n=5,\ d_{model}=64,\ h=8$，写出多头注意力中 $Q$、单个头的 $Q_i$、注意力分数矩阵的形状。**

<details>
<summary>参考答案</summary>

$d_k = 64/8 = 8$。$Q$ 形状为 $(5, 64)$；切分并转置后单个头 $Q_i$ 为 $(5, 8)$；
注意力分数 $Q_iK_i^{\top}/\sqrt{d_k}$ 形状为 $(5, 5)$，全部头堆叠后为 $(8, 5, 5)$。

</details>

**4. RoPE 相比可学习绝对位置编码的核心优势是什么？**

<details>
<summary>参考答案</summary>

RoPE 通过把 Q/K 向量按两两一组做旋转，使两个位置向量的内积只依赖它们的**相对距离**，
因此天然编码相对位置信息，并具有更好的**外推性**（训练时较短、推理时较长的场景更友好）。
可学习绝对位置编码与序列位置强绑定，一旦超出训练长度就完全失效。

</details>

## 7. 延伸阅读

- [Attention Is All You Need (arXiv:1706.03762)](https://arxiv.org/abs/1706.03762)
- [BERT (arXiv:1810.04805)](https://arxiv.org/abs/1810.04805)
- [Language Models are Few-Shot Learners / GPT-3 (arXiv:2005.14165)](https://arxiv.org/abs/2005.14165)
- [《神经网络与深度学习》（邱锡鹏）](https://nndl.github.io/)

---

[⬅️ 返回本目录索引](README.md)
