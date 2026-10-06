---
article_id: "f5340ad3033e"
learning_kind: "reference"
learning_category: "06-llm"
---

# -DPO与免强化学习对齐


> **一句话总结**：DPO（Direct Preference Optimization）用一个恒等式把「带 KL 约束的 RLHF 目标」的最优解写出来，再把奖励反解成「策略与参考模型的对数比」，代回 Bradley-Terry 似然后得到一个人人可训的分类损失——它需要训练的模型从四个降到两个，训练流程也退化成类似 SFT 的一遍前向加反向。
> **前置知识**：Bradley-Terry 模型与排序损失、KL 散度、Sigmoid 与交叉熵、极大似然；读过第 01 篇（RLHF 与 KL 惩罚）和第 02 篇（奖励模型）会非常顺。
> **学完能做到**：1. 独立完成 DPO 的完整推导链——从带 KL 约束的目标写出最优策略的闭式解，反解出隐式奖励，代回 Bradley-Terry 似然消掉配分函数，最后得到 DPO 损失；2. 说明 $\beta$ 的物理含义（每单位对数比的价格）以及它取大取小分别会发生什么；3. 在 DPO / IPO / KTO / ORPO / cDPO 之间做出有依据的选型，并手写一个可运行的 DPO 损失实现。

## 1. 核心概念

### 1.1 从「训一个奖励模型」到「奖励就藏在策略里」

第 01、02 篇的路线是：先训奖励模型 $r_\phi$，再用 PPO 最大化 $r_\phi$ 同时用 KL 约束贴住 SFT 模型。DPO 的出发点是两个观察：

**观察一**：如果 KL 约束下的 RL 目标存在最优策略的闭式解，那么这个闭式解与奖励之间是一一对应的关系——给定奖励，最优策略唯一确定；反过来，给定最优策略和参考模型，奖励也可以被唯一确定（相差一个只依赖 $x$ 的常数）。

**观察二**：Bradley-Terry 偏好概率只依赖奖励的**差值**，所以那个只依赖 $x$ 的常数会在相减时约掉。

把两个观察合起来：**我们可以把「策略模型本身」当作奖励模型来用**——不需要再单独训练 RM。「Your Language Model is Secretly a Reward Model」这句话说的就是这件事。

```text
RLHF（间接路线）
  prompt → 采样回答 → 人类排序 → 训练 RM → PPO 用 RM 当奖励
  参与训练的模型: Actor + Critic；驻留模型: 4 个
  训练循环里有生成 → On-Policy → 慢

DPO（直接路线）
  prompt → 采样回答 → 人类排序 → 直接对策略做偏好优化
  参与训练的模型: 只有策略一个；驻留模型: 2 个（策略 + 冻结的参考）
  训练循环里没有生成 → Off-Policy → 与 SFT 同样快
```

### 1.2 一张表看懂 DPO 与 RLHF 的差别

| 维度 | RLHF（PPO） | DPO |
|---|---|---|
| 显式奖励模型 | 需要，单独训练 | 不需要（隐式奖励由 $\pi_\theta/\pi_{ref}$ 给出） |
| 驻留模型数 | 4（Actor / Critic / Reward / Reference） | 2（Policy / Reference） |
| 可训练模型数 | 2 | 1 |
| 需要生成（rollout） | 需要，每步都要自回归采样 | 不需要 |
| 训练速度 | 慢（生成是瓶颈） | 接近 SFT |
| 显存 | 高（约 $32P$ 字节，见第 01 篇） | 约 $16P$（策略训练态 + 参考推理态） |
| 稳定性 | 敏感（KL 系数、优势归一化、学习率） | 相对稳定，但对 $\beta$ 与数据质量敏感 |
| 数据性质 | On-Policy，训练中不断产生新数据 | Off-Policy，固定离线偏好数据集 |
| 理论最优性 | 在 RM 准确的假设下更接近真实目标 | 与 RLHF 同源，但受限于离线分布 |
| 最擅长 | 需要探索、需要在线纠偏、有可验证奖励的任务 | 有高质量偏好数据、算力受限、需要快速迭代的任务 |
| 主要风险 | reward hacking、训练崩溃、对齐税 | 正负样本质量差导致「好坏一起降」、长度偏置、多轮训练过拟合 |

### 1.3 DPO 的损失长什么样

$$-\log\sigma\left(\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\text{ref}}(y_w\mid x)}-\beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\text{ref}}(y_l\mid x)}\right)$$

把它读成一句话：**让策略在「好回答」上相对参考模型的对数概率增益，明显大于在「坏回答」上的增益**。注意是「相对参考模型的增益（对数比）」，不是绝对概率——这正是 KL 约束被内化进损失的方式。

### 1.4 DPO 家族一览

| 方法 | 核心动机 | 与 DPO 的差异 | 是否需要参考模型 |
|---|---|---|---|
| DPO | 把 KL 约束下的 RL 最优解代回 BT 似然 | 基线 | 需要 |
| cDPO / rDPO | 标注必然有噪声，硬标签会过拟合 | 把标签按概率 $\epsilon$ 翻转，即目标用 $(1-\epsilon)\sigma(\cdot)+\epsilon\sigma(-\cdot)$ | 需要 |
| IPO | DPO 在「偏好确定性」（$p(y_w\succ y_l)=1$）时会把对数比推向无穷，导致过拟合 | 把 log-sigmoid 换成对「对数比与 $1/(2\beta)$ 的差」的平方损失，有界 | 需要 |
| KTO | 实际数据常是「单个回答 + 好/坏标签」，未必成对 | 基于前景理论的价值函数（对损失更敏感），直接用二值标签 | 需要 |
| ORPO | 想连参考模型也省掉 | 损失 = SFT 损失（在 chosen 上算交叉熵）$+\ \lambda\cdot$ odds ratio 惩罚 | **不需要** |
| SimPO | 参考模型占显存，且长度未归一化 | 用回答的平均对数概率作为隐式奖励，并加长度归一化与目标间隔 $\gamma$ | **不需要** |
| DPOP | DPO 可能把 chosen 的概率也压低 | 在 DPO 上加一项正则，限制 chosen 的对数比不低于参考 | 需要 |
| TDPO | PPO 有逐 token 的 KL 惩罚，DPO 没有 | 在 DPO 上加逐 token 的前向 KL 惩罚 | 需要 |

### 1.5 $\beta$ 该取多少

$\beta$ 是 DPO 里最重要的旋钮，常见取值在 $0.1$–$0.5$ 之间（实现里也常见 $0.01$–$0.1$ 的小值）。它的语义是「每偏离参考模型一个单位的对数概率，需要付出 $\beta$ 的隐含代价」。取值影响见下表（详细推导见 2.5 节）。

| $\beta$ | 允许的策略偏移 | 训练表现 | 风险 |
|---|---|---|---|
| 过小（如 $0.01$） | 很大 | 损失很快下降，偏好差迅速拉大 | 迅速离开参考分布，过拟合偏好数据、语言能力退化、输出多样性塌缩 |
| 合适（如 $0.1$） | 中等 | 损失平稳下降，chosen 概率上升、rejected 下降 | 需要按数据量调整 |
| 过大（如 $1.0$ 以上） | 很小 | 损失下降缓慢，模型几乎不变 | 学不动，等价于白跑一轮；极端时会偏向参考模型本身 |

## 2. 数学推导

> **说明**：本节基于公开论文整理。

### 2.1 出发：带 KL 约束的 RLHF 目标

第 01 篇给出的 RLHF 目标（在固定 prompt $x$ 下写开）：

$$\max_{\pi}\ \mathbb{E}_{y\sim\pi(\cdot\mid x)}\Big[r(x,y)\Big]-\beta\, D_{KL}\Big(\pi(\cdot\mid x)\,\big\|\,\pi_{\text{ref}}(\cdot\mid x)\Big)$$

其中 $r$ 是（未知的）真实奖励，$\pi_{\text{ref}}$ 是参考策略（SFT 模型），$\beta>0$ 是 KL 惩罚系数。第一项希望奖励高，第二项希望别离参考太远。注意这里是**反向 KL**（期望在 $\pi$ 下取），它倾向于让 $\pi$ 集中到参考分布中奖励高的模式上——这被称为 mode-seeking，正是 RLHF 想让输出「变好」而不是「变多样」的原因。

### 2.2 关键一步：写出最优策略的闭式解

**第一步：把 KL 展开成可逐点处理的期望。**

$$D_{KL}\big(\pi\|\pi_{\text{ref}}\big)=\mathbb{E}_{y\sim\pi}\Big[\log\frac{\pi(y\mid x)}{\pi_{\text{ref}}(y\mid x)}\Big]$$

代入目标：

$$J(\pi)=\mathbb{E}_{y\sim\pi}\Big[r(x,y)-\beta\log\frac{\pi(y\mid x)}{\pi_{\text{ref}}(y\mid x)}\Big]=\sum_y \pi(y\mid x)\Big[r(x,y)-\beta\log\frac{\pi(y\mid x)}{\pi_{\text{ref}}(y\mid x)}\Big]$$

**第二步：把「求最优分布」变成一个逐点的变分问题。** 由于目标是对 $y$ 的可加求和，且 $\pi$ 只需满足 $\sum_y\pi(y\mid x)=1$，可以引入拉格朗日乘子 $\lambda(x)$：

$$\mathcal{L}(\pi,\lambda)=\sum_y \pi(y\mid x)\Big[r(x,y)-\beta\log\frac{\pi(y\mid x)}{\pi_{\text{ref}}(y\mid x)}\Big]+\lambda(x)\Big(\sum_y\pi(y\mid x)-1\Big)$$

**第三步：对每个 $\pi(y\mid x)$ 求偏导并令其为 0。**

$$\frac{\partial\mathcal{L}}{\partial\pi(y\mid x)}=r(x,y)-\beta\log\frac{\pi(y\mid x)}{\pi_{\text{ref}}(y\mid x)}-\beta+\lambda(x)=0$$

**第四步：解出 $\pi$。** 移项整理：

$$\beta\log\frac{\pi(y\mid x)}{\pi_{\text{ref}}(y\mid x)}=r(x,y)+\lambda(x)-\beta$$

$$\pi(y\mid x)=\pi_{\text{ref}}(y\mid x)\exp\!\Big(\frac{1}{\beta}\big[r(x,y)+\lambda(x)-\beta\big]\Big)$$

把与 $y$ 无关的因子 $\exp\big(\frac{\lambda(x)-\beta}{\beta}\big)$ 吸收进归一化常数，定义配分函数

$$Z(x)=\sum_y \pi_{\text{ref}}(y\mid x)\exp\!\Big(\frac{1}{\beta}r(x,y)\Big)$$

就得到

$$\boxed{\ \pi^*(y\mid x)=\frac{1}{Z(x)}\,\pi_{\text{ref}}(y\mid x)\exp\!\Big(\frac{1}{\beta}r(x,y)\Big)\ }$$

**这就是「Gibbs 分布形式」的最优策略：以参考分布为底，按奖励的指数做重加权。** 三个直观含义：

1. $\beta\to\infty$ 时指数项趋于均匀，$\pi^*\to\pi_{\text{ref}}$：惩罚太贵，索性不动。
2. $\beta\to 0$ 时指数项极端放大，$\pi^*$ 把全部质量压到 $\arg\max_y r(x,y)$：奖励至上。（这也解释了为什么 $\beta$ 是温度的角色。）
3. $\lambda(x)$ 被吸收进 $Z(x)$ 后消失了，**说明最优策略与「奖励的绝对水平」无关，只与奖励的相对形状有关**。

**注意 $Z(x)$ 的代价**：它需要对整个词表/整个回答空间求和，实际不可计算。DPO 的巧妙之处就在于后面会把它约掉。

### 2.3 反解隐式奖励（implicit reward）

把 $Z(x)$ 的表达式代入闭式解并取对数：

$$\beta\log\frac{\pi^*(y\mid x)}{\pi_{\text{ref}}(y\mid x)}=r(x,y)-\beta\log Z(x)$$

于是奖励可以被表示为

$$r(x,y)=\beta\log\frac{\pi^*(y\mid x)}{\pi_{\text{ref}}(y\mid x)}+\beta\log Z(x)$$

**因为 $Z(x)$ 只依赖 $x$，它对同一个 prompt 下的两条回答是同一个常数。** 定义隐式奖励（implicit reward）

$$\hat r_\theta(x,y)\triangleq \beta\log\frac{\pi_\theta(y\mid x)}{\pi_{\text{ref}}(y\mid x)}$$

即：**我们不再训练一个奖励模型，而是把「策略相对参考模型的对数比」本身当作奖励**。这句话是整篇文档的枢纽。

### 2.4 代回 Bradley-Terry 似然：配分函数为什么消失

第 02 篇给出的偏好概率（用隐式奖励替换真实奖励）：

$$p\big(y_w\succ y_l\mid x\big)=\sigma\Big(r(x,y_w)-r(x,y_l)\Big)=\sigma\Big(\hat r_\theta(x,y_w)+\beta\log Z(x)-\hat r_\theta(x,y_l)-\beta\log Z(x)\Big)$$

**两个 $\beta\log Z(x)$ 直接相消**：

$$p\big(y_w\succ y_l\mid x\big)=\sigma\Big(\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\text{ref}}(y_w\mid x)}-\beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\text{ref}}(y_l\mid x)}\Big)$$

**这就是配分函数消失的原因**：它只依赖 $x$，而成对比较恰恰只比较同一 $x$ 下的两条回答。**如果偏好数据跨 prompt 配对，这个消去就不成立，DPO 的理论基础也随之破裂**——这是 DPO 数据必须同 prompt 配对的硬性原因（与 RM 训练完全相同）。

对数据集取负对数似然，得到 DPO 损失：

$$\boxed{\ \mathcal{L}_{DPO}(\theta)=-\,\mathbb{E}_{(x,y_w,y_l)\sim\mathcal{D}}\left[\log\sigma\!\left(\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\text{ref}}(y_w\mid x)}-\beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\text{ref}}(y_l\mid x)}\right)\right]\ }$$

### 2.5 DPO 损失的另一种读法：一个带动态权重的加权分类损失

把对数比之差记作 $h_\theta(x,y_w,y_l)$，则损失是 logistic 损失。若把它改写成「等价于一个二分类问题」，可以看得更清楚：

定义 $\hat r_\theta$ 如 2.3 节，则

$$\mathcal{L}_{DPO}=-\log\sigma\big(\hat r_\theta(x,y_w)-\hat r_\theta(x,y_l)\big)$$

这看起来和「用 $\hat r_\theta$ 训练一个 RM」的损失完全一样，**区别只在于 $\hat r_\theta$ 不是自由参数化的打分函数，而是被策略的对数比唯一决定的**。所以 DPO 可以理解为「用策略本身充当奖励模型，并对其施加了参考模型的正则」。

### 2.6 梯度推导

记

$$u=\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\text{ref}}(y_w\mid x)}-\beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\text{ref}}(y_l\mid x)}$$

则 $\mathcal{L}=-\log\sigma(u)$，且 $\frac{\partial\mathcal{L}}{\partial u}=-\sigma(-u)$。又

$$\frac{\partial u}{\partial\theta}=\beta\Big(\nabla_\theta\log\pi_\theta(y_w\mid x)-\nabla_\theta\log\pi_\theta(y_l\mid x)\Big)$$

（$\pi_{\text{ref}}$ 与 $\theta$ 无关，所以它的项在求导时消失。）于是

$$\boxed{\ \nabla_\theta\mathcal{L}_{DPO}=-\,\beta\,\underbrace{\sigma\big(\hat r_\theta(x,y_l)-\hat r_\theta(x,y_w)\big)}_{\text{权重 }w}\Big(\nabla_\theta\log\pi_\theta(y_w\mid x)-\nabla_\theta\log\pi_\theta(y_l\mid x)\Big)\ }$$

**逐项解读这个梯度：**

| 因子 | 含义 |
|---|---|
| $w=\sigma\big(\hat r_\theta(y_l)-\hat r_\theta(y_w)\big)$ | 模型当前把顺序判错的程度；判得越准越小，判错越大越接近 1 —— 自动形成难例加权 |
| $\nabla_\theta\log\pi_\theta(y_w\mid x)$ | 提高好回答的对数概率 |
| $-\nabla_\theta\log\pi_\theta(y_l\mid x)$ | 降低坏回答的对数概率 |
| $\beta$ | 整体缩放：$\beta$ 越小，梯度幅度越小（因为 $u$ 被缩小），但**允许达到的偏移更大**（因为达到同样 $w$ 需要的对数比更大） |

**关键洞察**：梯度里**没有**任何「整体提高 chosen 概率」的显式项，只有「提高 chosen 相对于 rejected 的对数概率」。因此当 chosen 与 rejected 内容高度重合（只差一个 token 或一句话）时，DPO 可能同时压低两者的绝对概率，只是把 rejected 压得更低——这就是 2.7 节要讨论的失效模式。

### 2.7 DPO 的失效模式与 $\beta$ 的关系（自己推导）

**失效模式一：chosen 概率也被压低。** 因为损失只约束差值 $\hat r_\theta(y_w)-\hat r_\theta(y_l)$，任何让两者同时下降但差保持不变（或增大）的方向都不被惩罚。取 $y_l$ 与 $y_w$ 仅尾部不同的例子：降低共同前缀的概率会同时压低两个对数概率，若 $y_l$ 压得更多，损失反而下降。**后果是模型「越来越不会写这段文字」，只是更不倾向于写坏的版本。** 缓解手段是加入「chosen 上的 SFT 正则」（ORPO 的思路）或在 DPO 上加限制 chosen 对数比不低于参考的正则（DPOP 的思路）。

**失效模式二：偏好确定性导致无界。** 若数据中标注意味着 $y_w$ 绝对优于 $y_l$，则最优解会把 $u\to+\infty$，也就是对数比无界增长，模型彻底过拟合数据。IPO 用有界的平方损失替代 log-sigmoid 正是为此。

**$\beta$ 的定量角色。** 在闭式解里，$\beta$ 是「奖励的每单位价值所对应的对数比代价」。从

$$\hat r_\theta(x,y)=\beta\log\frac{\pi_\theta(y\mid x)}{\pi_{\text{ref}}(y\mid x)}$$

可以看出：**要达到同样的隐式奖励 $\hat r$，$\beta$ 越小，需要的对数比 $\log(\pi_\theta/\pi_{ref})$ 越大**，即模型必须离参考模型越远。因此：

| 现象 | $\beta$ 小 | $\beta$ 大 |
|---|---|---|
| 有效学习率（梯度中的 $\beta$ 因子） | 小 | 大 |
| 达到相同偏好差所需的对数比 | 大 | 小 |
| 隐式奖励的量纲（相对 RM 分数） | 被放大 | 被压缩 |
| 过拟合与能力退化风险 | 高 | 低 |
| 收敛速度 | 快（但可能一步跑太远） | 慢 |

**实践建议**：把 $\beta$ 与「数据量、正负样本的差异程度」一起调。样本差异很大（chosen 与 rejected 完全不同）时可以用较大 $\beta$；样本差异很小（只差一句话）时要用较小 $\beta$，同时监控 chosen 的绝对对数概率是否下降。

### 2.8 与 RLHF 目标的一致性：DPO 也最大化了同一个目标

代回验证一下。把隐式奖励代回 RLHF 的目标：

$$J(\pi_\theta)=\mathbb{E}_{y\sim\pi_\theta}\Big[\hat r_\theta(x,y)\Big]-\beta D_{KL}\big(\pi_\theta\|\pi_{\text{ref}}\big)$$

$$=\mathbb{E}_{y\sim\pi_\theta}\Big[\beta\log\frac{\pi_\theta(y\mid x)}{\pi_{\text{ref}}(y\mid x)}\Big]-\beta D_{KL}\big(\pi_\theta\|\pi_{\text{ref}}\big)$$

**注意这两项其实是同一个东西**：第一项就是 $\beta D_{KL}(\pi_\theta\|\pi_{\text{ref}})$，两者相减恒为 0。这不是巧合，而是「用最优解反解出的奖励」所满足的**自洽性条件**——只有在 $\pi_\theta=\pi^*$ 时该式才有意义。这也提醒我们：**DPO 的推导是「在最优解附近做重参数化」，它并不直接优化原始 RL 目标，而是优化一个 surrogate；因此它的理论保证依赖于「最优策略落在策略族内」这个假设。**

### 2.9 为什么 DPO 是 Off-Policy 且这为什么重要

DPO 的损失只用到固定数据集里的 $(y_w,y_l)$，训练过程中不生成新样本，所以是 Off-Policy。这带来两个直接推论：

1. **快**：一次前向 + 反向即可，不需要自回归生成。
2. **受限于分布匹配度**：损失中出现的 $y_w,y_l$ 必须「落在当前策略的合理范围内」。如果偏好数据是更强的模型生成的（分布外），DPO 会倾向于把当前策略往那个分布推，而它没有 RL 那种「自己探索、自己纠偏」的机制，可能出现模式塌缩或学不像。

这也解释了为什么实践中常用「多轮 DPO + 每轮用当前模型重新采样数据（拒绝采样或在线标注）」来弥补这一点，代价是回到了部分在线流程。

## 3. 可运行示例

`# 依赖：仅需 numpy（pip install numpy）。用 numpy 实现 DPO 损失与梯度并做梯度下降，策略用「对回答的小型表格分布」模拟，以便手算校验，不依赖 torch。`

```python
# 依赖：pip install numpy
"""DPO 损失、梯度与最小训练循环（纯 numpy）。

为便于校验，这里不走语言模型，而是把「策略对某个回答的概率」直接当作
可优化的参数（每个 (prompt, response) 一个 logit，经 softmax 归一化）。
这样 DPO 的每一项都能手工复算。
"""

import numpy as np

BETA = 0.1


def softmax(z):
    z = z - np.max(z)
    e = np.exp(z)
    return e / e.sum()


class ToyPolicy:
    """一个极简的"策略"：每个回答有一个 logit，概率 = 该 prompt 下的 softmax。"""

    def __init__(self, n_prompts, n_responses, seed=0):
        rng = np.random.default_rng(seed)
        self.logits = rng.normal(scale=0.1, size=(n_prompts, n_responses))
        self.ref_logits = self.logits.copy()   # 参考模型：初始策略的冻结副本

    def logp(self, p, r):
        return float(np.log(softmax(self.logits[p])[r]))

    def ref_logp(self, p, r):
        return float(np.log(softmax(self.ref_logits[p])[r]))

    def dlogp_dlogit(self, p, r):
        """d log pi(r|p) / d logit[p, k] = delta_{kr} - pi(k|p)。"""
        probs = softmax(self.logits[p])
        g = -probs
        g[r] += 1.0
        return g


def implicit_reward(policy, p, r, beta=BETA):
    """隐式奖励 r_hat = beta * log( pi_theta(y|x) / pi_ref(y|x) )。"""
    return beta * (policy.logp(p, r) - policy.ref_logp(p, r))


def dpo_loss_and_grad(policy, data, beta=BETA):
    """data: [(prompt_id, chosen_resp_id, rejected_resp_id), ...]"""
    n = len(data)
    total_loss = 0.0
    grad = np.zeros_like(policy.logits)
    for p, y_w, y_l in data:
        rw = implicit_reward(policy, p, y_w, beta)
        rl = implicit_reward(policy, p, y_l, beta)
        u = rw - rl
        # -log sigmoid(u)，数值稳定写法
        if u >= 0:
            loss = np.log1p(np.exp(-u))
        else:
            loss = -u + np.log1p(np.exp(u))
        total_loss += loss
        # 梯度权重 w = sigma(-u)
        w = 1.0 / (1.0 + np.exp(u))
        # dL/dtheta = -beta * w * (dlogpi_w - dlogpi_l)
        grad[p] += (-beta * w) * (
            policy.dlogp_dlogit(p, y_w) - policy.dlogp_dlogit(p, y_l)
        )
    return total_loss / n, grad / n


def accuracy(policy, data, beta=BETA):
    ok = 0
    for p, y_w, y_l in data:
        if implicit_reward(policy, p, y_w, beta) > implicit_reward(policy, p, y_l, beta):
            ok += 1
    return ok / len(data)


def main():
    n_prompts, n_responses = 6, 3
    policy = ToyPolicy(n_prompts, n_responses, seed=1)
    # 数据: 每个 prompt 让 chosen 固定比 rejected 好
    data = [(p, 0, 1) for p in range(n_prompts)] + \
           [(p, 1, 2) for p in range(n_prompts)]

    print("训练前准确率:", round(accuracy(policy, data), 3))
    lr = 0.5
    for step in range(1, 61):
        loss, grad = dpo_loss_and_grad(policy, data)
        policy.logits -= lr * grad
        if step % 15 == 0:
            print(f"step {step:3d}  DPO loss={loss:.4f}  acc={accuracy(policy, data):.3f}")

    print("\n各 prompt 的隐式奖励差 (chosen - rejected):")
    for p, y_w, y_l in data[:6]:
        d = implicit_reward(policy, p, y_w) - implicit_reward(policy, p, y_l)
        print(f"  prompt {p}  chosen={y_w} rejected={y_l}  "
              f"delta_r_hat = {d:+.4f}")

    # ---- 对照实验 1: beta 的影响 ----
    print("\n[对照] beta 对'学得多快/偏多远'的影响 (同样 60 步, lr=0.5):")
    for beta in (0.02, 0.1, 0.5):
        pol = ToyPolicy(n_prompts, n_responses, seed=1)
        for _ in range(60):
            _, g = dpo_loss_and_grad(pol, data, beta=beta)
            pol.logits -= lr * g
        logratio = pol.logp(0, 0) - pol.ref_logp(0, 0)
        dr = implicit_reward(pol, 0, 0, beta) - implicit_reward(pol, 0, 1, beta)
        print(f"  beta={beta:<4} acc={accuracy(pol, data, beta):.3f}  "
              f"log_ratio(chosen)={logratio:+.3f}  delta_r_hat={dr:+.4f}")

    # ---- 对照实验 2: 梯度权重的难例效应 ----
    print("\n[对照] 梯度权重 w = sigmoid(-u):")
    for u in (-3.0, -1.0, 0.0, 1.0, 3.0):
        print(f"  u={u:+.1f} -> w={1/(1+np.exp(u)):.4f}")


if __name__ == "__main__":
    main()
```

**代码与公式的对应关系：**

| 代码 | 公式 |
|---|---|
| `implicit_reward` | $\hat r_\theta(x,y)=\beta\log\frac{\pi_\theta(y\mid x)}{\pi_{ref}(y\mid x)}$ |
| `u = rw - rl` | $\hat r_\theta(y_w)-\hat r_\theta(y_l)$ |
| 分段 `loss` | 数值稳定的 $-\log\sigma(u)$ |
| `w = 1/(1+exp(u))` | $\sigma(-u)$，DPO 梯度中的动态权重 |
| `grad[p] += -beta*w*(dlogp_w - dlogp_l)` | $\nabla_\theta\mathcal{L}_{DPO}$ |
| 对照实验 1 | 同一 $\beta$ 下 log 比与隐式奖励的此消彼长 |
| 对照实验 2 | 难例加权：$u$ 越负（判错越狠），权重越接近 1 |

## 4. 常见坑

| 坑 | 现象 | 原因 | 正确做法 |
|---|---|---|---|
| 正负样本质量差 | loss 下降但人工评估不变甚至变差 | chosen 本身不够好（如也是模型生成的低质样本），rejected 又不够差 | chosen 用人工撰写或多次采样中筛选的优质样本；rejected 要「合理但不好」，不能是乱码 |
| 正负样本差异过大 | 训练极快，但模型变得生硬、复读、过度模板化 | 数据偏好过于容易区分，模型只学到表面差异（长度、格式） | 构造「难负样本」（与 chosen 只差关键一步）；长度匹配 |
| 跨 prompt 配对 | 损失能降但效果差，理论前提被破坏 | $Z(x)$ 无法消去 | 严格同 prompt 配对，并按 prompt 划分数据 |
| $\beta$ 太小 | chosen 概率先升后降，输出变短、语言能力退化 | 策略被允许离参考太远，过拟合数据 | 从 $0.1$ 起步扫参；监控 chosen 的绝对对数概率与 KL |
| $\beta$ 太大 | loss 几乎不动，模型与 SFT 无异 | 参考惩罚过强 | 调小 $\beta$；确认参考模型与策略同源且初始时 loss 合理（$u\approx0$） |
| 参考模型与策略不同源 | 训练开始 loss 就异常低或异常高 | 初始时隐式奖励不是 0 附近，梯度方向被错误偏置 | 参考模型必须是策略的冻结初始化副本 |
| 学习率沿用 SFT 的 | 训练几步就发散或塌缩 | DPO 的梯度尺度被 $\beta$ 缩放，与 SFT 不同 | DPO 学习率通常比 SFT 小一到两个数量级；先用小步数观察 |
| 只训一轮 vs 多轮 | 一轮欠拟合，多轮过拟合且越来越像参考模型 | 离线数据只能提供有限的分布覆盖，多轮会反复咀嚼同一批数据 | 一到三轮通常足够；如果要更多轮，每轮用当前策略重新采样数据（近似在线） |
| 长度偏置未处理 | 策略学会把回答写长（或写短） | 对数概率是逐 token 求和，长度天然放大/缩小对数比 | 用长度归一化的隐式奖励（SimPO 思路）或长度匹配的数据 |
| chosen 概率被同时压低 | 模型「越来越不会写」，回答变得空洞 | 损失只约束差值，不约束 chosen 的绝对水平 | 加 chosen 的 SFT 正则（ORPO 思路）或加限制 chosen 对数比的正则（DPOP 思路） |
| 数学/代码任务上直接用 DPO | 效果不如规则奖励的 RL | 偏好数据无法表达「答案对不对」这种客观信号 | 可验证任务优先用规则奖励 + RL；DPO 用于风格、语气、格式类偏好 |
| 未做 KL 与多样性监控 | 输出千篇一律，评测分数先涨后跌 | 无从发现分布塌缩 | 监控 KL、unique n-gram、熵、以及固定 prompt 集合的输出差异 |

## 5. 面试问答

**Q1：请完整推导 DPO 的损失函数。**

<details markdown="1">
<summary markdown="1">参考答案</summary>

四步。

① 出发点：带 KL 约束的 RL 目标 $\max_\pi\mathbb{E}_{y\sim\pi}[r(x,y)]-\beta D_{KL}(\pi\|\pi_{ref})$。

② 求闭式解。把 KL 展开成 $\sum_y\pi(y\mid x)\left[r(x,y)-\beta\log\frac{\pi(y\mid x)}{\pi_{ref}(y\mid x)}\right]$，加上归一化约束的拉格朗日乘子 $\lambda(x)$，对每个 $\pi(y\mid x)$ 求偏导令零，解得 $\pi^*(y\mid x)=\frac{1}{Z(x)}\pi_{ref}(y\mid x)\exp\left(\frac{1}{\beta}r(x,y)\right)$，其中 $Z(x)=\sum_y\pi_{ref}(y\mid x)\exp\left(\frac{1}{\beta}r(x,y)\right)$。

③ 反解奖励：对上式取对数得 $r(x,y)=\beta\log\frac{\pi^*(y\mid x)}{\pi_{ref}(y\mid x)}+\beta\log Z(x)$。定义隐式奖励 $\hat r_\theta(x,y)=\beta\log\frac{\pi_\theta(y\mid x)}{\pi_{ref}(y\mid x)}$，即把策略与参考的对数比本身当成奖励。

④ 代回 Bradley-Terry 似然 $p(y_w\succ y_l)=\sigma(r_w-r_l)$，注意 $r_w-r_l=\hat r_\theta(y_w)-\hat r_\theta(y_l)$，因为 $\beta\log Z(x)$ 在两条回答上是同一个常数、相减即消。取负对数似然即得 DPO 损失：

$$\mathcal{L}_{DPO}=-\mathbb{E}\left[\log\sigma\!\left(\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{ref}(y_w\mid x)}-\beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{ref}(y_l\mid x)}\right)\right]$$

补充一点理论诚实性：这个推导把「最优策略落在策略族内」当作假设，因此 DPO 优化的是一个 surrogate，不等于直接优化原始 RL 目标。

</details>

**Q2：$\beta$ 的物理含义是什么？取太小或太大会发生什么？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

物理含义：$\beta$ 是「KL 约束的价格」，也就是「每偏离参考模型一个单位对数概率所需付出的代价」。从闭式解 $\pi^*\propto\pi_{ref}\exp(r/\beta)$ 看，$\beta$ 是温度——越小越激进地追逐奖励，越大越贴近参考。也可以从隐式奖励 $\hat r=\beta\log(\pi_\theta/\pi_{ref})$ 看：要达到同样的隐式奖励，$\beta$ 越小就需要越大的对数比，也就是离参考越远。

取太小：允许的偏移很大，损失下降快，但迅速离开参考分布，过拟合偏好数据，正负样本的表面差异（长度、格式）被放大，chosen 概率可能被同时压低，语言能力退化。

取太大：策略几乎不动，损失下降缓慢，等价于白跑一轮。

实践：从 $0.1$–$0.5$ 起步，结合数据量、正负样本差异程度一起调；同时监控 chosen 的绝对对数概率（不能持续下降）、KL 散度与输出多样性。差异小的样本用更小的 $\beta$。

</details>

**Q3：DPO 与 RLHF 各自的适用场景是什么？为什么不干脆全用 DPO？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

DPO 适合：有高质量离线偏好数据、算力有限、需要快速迭代、偏好主要体现在风格/语气/格式/安全性上、以及不想维护 PPO 那套四模型基础设施的场景。它的训练成本接近 SFT，稳定性也更好。

RLHF（PPO/GRPO）适合：任务需要「探索」和在线纠偏；有可验证奖励（数学、代码）可以绕过神经 RM；偏好数据难以一次性覆盖策略可能走偏的所有方向；以及需要显式控制 KL 与奖励权衡的场景。On-Policy 的本质优势是训练数据始终与当前策略匹配。

不应该全用 DPO 的原因：① DPO 是 Off-Policy，理论上限受离线数据分布匹配度限制；② 它不显式建模奖励，因此无法像 RM 那样被独立评估、复用或做集成；③ 在需要搜索/探索的任务上，它能达到的效果通常不如带可验证奖励的 RL；④ DPO 的隐含假设（最优策略在策略族内、偏好数据同分布）在实践中常被违反。

实践中常见的组合是：先用 SFT 打底，再用 DPO 做一轮性价比很高的偏好对齐，然后用带规则奖励的 RL（如 GRPO）在推理类任务上继续提升。

</details>

**Q4：写出 DPO 的梯度并解释其中的「动态权重」。**

<details markdown="1">
<summary markdown="1">参考答案</summary>

记 $u=\hat r_\theta(x,y_w)-\hat r_\theta(x,y_l)$，则

$$\nabla_\theta\mathcal{L}_{DPO}=-\beta\,\sigma(-u)\Big(\nabla_\theta\log\pi_\theta(y_w\mid x)-\nabla_\theta\log\pi_\theta(y_l\mid x)\Big)$$

动态权重是 $\sigma(-u)$，即模型当前把偏好顺序判错的程度：当模型严重判错（$u\ll0$）时权重接近 1，梯度最大；当模型已经很笃定（$u\gg0$）时权重接近 0，梯度几乎为零。因此 DPO 会自动把学习集中在难例上，形式与逻辑回归的梯度完全一致。

对比 SFT：SFT 的梯度是无权重的 $\nabla_\theta\log\pi_\theta(y_w)$，只提高好回答的绝对概率；DPO 的梯度是加权的差值，只提高好回答相对坏回答的对数概率，代价是可能同时压低两者的绝对概率（这就是 DPOP/ORPO 要修的问题）。

另一个值得指出的点：$\beta$ 既出现在 $u$ 里（影响权重与饱和速度），又乘在梯度外面——所以调 $\beta$ 会同时改变「学多快」和「能偏多远」两件事，不能当成单纯的学习率缩放。

</details>

## 6. 自测题

**1. 为什么 DPO 的配分函数 $Z(x)$ 可以消掉？如果偏好数据跨 prompt 配对会发生什么？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

代回 Bradley-Terry 时，两条回答的奖励差为

$$r(x,y_w)-r(x,y_l)=\left[\beta\log\frac{\pi^*(y_w\mid x)}{\pi_{ref}(y_w\mid x)}+\beta\log Z(x)\right]-\left[\beta\log\frac{\pi^*(y_l\mid x)}{\pi_{ref}(y_l\mid x)}+\beta\log Z(x)\right]$$

$\beta\log Z(x)$ 只依赖 $x$，在同一 prompt 的两条回答上完全相同，相减即为 0。这正是 DPO 不需要计算不可处理的 $Z(x)$ 的原因。

如果跨 prompt 配对（$y_1$ 来自 $x_1$，$y_2$ 来自 $x_2$），两个 $Z$ 不相等，相减后留下 $\beta\log\frac{Z(x_1)}{Z(x_2)}$，无法消去；同时奖励差里还混进了「任务难度差」。这会使损失不再对应任何有效的偏好模型，理论保证失效，实践中表现为损失能降但泛化很差。所以 DPO 与 RM 训练一样，必须严格同 prompt 配对。

</details>

**2. 某次 DPO 训练中观察到：loss 从 0.69 降到 0.05，但人工评估变差，输出变短且套话变多。请给出三条最可能的原因与对应处理。**

<details markdown="1">
<summary markdown="1">参考答案</summary>

① $\beta$ 太小导致策略离参考太远、过拟合偏好数据。处理：调大 $\beta$（例如 $0.1\to0.3$），并监控 chosen 的绝对对数概率是否在下降。

② 偏好数据里 chosen 与 rejected 的差异是表面性的（长度、格式、套话），模型学到的正是这些捷径。处理：检查分数与长度/格式的相关性；构造长度匹配的难负样本；把「简洁但准确」纳入 chosen 的构成。

③ 训练轮数过多，反复咀嚼同一批离线数据。处理：减少轮数（一到三轮），或每轮用当前模型重新采样数据，转为近似在线。

此外还可能是参考模型与策略不同源，导致初期的隐式奖励就有系统性偏置，使梯度一开始就朝错误方向走——这类问题表现为训练一开始 loss 就异常低。

</details>

**3. 计算：$\beta=0.1$，$\log\frac{\pi_\theta(y_w)}{\pi_{ref}(y_w)}=-0.4$，$\log\frac{\pi_\theta(y_l)}{\pi_{ref}(y_l)}=-0.9$。求 $\hat r_\theta(y_w)$、$\hat r_\theta(y_l)$、$u$、DPO 损失与梯度权重。**

<details markdown="1">
<summary markdown="1">参考答案</summary>

$\hat r_\theta(y_w)=\beta\times(-0.4)=-0.04$；$\hat r_\theta(y_l)=\beta\times(-0.9)=-0.09$。

$u=-0.04-(-0.09)=0.05$。

损失 $=-\log\sigma(0.05)=-\log\frac{1}{1+e^{-0.05}}$。$\sigma(0.05)\approx0.5125$，故损失 $\approx0.6686$。（对照：模型完全无偏好时 $u=0$，损失为 $\ln 2\approx0.6931$，可见此处只是略微判对。）

梯度权重 $=\sigma(-u)=\sigma(-0.05)\approx0.4875$。

**注意**：这里两条回答相对参考的对数概率都是负的，说明当前策略对**两者**的偏好都低于参考模型。这正是 2.7 节讨论的失效模式——损失只关心差值，不关心绝对水平，所以 DPO 有可能让 chosen 的绝对概率持续下降。

</details>

**4. ORPO 和 SimPO 都去掉了参考模型，它们各自是怎么做到的？代价是什么？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

ORPO：损失 = 在 chosen 上计算的 SFT 交叉熵损失 $+\ \lambda\times$ odds ratio 惩罚。核心在于那个 SFT 项本身起到了「锚住 chosen 分布」的作用，替代了参考模型的角色；odds ratio 惩罚则承担「拉开好坏差距」的职责。代价是失去了对着参考模型的显式约束，无法直接控制 KL 偏移，只能靠 $\lambda$ 与学习率间接约束。

SimPO：直接用「回答的平均对数概率」作为隐式奖励（即 $\frac{1}{|y|}\log\pi_\theta(y\mid x)$），并加上目标间隔 $\gamma$（要求 chosen 的隐式奖励比 rejected 高出至少 $\gamma$）。去掉参考模型的同时，长度归一化也顺带缓解了 DPO 的长度偏置问题。代价同样是失去显式 KL 锚点，且平均对数概率这个奖励的形式与真实偏好是否匹配需要任务验证。

KTO 也值得一提：它面向「单个回答 + 好/坏标签」的场景，用前景理论的价值函数（对损失更敏感）替代成对比较，但通常**仍需**参考模型来计算对数比。

</details>

**5. 什么情况下你会放弃 DPO，改回 RL？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

① 任务有可验证奖励（数学答案、代码单测、工具调用是否成功）。这类任务的偏好不该由人类主观判断，规则奖励更准、更便宜、抗 hack，而 DPO 无法把「答案对错」写进离线偏好对里。

② 需要探索：策略需要学会「先思考再回答」这类无法从现有数据中模仿的行为，必须靠采样 + 奖励反馈来发现，On-Policy 的 RL 是唯一途径（这也是 DeepSeek-R1 类路线的核心）。

③ 偏好数据覆盖不足：离线数据的分布在策略应该去的方向上很稀疏，DPO 会模式塌缩。

④ 需要显式控制奖励—KL 权衡：RL 里 $\beta_{KL}$ 是一个可扫描、可监控、可在训练中动态调整的旋钮；DPO 的 $\beta$ 虽然数学角色类似，但缺少在线反馈来校准。

⑤ 需要奖励模型被独立评估、复用或集成：RL 路线把 RM 显式化，可以单独测准确率、做集成、做不确定性惩罚；DPO 把奖励隐式化了，这些工具就失去了立足点。

</details>

## 7. 延伸阅读

- [Direct Preference Optimization: Your Language Model is Secretly a Reward Model (DPO, arXiv:2305.18290)](https://arxiv.org/abs/2305.18290)
- [A General Theoretical Paradigm to Understand Learning from Human Preferences (IPO, arXiv:2310.12036)](https://arxiv.org/abs/2310.12036)
- [KTO: Model Alignment as Prospect Theoretic Optimization (arXiv:2402.01306)](https://arxiv.org/abs/2402.01306)
- [ORPO: Monolithic Preference Optimization without Reference Model (arXiv:2403.07691)](https://arxiv.org/abs/2403.07691)
- [Training language models to follow instructions with human feedback (InstructGPT, arXiv:2203.02155)](https://arxiv.org/abs/2203.02155)

---

[⬅️ 返回本章目录](README.md)
