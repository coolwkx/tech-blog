---
article_id: "eeb0dcb17743"
learning_kind: "reference"
learning_category: "06-llm"
---

# -RAG评估与优化


> **一句话总结**：RAG 优化不是「炼丹」而是科学实验——先用 RAGAS 这类框架把**检索**与**生成**两个环节量化成 0~1 的指标，再用「生成代理 + 质量评审代理 + 评估代理」自动造出高质量评估集，最后靠指标对比来判断每一次改动是否真的有效。
> **前置知识**：RAG 完整链路（见《09-RAG系统构建》）、LLM 调用与 Prompt 设计（见《04-提示词工程》）、embedding 与余弦相似度。
> **学完能做到**：1. 用 RAGAS 跑出忠实度/答案相关性/上下文相关性/上下文召回率四个指标；2. 自动生成并过滤出高质量的 RAG 评估数据集；3. 看懂指标异常，定位问题出在检索侧还是生成侧。

## 1. 核心概念

### 1.1 为什么必须先评估

当我们为真实线上系统开发了 RAG 应用，**在上线前需要评估 RAG 的表现**；如果效果不理想，可能需要新的 RAG 算法流程来改进——
但**在这之前必须先得到评估指标，才能做自动化对比，观察改进的流程是否真的有效**。

反模式（的批评）：很多人采取「试错」方法——「我尝试了一个新模块，问了几个问题，答案看起来还行……」。
这种定性评估方式虽然直观，但**很难得出可靠的改进结论**。

| 维度 | 定性试错 | 系统化评估 |
|---|---|---|
| 依据 | 主观感受、少量问题 | 量化指标 + 固定数据集 |
| 可比较性 | 不同版本无法比较 | 同一数据集横向对比 |
| 结论可靠性 | 低（受个例与随机性影响） | 高（统计意义） |
| 迭代效率 | 容易在无效改动上浪费大量时间 | 每个调整都有量化依据 |

**核心方法论**：优化 RAG 需要采用科学实验的方式——**设计量化评估指标 + 准备高质量评估数据集**。

### 1.3 RAGAS 是什么

**RAGAS (Retrieval Augmented Generation Assessment)**，一般称为 **Automated Evaluation of Retrieval Augmented Generation**，
即**检索增强生成的自动评估**。它是一个大模型评测框架，可以评估 RAG 的效果、帮助分析模型输出、了解模型在给定任务上的表现。
（GitHub: `explodinggradients/ragas`）

**最重要的设计取向**：最开始的 RAGAS 在评估数据集时**不必依赖人工标注的标准答案**，而是通过底层的大语言模型（LLM）来评估。
因此只需要一个带问题-答案对的评估数据集（QA 对）即可起步。

### 1.4 评估数据集字段

| 字段 | 含义 | 来源 |
|---|---|---|
| `question` | 作为 RAG 管道输入的用户查询 | 输入 |
| `answer` | 从 RAG 管道生成的答案 | 输出 |
| `contexts` | 从外部知识源中检索到的、用于回答该问题的上下文 | RAG 中间产物 |
| `ground_truths` | question 的基本事实答案 | **唯一需要人工注释的信息** |

**关键细节**：`contexts` **必须是列表**，即使每个问题只对应一段上下文，也要写成 `["context text"]`。
这是最容易踩的格式坑。

## 2. 关键机制

### 2.1 四个核心指标：作用与计算

#### ① 上下文相关性（context relevance）

| 项 | 说明 |
|---|---|
| 作用 | 检索到的上下文**应该只包含回答问题所需的信息**，该指标旨在**惩罚包含冗余信息**的情况 |
| 方向 | 比率越高，表示检索到的上下文与问题的相关性越强 |
| 计算思路 | 用 LLM 从上下文 $C(q)$ 中抽取对回答问题 $q$ 至关重要的句子 $S$，再计算抽取比例 |

抽取用的 prompt（可直接复用）：

```text
请从提供的{上下文}中提取可能有助于回答以下{问题}的相关句子。
如果没有找到相关句子，或者你认为问题无法从给定上下文中得到回答，则返回短语"信息不足"。
在提取候选句子时，你不得更改给定上下文中的句子。
```

> 「不得更改给定上下文中的句子」这条约束很关键——它保证抽取是**可核验的选取**而不是**改写**，
> 否则指标会失去客观性。

#### ② 上下文召回率（context recall）

| 项 | 说明 |
|---|---|
| 作用 | 衡量检索到的上下文（contexts）与真实答案（ground_truths）的**匹配程度** |
| 计算 | 通过问题、标注答案和检索到的上下文计算，**分数范围 0~1，越高越好** |
| 公式 | $\text{ContextRecall}=\dfrac{\text{GT claims that can be attributed to context}}{\text{Number of claims in GT}}$ |

分子是「真实答案中的论断中，有多少可以归因于检索到的上下文」（即在上下文中找到支持）；
分母是「真实答案中论断的总数量」。**理想情况下真实答案中的所有声明都应可归因于检索到的上下文**。

给的完整算例：

| 项 | 内容 |
|---|---|
| 真实答案 | ①「2010 年世界杯的冠军是西班牙。」②「西班牙在决赛中以 1-0 击败了荷兰。」 |
| 检索到的上下文 | ①「西班牙在 2010 年世界杯的决赛中击败了荷兰。」②「2010 年世界杯的冠军是西班牙，西班牙队首次赢得世界杯。」 |
| 声明 1 | 「2010 年世界杯的冠军是西班牙。」→ 上下文包含该信息 → **召回** |
| 声明 2 | 「西班牙在决赛中以 1-0 击败了荷兰。」→ 上下文提到击败荷兰，**但未提到比分 1-0** → **未召回** |
| 结果 | 总声明 2、被召回 1 → $\text{Context Recall}=0.5$ |

> 这个算例说明：**上下文召回率对细节极其敏感**。同一件事，"提到过"和"提到具体比分"是两种不同的召回。

#### ③ 忠实度（faithfulness）

| 项 | 说明 |
|---|---|
| 作用 | 答案确实是根据给定的上下文得到的；对于**避免错觉**并确保检索到的上下文能作为生成依据非常重要 |
| 分数低意味着 | LLM 的回应**没有遵循检索到的知识，提供幻觉式答案的可能性增加** |
| 公式 | $F=\lvert V\rvert / \lvert S\rvert$，$\lvert V\rvert$ 为 LLM 支持的陈述数量，$\lvert S\rvert$ 为陈述总数 |

**两步实现**：

**第一步**：用 LLM 从答案中提取一组陈述 $S(a(q))$：

```text
给定一个问题和答案，从给定答案的每个句子中创建一个或多个陈述。
问题：[问题]
答案：[答案]
```

**第二步**：判断每个陈述 $s_i$ 是否可从上下文 $c(q)$ 推断出来：

```text
考虑给定的上下文和以下陈述，然后确定它们是否由上下文中的信息支持。
在得出结论（是/否）之前，为每个陈述提供简要解释。
在最后以给定格式为每个陈述提供最终结论。不要偏离指定的格式。
陈述：[陈述 1]
...
陈述：[陈述 n]
```

> 注意第二步要求「在得出结论之前，为每个陈述提供简要解释」——这是让 LLM 先推理再判断，
> 与《04-提示词工程》里「给模型充足思考时间」是同一个技巧，能显著提升评判一致性。

#### ④ 答案相关性（answer relevancy）

| 项 | 说明 |
|---|---|
| 作用 | 生成的答案与查询之间的相关性，**分数越高相关性越好** |
| 计算思路 | **反向生成问题**：让 LLM 根据答案生成 n 个「这个答案可能在回答什么问题」，再与原问题比相似度 |

实现步骤：
1. 对给定答案，提示 LLM 生成基于该答案可能的 $n$ 个问题 $q_i$（prompt：`为给定答案生成一个问题。答案：[答案]`）；
2. 使用 **embedding 模型**获取所有问题的嵌入表示；
3. 对每个生成的问题 $q_i$，计算它与原始问题 $q$ 的相似度 $\mathrm{sim}(q,q_i)$——
 这里的相似度通过计算对应**嵌入之间的余弦相似度**得到；
4. 答案相关性得分 AR = 这些相似度的**平均值**。

**为什么用「反向生成问题」而不是直接问 LLM「这个答案切题吗」**：
反向生成把「主观判断」变成了「可量化的向量相似度」，避免评估模型的评分偏好影响结果，
同时能捕捉到「答案是正确知识但答非所问」这种情况。

### 2.2 四个指标的判读：定位问题出在哪一侧

| 现象 | 推断 | 应该动哪里 |
|---|---|---|
| 忠实度高、上下文召回率低 | 模型老实（没编），但**这里没找全** | 改进检索：切片粒度、混合检索、Query 改写、增大 `retrieval_k` |
| 忠实度低、上下文召回率高 | 够了，但模型**没用**（幻觉） | 改进生成：Prompt 约束「依据材料作答」、降低 `temperature`、换更强模型 |
| 上下文相关性低 | 检索结果里**冗余/无关内容多** | 改进检索精度：重排序、减小 `candidate_m`、加 `filter` 过滤 |
| 答案相关性低 | 答案**东拉西扯、答非所问** | 改进 Prompt 的任务描述与输出格式约束 |
| 四项都不错但业务不满意 | 指标覆盖不到的方面（语气、合规、时效） | 补充自定义指标或人工抽检 |

**这张表是评估体系最大的实用价值**：把「效果不好」这个模糊感受，转换成「该修检索还是该修生成」的具体行动。

### 2.4 用 RAGAS 跑评估：代码结构

`ragas_evaluate.py` 的五个步骤：

| 步骤 | 做什么 |
|---|---|
| ① 数据集加载 | 从 JSON 加载包含 question / answer / context / ground_truth 的评估数据集 |
| ② 数据格式转换 | 转换为 RAGAS 要求的 `Dataset` 格式 |
| ③ 环境配置 | 用 LangChain 的 OpenAI 模型与嵌入模型初始化 RAGAS 评估环境 |
| ④ 评估执行 | 计算 faithfulness、answer_relevancy、context_relevancy、context_recall |
| ⑤ 结果输出 | 打印并保存为 CSV，便于统计分析和多次运行比较 |

```python
# 依赖：pip install ragas datasets langchain-openai pandas
import json
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_relevancy, context_recall
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
```

**三个配置要点**：
① `ChatOpenAI` 用于生成评估所需的推理（如判断忠实度），需指定模型与 API Key；
② `OpenAIEmbeddings` 用于计算语义相似度（如答案相关性）；
③ **可替换为其他 LLM（如通义千问），只需适配 LangChain 的模型接口**——这意味着国内环境完全可以用
DashScope / 本地 Ollama 替代，不必依赖 OpenAI。

**结果示例**（字典，各指标 0~1，1 为最佳）：

```python
{'faithfulness': 0.95, 'answer_relevancy': 0.92, 'context_relevancy': 0.90, 'context_recall': 0.93}
```

结果保存为 CSV（`ragas_evaluation_results.csv`）的价值在于：**多次运行可横向比较**，
从而判断「这次改动到底有没有提升」。代码结构通用，可用于任何 RAG 系统评估，只需替换数据集与 LLM 配置；
也可扩展指标（如 `answer_correctness`）或添加自定义数据处理逻辑（如过滤低质量数据）。

## 3. 可运行示例

```python
# 依赖：pip install ragas datasets langchain-openai pandas
import json, os
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_relevancy, context_recall
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

with open("rag_evaluation_dataset.json", encoding="utf-8") as f:
 data = json.load(f) # [{"question","answer","context":[...],"ground_truth"}, ...]

dataset = Dataset.from_dict({
 "question": [d["question"] for d in data],
 "answer": [d["answer"] for d in data],
 "contexts": [d["context"] for d in data], # 必须是 list，即使只有一条
 "ground_truth": [d["ground_truth"] for d in data],
})

# 可换成 DashScope / 本地 Ollama 的 OpenAI 兼容端点
llm = ChatOpenAI(model="gpt-4", api_key=os.environ["OPENAI_API_KEY"])
embeddings = OpenAIEmbeddings(api_key=os.environ["OPENAI_API_KEY"])

result = evaluate(dataset=dataset,
 metrics=[faithfulness, answer_relevancy, context_relevancy, context_recall],
 llm=llm, embeddings=embeddings)
print(result)
pd.DataFrame([result]).to_csv("ragas_evaluation_results.csv", index=False) # 多次运行横向对比
```

## 4. 常见坑

| 坑 | 现象 | 原因 | 正确做法 |
|---|---|---|---|
| `contexts` 传字符串 | RAGAS 报格式错误 | 该字段**必须是列表** | 即使只有一段上下文也写成 `["..."]` |
| 缺少 `ground_truths` | `context_recall` 无法计算 | 该指标需要真实答案 | 至少为 `context_recall` 准备人工标注答案（唯一必须人工的部分） |
| 用自己的模型当评估模型 | 指标偏高、看不出问题 | 自评自夸有偏见 | 用更强的第三方模型（GPT-4）或开源评判模型（Prometheus、JudgeLM） |
| 评估 Prompt 没有评分细则 | 同一份数据多次跑分数波动大 | 标准模糊导致评分漂移 | 给出 1~5 分 rubric，并在输出中用 `[RESULT]` 固定抽取位置 |
| 让评估模型直接给分 | 分数无法解释、难以复核 | 缺少推理过程 | **先输出理由再给分**，理由用于核验一致性 |
| 评估样本量太小 | 指标波动、结论不可靠 | 统计噪声 | 针对特定知识库生成 **≥200 条**，过滤后约保留一半 |
| 测试问题里带「根据上文」 | 检索指标虚高 | 问题泄露了上下文依赖 | 生成时约束 `MUST NOT mention "according to the passage"` |
| 不做质量过滤 | 有歧义/无答案的样本混入 | 自动生成质量参差 | 引入 Critic Agent 三维打分，任一维过低直接剔除 |
| 训练/评估数据类别不均衡 | 分类器偏向多数类、指标虚高 | 数据分布偏斜 | 两类等量生成（如各 3000 条），并 shuffle |
| 只跑一次评估就下结论 | 无法判断改动是否有效 | 没有对照 | 固定同一评估集，**每次只改一个变量**，结果落 CSV 横向对比 |
| 四个指标只看总分 | 不知道该修哪 | 缺少归因 | 按「忠实度低→修生成；召回低→修检索」的映射定位 |
| 用 `context_relevancy` 判断答案对错 | 指标含义混淆 | 该指标只看上下文冗余度 | 答案正确性看 faithfulness 与 `answer_correctness` |
| 生成脚本中途失败 | 全量重跑，浪费大量调用 | 没有断点 | **分阶段保存**（每 1500 条落盘一次） |
| 生成接口偶发超时拖死流程 | 卡住不动 | 未设超时 | `timeout=10` 并对失败返回 `None` 继续流程 |
| 把评估数据集和训练数据集混用 | 指标虚高（数据泄露） | 评估样本出现在训练里 | 训练/评估严格分离，最好来自不同文档与不同生成批次 |

## 5. 面试问答

**Q1：RAGAS 的四个核心指标分别衡量什么？分数低时应优先改哪一侧？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

四个指标按「检索 / 生成」两侧划分：

| 指标 | 一侧 | 衡量什么 |
|---|---|---|
| `context_relevancy` | 检索 | 检索到的上下文是否**只包含**回答所需信息（惩罚冗余） |
| `context_recall` | 检索 | 真实答案中的论断有多少能**归因于**检索到的上下文，$\frac{\text{可归因论断数}}{\text{真实答案论断总数}}$ |
| `faithfulness` | 生成 | 答案是否确实由给定上下文推出，$F=\frac{\lvert V\rvert}{\lvert S\rvert}$，低分意味着幻觉风险高 |
| `answer_relevancy` | 生成 | 答案与问题的切题程度（用反向生成问题 + 余弦相似度平均计算） |

定位方法：
- **faithfulness 高但 context_recall 低** → 模型老实、这里没找全 → 改检索（切片粒度、混合检索、Query 改写、增大 `retrieval_k`）；
- **faithfulness 低但 context_recall 高** → 够了但模型没照用 → 改生成（Prompt 约束、降 temperature、换模型）；
- **context_relevancy 低** → 检索结果冗余 → 加重排序、减小 `candidate_m`、加标量过滤。

这就是评估体系最大的价值：把「效果不好」翻译成「该改哪一侧」。

</details>

**Q2：如何自动构造一份高质量的 RAG 评估数据集？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

用三个代理协作：

1. **测试样本代理（Test Sample Agent）**：基于文档片段生成 factoid 问答对。
 Prompt 关键约束是「问题必须能用上下文中具体、简洁的事实信息回答」，
 且 **`MUST NOT mention "according to the passage" or "context"`**——否则问题泄露上下文依赖，评估会虚高。
 建议生成 **≥200 条**（过滤后约保留一半）。
2. **样本质量评价代理（Critique Agent）**：对每个问题按三个维度打 1~5 分——
 领域相关性（对目标用户是否有用）、由上下文可回答性（是否清晰无歧义）、独立性（是否单独可理解，不依赖隐含设定）。
 **任一维度评分过低就直接剔除**。
 两条经验：① 让代理**先输出理由再给分**，既便于人工核验、又能提高评分准确性；
 ② 输出格式固定为 `Evaluation:` + `Totalrating:`，便于程序解析。
3. **评估代理（Evaluation Agent）**：选评估模型（GPT-4 或 Prometheus-13B、JudgeLM-33B），
 设计带 1~5 分 rubric 的评估 prompt，要求以 `Feedback: ... [RESULT] n` 格式输出。
 建议重点关注 **faithfulness** 作为主要指标，因为它能全面反映端到端性能。

整体收益：把「试错式定性评估」变成「有量化依据的数据驱动迭代」，避免在无效改动上浪费时间。

</details>

**Q3：`context_recall` 和 `faithfulness` 都在做「声明级」核对，它们有什么本质区别？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

两者的比较对象不同：

- **`context_recall` 比较「真实答案 vs 检索上下文」**：把 ground truth 拆成若干 claim，
 逐个判断能否在检索到的上下文里找到支持，算的是**检索的覆盖度**。
 它回答「找全了没有」。算例中，上下文提到「西班牙击败荷兰」但没提「1-0 比分」，
 该 claim 记为未召回，$\text{ContextRecall}=0.5$。
- **`faithfulness` 比较「模型答案 vs 检索上下文」**：把**模型生成的答案**拆成陈述，
 判断每条能否从上下文推断出来，算的是**生成的可靠度**。它回答「模型有没有编」。

所以两者对「不通过」的含义完全不同：`context_recall` 低说明检索漏料（**修检索**）；
`faithfulness` 低说明模型脱离材料（**修生成**）。如果只用一个指标，就无法区分这两种故障模式——
这正是评估体系需要同时覆盖检索侧与生成侧的原因。

</details>

## 6. 自测题

**1. RAGAS 评估数据集需要哪四个字段？哪个是唯一需要人工标注的？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

- `question`：作为 RAG 管道输入的用户查询（输入）；
- `answer`：RAG 管道生成的答案（输出）；
- `contexts`：从外部知识源检索到的、用于回答该问题的上下文（**必须是列表**）；
- `ground_truths`：question 的基本事实答案——**这是唯一人工注释的信息**。

RAGAS 的设计取向正是「不必依赖人工标注的标准答案，而是通过底层 LLM 来评估」，
因此除了 `ground_truths`（且主要用于 `context_recall`），其余都可自动获得。

</details>

**2. `answer_relevancy` 为什么用「反向生成问题」来实现？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

因为直接让 LLM 判断「这个答案切题吗」是主观打分，容易受评估模型偏好影响、且难以复现。
反向生成的做法是：让 LLM 根据答案生成 n 个「这个答案可能在回答的问题」$q_i$，
再用 embedding 模型把这些 $q_i$ 与原始问题 $q$ 都编码成向量，
计算每一对的**余弦相似度**，最后取平均作为答案相关性得分。

好处：① 把主观判断转化为**可量化的向量相似度**；② 能捕捉「答案是正确知识但答非所问」的情况——
如果答案与问题无关，由它反推出来的问题就会与原问题距离很远。

</details>

**3. 设计评估 Prompt 时，为什么要给 1-5 分的 rubric 并要求先输出理由？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

给 rubric 的原因：**保持评估代理的一致性，避免因模糊标准导致评分结果波动**。
没有明确标准时，同一份数据多次评估的分数可能差异很大，指标就失去了横向比较的意义。

要求先输出理由的原因有两点：① **便于人工核验评分是否合理**（分数背后有依据可查）；
② **促使代理在回答过程中进行更深入的思考，从而提高评分的准确性**——这与「给模型充足思考时间」是同一个原理。

此外输出格式要固定（如 `Feedback: ... [RESULT] n`），让程序能稳定抽取分数，避免解析失败。

</details>

**4. 为什么要对自动生成的测试样本做质量过滤？三维评分分别是什么？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

因为自动生成的样本可能存在质量问题（问题有歧义、无法从上下文回答、脱离上下文看不懂等），
低质量样本会污染评估结论。因此引入样本质量评价代理，对每个问题按三个维度打 1~5 分：

① **领域相关性**：这个问题对目标用户有多大用处（1=没用，5=极其有用）；
② **由上下文可回答性**：给定上下文，问题能被清晰无歧义地回答的程度（1=无法回答，5=清晰可答）；
③ **独立性**：问题在多大程度上依赖额外信息才能被理解（1=必须依赖上下文设定，5=单独就能看懂）。

**任一维度评分过低就直接剔除该问题**。经验值是过滤后大约能保留一半样本，
所以想得到 100 条有效样本，建议先生成 200 条。

</details>

**5. 评估指标四项都很高，但业务方仍不满意，可能是什么问题？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

说明**指标体系没有覆盖业务的真实诉求**。常见情况：

① **时效性**：答案依据的文档过时（如政策、价格），指标只衡量「忠于上下文」而不衡量「上下文是否最新」——
需引入时间过滤或数据新鲜度检查；
② **合规与安全**：答案虽忠实但包含不该输出的内容（承诺收益、诊疗建议）——
需要独立的安全护栏与合规评审；
③ **语气与格式**：答案正确但不符合品牌话术或输出格式要求——
需要补充格式与风格的规则校验；
④ **完整性与有用性**：`faithfulness` 高只说明「没编」，不代表「答得全」——
可补充完整性（Completeness）与利用率（Utilization）指标；
⑤ **评估集分布偏斜**：测试问题集中在简单查询上，真实流量里的长尾难题没被覆盖——
需要按业务流量分布重新采样评估集。

结论：RAGAS 四个指标是**必要但不充分**的，业务上线前仍需在真实流量上做人工抽检与 A/B。

</details>

## 7. 延伸阅读

- [Judging LLM-as-a-Judge / MT-Bench (arXiv:2306.05685)](https://arxiv.org/abs/2306.05685)
- [Self-RAG (arXiv:2310.11511)](https://arxiv.org/abs/2310.11511)
- [RAG 综述 (arXiv:2312.10997)](https://arxiv.org/abs/2312.10997)
- [RAGAS 官方文档](https://docs.ragas.io/)
- [RAGAS GitHub](https://github.com/explodinggradients/ragas)
- [Hugging Face Datasets](https://huggingface.co/docs/datasets/index)

---

[⬅️ 返回本目录索引](README.md)
