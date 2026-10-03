> **一句话总结**：规划是 Agent 把「一个模糊目标」翻译成「一串可执行子目标」的能力——给出的四个动作是**任务分析、目标设定、搜索、路径规划**，而在它以四种形态出现：Function Call 的链式工具调用、RAG 的查询改写策略、CrewAI 的 Task 拆解、以及人工编排的工作流。
> **前置知识**：[01-Agent基础范式与ReAct循环](../01-基础范式/01-Agent基础范式与ReAct循环.md) 的五要素、[03-LangChain与工具编排](../03-记忆与多智能体/03-LangChain与工具编排.md) 的 Task/Crew、[06-RAG作为Agent的知识获取手段](../03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md) 的检索流程。
> **学完能做到**：
> 1. 说出规划的四个动作用各自的输入输出，并区分「隐式规划（ReAct 内嵌）」与「显式规划（先出计划再执行）」。
> 2. 用「子查询分解 / HyDE / 回溯提问」三种策略改写用户的模糊查询，并说明各自适用场景。
> 3. 实现一个「分解 → 并行执行 → 去重合并 → 裁剪」的任务分解器，并识别规划失效的典型模式。

---

## 1. 核心概念

### 1.1 为什么 Agent 需要规划

LLM 单次调用只能解决「一步能说清」的问题。一旦任务需要多步、且步骤之间有条件依赖，就必须先有规划：

| 任务特征 | 单次调用的问题 | 规划的作用 |
| --- | --- | --- |
| 多步 | 模型倾向于只做第一步就直接给答案 | 把步骤显式列出来，逐步执行 |
| 有条件依赖 | 第 2 步的参数来自第 1 步的结果 | 建立依赖顺序（先查航班号，再查票价） |
| 多实体 / 多方面 | 一次检索覆盖不全，容易只回答其中一面 | 拆成多个子问题分别处理再合并 |
| 表述抽象 | 字面语义与知识库表述不匹配 | 改写查询（生成假设答案 / 简化问题） |

对 Planning 的定义：

> 利用 LLM 大模型对要完成的任务或解决的问题进行**深入分析，生成可能的解决方案**。它涉及对任务的分解、目标的设定、搜索、路径的规划等。

### 1.2 规划的四个动作

| 动作 | 回答的问题 | 典型实现 | 对应描述 |
| --- | --- | --- | --- |
| 任务分析 | 这个请求到底要什么？ | 意图识别、查询分类 | 「对要完成的任务或解决的问题进行深入分析」 |
| 目标设定 | 成功的标准是什么？ | 定义终态、输出契约 | 「目标的设定」 |
| 搜索 | 有哪些可行路径？ | 候选方案生成、试错 | 「搜索」 |
| 路径规划 | 先做哪一步？ | 排序、依赖编排、并行化 | 「路径的规划」 |

注意「目标设定」在工程上常被忽略，但它其实是最省事的一步：在 Task / prompt 里写清「你最后的答案必须是……」就能显著减少 Agent 的跑偏。 CrewAI 的三个 Task description 全部以输出契约结尾，正是这个道理。

### 1.3 三层粒度：目标 → 子目标 → 动作

| 层级 | 粒度 | 载体 | 例子（退货场景） |
| --- | --- | --- | --- |
| 目标（Goal） | 整个任务 | 用户输入 + system prompt | 处理客户的退货请求 |
| 子目标（Sub-goal） | 可独立验证的阶段 | Task / Plan 步骤列表 | 验证订单 → 判断条件 → 生成标签 → 通知仓库 |
| 动作（Action） | 一次工具调用 | tool call | `query_order(order_id="12345")` |

粒度控制的原则：**子目标要小到「能用一个工具或一段推理验证完成」**，但不要小到「一步一个 token」。 CrewAI 对 Task 的表述是「每个任务都具有明确的目标和要求，并且被分解成**小而专注的子任务**」。

### 1.4 规划在的四种形态

本节没有单独讲「Planning 算法」，但规划在四个地方反复出现：

| 形态 | 出现位置 | 规划的粒度 | 谁做规划 |
| --- | --- | --- | --- |
| 链式工具调用 | Function Call 多函数示例（航班） | 动作级 | 模型（隐式，每轮决定下一步） |
| 查询改写与检索策略 | RAG 系统 `strategy_selector.py` | 检索级 | 模型（先选策略，再执行） |
| 多角色任务拆解 | CrewAI 写情书项目 | 子目标级 | 人（写 Task）+ 模型（执行） |
| 工作流编排 | 「Flow 工作流」形式 | 流程级 | 完全由人 |

这张表可以用来判断一个系统到底「智能在哪一层」：如果规划全在第四行，那它是工作流不是 Agent。

### 1.5 检索级规划：四种查询策略

RAG 系统用 `StrategySelector` 让 LLM 在四种策略里选一个，这是最完整的「规划器」实现：

| 策略 | 做法 | 适用场景 | 示例 |
| --- | --- | --- | --- |
| 直接检索 | 对用户查询直接检索，不做任何增强 | 查询意图明确，需要从知识库检索**特定信息** | 「人工智能方向学费是多少？」「JAVA 的大纲是什么？」 |
| 假设问题检索（HyDE） | 让 LLM 先生成一个假设答案，再基于假设答案检索 | 查询较为**抽象**，直接检索效果不佳 | 「人工智能在教育领域的应用有哪些？」 |
| 子查询检索 | 把复杂查询拆成多个简单子查询，分别检索并合并结果 | 查询涉及**多个实体或方面**，需要分别检索 | 「比较 Milvus 和 Zilliz Cloud 的优缺点。」 |
| 回溯问题检索 | 把复杂查询转化为**更基础、更易于检索**的问题 | 查询较为复杂，需要简化后才能有效检索 | 「我有一个包含 100 亿条记录的数据集，想存到 Milvus 中查询，可以吗？」 |

策略选择器的提示词有两点值得学习：

1. **给出每种策略的描述 + 适用场景 + 正例**，而不是只列名称——这是让模型稳定分类的关键；
2. **要求模型只返回策略名称，不要解释过程**，并配合 `temperature=0.1`，把自由生成压成一次受限分类。

```text
你是一个智能助手，负责分析用户查询 {query}，并从以下四种检索增强策略中选择一个最适合的策略，
直接返回策略名称，不需要解释过程。
...
根据用户查询 {query}，直接返回最适合的策略名称，例如 "直接检索"。不要输出任何分析过程或其他内容。
```

工程上还有一层兜底：`call_dashscope` 在异常时 `return "直接检索"`——**规划器失败时必须有一个安全默认值**。

---

## 2. 关键机制

### 2.1 隐式规划 vs 显式规划

> **说明**：未出现 Plan-and-Execute / Tree-of-Thought 等术语，本小节为通用知识补充，用于和内容对照。

| 维度 | 隐式规划（ReAct 风格） | 显式规划（Plan-and-Execute 风格） |
| --- | --- | --- |
| 计划产出 | 不产出完整计划，每步现想 | 先输出完整步骤列表，再逐步执行 |
| 的实例 | Function Call 的链式调用（航班示例） | CrewAI 的 `tasks=[task1, task2, task3]` |
| 优点 | 灵活，可随时根据 Observation 改道 | 计划可见、可人工审核、可并行 |
| 缺点 | 轨迹难以预测，容易原地打转 | 计划一旦错误，后续步骤集体偏航 |
| 适合 | 环境反馈快、步骤不确定的任务 | 步骤可预先枚举、需要审计的任务 |

实践中的折中方案：**先让模型产出 3–7 步的计划，再逐步执行；每执行完一步允许模型修订后续计划**。这样既有可审计性，又保留改道能力。

### 2.2 子查询分解的执行细节（来自 `rag_system.py`）

给出的子查询检索实现包含四个动作：

| 步骤 | 代码位置 | 关键细节 |
| --- | --- | --- |
| 1. 生成子查询 | `subquery_prompt` + LLM | 提示词要求「每行一个子查询」，随后按 `\n` 切分并过滤空行 |
| 2. 逐个检索 | `for sub_q in subqueries` | 每个子查询都做一次 `hybrid_search_with_rerank`（含混合检索 + 重排），**开销与子查询数量成正比** |
| 3. 去重合并 | `{doc.page_content: doc for doc in all_docs}` | 用一个 dict 按内容去重；按对象地址去重不可靠，因为内容相同但对象不同无法去重 |
| 4. 数量裁剪 | `final_context_docs = ranked_sub_chunks[:conf.CANDIDATE_M]` | 统一在 `retrieve_and_merge` 末尾限制送入 prompt 的候选数量 |

第 3 步的去重策略值得记住：**用内容做 key**（或更严谨地用文档 ID），而不是用对象哈希。

### 2.3 HyDE：用「假答案」检索

流程极其简单，但效果显著：

```text
用户问题（抽象）──▶ LLM 生成假设答案（具体、术语密集）──▶ 用假设答案去检索 ──▶ 重排 ──▶ 上下文
```

原理：向量检索比较的是「查询向量与文档向量的相似度」。抽象问题（「人工智能在教育领域的应用有哪些？」）与知识库里的具体段落（「RAG 系统在问答中的落地」）在向量空间里可能相距很远；而一段**假设答案**的用词与文档更接近，因此检索命中率更高。

代码中有一行注释点出了关键取舍：

> 注意：HyDE 通常只用于生成检索向量，不一定需要 rerank 这一步，但这里复用了

也就是说，HyDE 的价值在**召回**阶段，而 rerank 是**精排**阶段；把二者叠在一起能提高质量，但也会增加延迟。

### 2.4 回溯式提问：把「难检索的问题」变成「好检索的问题」

| 原问题 | 回溯问题 | 为什么有效 |
| --- | --- | --- |
| 我有一个包含 100 亿条记录的数据集，想把它存储到 Milvus 中进行查询。可以吗？ | Milvus 支持的数据规模上限是多少？ | 原问题含大量上下文噪声（100 亿、存储、查询），简化后与知识库中的「容量上限」段落对齐 |

它和子查询分解的区别：**子查询是「一拆多」，回溯是「多合一」**（抽象成一个更基础的问题）。选择器提示词里把二者并列，正说明同一个问题可以用不同的规划方式处理。

### 2.5 依赖图：什么时候可以并行

航班示例揭示了任务间的依赖类型：

| 依赖类型 | 表现 | 能否并行 |
| --- | --- | --- |
| 串行依赖 | `get_ticket_price` 需要 `get_plane_number` 返回的航班号 | 不能 |
| 独立并列 | 「比较 Milvus 和 Zilliz Cloud 的优缺点」中的两个子查询 | 能 |

工程建议：在生成子查询后，先判断其是否存在数据依赖（后一个查询是否引用前一个的结果），无依赖的可以并发检索；当前实现是纯串行 `for` 循环，属于可优化点（代价是复杂度与限流控制）。

### 2.6 反思与完善（Reflection）

在 Agent 能力图中列出了「反思与完善」与「代码解释器」。反思的本质是**把执行结果回灌给模型，要求它检查并修订**：

| 形式 | 做法 | 的对应 |
| --- | --- | --- |
| 解析失败重试 | 把「格式错误」作为 Observation 回灌 | LangChain `handle_parsing_errors=True`（见 [03](../03-记忆与多智能体/03-LangChain与工具编排.md) 常见坑） |
| 结果校验 | 工具返回 error 字段，模型据此重规划 | Function Call 的 `{"error": ...}` 返回模式 |
| 自我批评 | 让第二个 Agent 审阅第一个的输出 | CrewAI 「内容编辑」Agent 检查语法与格式 |

CrewAI 项目里「作家写 → 编辑改 → 信使发」的流水线，本质上就是一个**角色化的反思链**：每个下游角色都是对上游输出的校验器。

### 2.7 规划失效的典型模式

| 失效模式 | 现象 | 根因 | 缓解 |
| --- | --- | --- | --- |
| 计划过粗 | 一步跨越多个工具，模型无法完成 | 分解粒度不足 | 强制「每个子目标可被单个工具验证」 |
| 计划过细 | token 爆炸、成本高、延迟长 | 把一步能做的事拆成五步 | 限制计划步数（如 3–7 步） |
| 计划漂移 | 执行到中途忘了原目标 | 上下文过长，早期目标被稀释 | 每轮把原目标复述在 prompt 中 |
| 依赖错序 | 用还没拿到的参数调用工具 | 未做依赖分析 | 显式建立参数来源表；模型自检「参数是否已知」 |
| 规划器失效 | 策略选择输出乱码或无关文本 | 模型不稳定 / 提示词允许多余输出 | 兜底默认值（如 `return "直接检索"`）+ 白名单校验 |

---

## 3. 可运行示例

### 3.1 任务分解器：分解 → 检索 → 去重 → 裁剪

下面的例子把 RAG 子查询检索的骨架抽出来，用假 LLM 与假检索器实现，**仅依赖标准库，可直接运行**。

```python
"""任务分解与合并去重的骨架实现（对应 RAG 子查询检索策略）。

依赖：仅标准库。
"""

import json

# ---------- 假知识库 ----------
KNOWLEDGE_BASE = [
{"id": "d1", "text": "Milvus 是面向向量检索的数据库，支持亿级向量的近似最近邻搜索。"},
{"id": "d2", "text": "Milvus 采用分布式架构，可通过增加 query node 水平扩展检索吞吐。"},
{"id": "d3", "text": "Zilliz Cloud 是全托管的 Milvus 服务，免去集群运维，按量计费。"},
{"id": "d4", "text": "Zilliz Cloud 提供自动扩缩容与备份恢复，适合中小团队快速上线。"},
{"id": "d5", "text": "选择向量数据库时需要权衡成本、运维复杂度与数据规模。"},
]

def fake_retriever(query, k=2):
    """极简关键词检索：按查询词与文档的重合度排序，返回 top-k。"""
    tokens = set(query.replace("？", "").replace("，", "").replace(" ", ""))
    scored = []
    for doc in KNOWLEDGE_BASE:
        overlap = len(tokens & set(doc["text"]))
        if overlap:
            scored.append((overlap, doc))
            scored.sort(key=lambda pair: pair[0], reverse=True)
            return [doc for _, doc in scored[:k]]

        # ---------- 假 LLM：把复杂查询拆成子查询 ----------
        def fake_llm_decompose(query):
            if "比较" in query and "优缺点" in query:
                return "Milvus 的优缺点是什么\nZilliz Cloud 的优缺点是什么"
            return query

        def retrieve_with_subqueries(query, k=2, candidate_m=4):
            """子查询检索：分解 → 逐个检索 → 按内容去重 → 裁剪数量。"""
            subqueries_text = fake_llm_decompose(query)
            subqueries = [q.strip() for q in subqueries_text.split("\n") if q.strip()]
            print("生成的子查询:", subqueries)

            all_docs = []
            for sub_q in subqueries:
                docs = fake_retriever(sub_q, k=k)
                print("子查询 %r 检索到 %d 个文档" % (sub_q, len(docs)))
                all_docs.extend(docs)

                # 按内容去重（比按对象地址去重更可靠）
                unique_docs = list({doc["text"]: doc for doc in all_docs}.values())
                print("共检索到 %d 个文档, 去重后剩 %d 个" % (len(all_docs), len(unique_docs)))

                final_docs = unique_docs[:candidate_m]
                print("最终选取 %d 个文档作为上下文" % len(final_docs))
                return final_docs

            if __name__ == "__main__":
                result = retrieve_with_subqueries("比较 Milvus 和 Zilliz Cloud 的优缺点")
                print(json.dumps(result, ensure_ascii=False, indent=2))
```

预期输出（要点）：

```text
生成的子查询: ['Milvus 的优缺点是什么', 'Zilliz Cloud 的优缺点是什么']
子查询 'Milvus 的优缺点是什么' 检索到 2 个文档
子查询 'Zilliz Cloud 的优缺点是什么' 检索到 2 个文档
共检索到 4 个文档, 去重后剩 4 个
最终选取 4 个文档作为上下文
```

### 3.2 Plan-and-Execute 骨架：先出计划，再逐步执行

**依赖**：仅标准库（用脚本化 planner 替代 LLM）。

```python
"""显式规划（Plan-and-Execute）骨架：先产出计划，再逐步执行并允许修订。

依赖：仅标准库。
"""

import json

TOOL_REGISTRY = {
"get_plane_number": lambda **kw: {"date": kw["date"], "number": "1123"},
"get_ticket_price": lambda **kw: {"ticket_price": "668"},
"notify_user": lambda **kw: {"sent": True, "to": kw.get("contact", "unknown")},
}

def scripted_planner(goal, known_facts):
    """假规划器：根据已知事实逐步给出下一步动作，模拟 Plan-and-Execute。"""
    if "number" not in known_facts:
        return {"step": 1, "tool": "get_plane_number",
    "args": {"date": "2024-04-02", "start": "郑州", "end": "北京"}}
    if "ticket_price" not in known_facts:
        return {"step": 2, "tool": "get_ticket_price",
    "args": {"date": "2024-04-02", "number": known_facts["number"]}}
    return None # 计划完成

def execute_plan(goal, max_steps=5):
    known_facts = {}
    trace = []
    for _ in range(max_steps):
        action = scripted_planner(goal, known_facts)
        if action is None:
            break
        tool_name = action["tool"]
        result = TOOL_REGISTRY[tool_name](**action["args"])
        print("step %d -> %s(%s) => %s" % (
        action["step"], tool_name,
        json.dumps(action["args"], ensure_ascii=False),
        json.dumps(result, ensure_ascii=False),
        ))
        known_facts.update(result)
        trace.append({"tool": tool_name, "args": action["args"], "result": result})
        return known_facts, trace

    if __name__ == "__main__":
        facts, trace = execute_plan("查询 2024-04-02 郑州到北京的票价")
        print("最终已知事实:", json.dumps(facts, ensure_ascii=False))
```

这个骨架演示了两个关键设计：`known_facts` 充当**执行期状态**（步骤间传参的载体），`scripted_planner` 每次只返回**一步**并在信息充足时返回 `None` 终止——对应 2.1 节「先出计划、允许修订」的折中方案。真实场景中把 `scripted_planner` 换成一次 LLM 调用即可。

### 3.3 策略选择器（对应 `strategy_selector.py`）

**依赖**：`pip install openai langchain python-dotenv`；环境变量 `DASHSCOPE_API_KEY`。

```python
"""检索策略选择器：让 LLM 在四种增强策略中选择一个（只返回策略名）。

依赖：pip install openai langchain python-dotenv
环境变量：DASHSCOPE_API_KEY
"""

import os

from langchain.prompts import PromptTemplate
from openai import OpenAI

STRATEGIES = ["直接检索", "假设问题检索", "子查询检索", "回溯问题检索"]

STRATEGY_PROMPT = PromptTemplate(
template="""
你是一个智能助手，负责分析用户查询 {query}，并从以下四种检索增强策略中选择一个最适合的策略，
直接返回策略名称，不需要解释过程。

1. **直接检索**：对用户查询直接进行检索，不进行任何增强处理。
适用场景：查询意图明确，需要从知识库中检索特定信息的问题。
2. **假设问题检索（HyDE）**：使用 LLM 生成一个假设的答案，然后基于假设答案进行检索。
适用场景：查询较为抽象，直接检索效果不佳的问题。
3. **子查询检索**：将复杂的用户查询拆分为多个简单的子查询，分别检索并合并结果。
适用场景：查询涉及多个实体或方面，需要分别检索不同信息的问题。
4. **回溯问题检索**：将复杂的用户查询转化为更基础、更易于检索的问题，然后进行检索。
适用场景：查询较为复杂，需要简化后才能有效检索的问题。

根据用户查询 {query}，直接返回最适合的策略名称，例如 "直接检索"。不要输出任何分析过程或其他内容。
""",
input_variables=["query"],
)

def select_strategy(query, model="qwen-plus"):
    client = OpenAI(
    api_key=os.environ["DASHSCOPE_API_KEY"],
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    try:
        completion = client.chat.completions.create(
        model=model,
        messages=[
        {"role": "system", "content": "你是一个有用的助手。"},
        {"role": "user", "content": STRATEGY_PROMPT.format(query=query)},
        ],
        temperature=0.1, # 压低随机性，把生成压成一次受限分类
        )
        raw = completion.choices[0].message.content if completion.choices else ""
    except Exception as exc: # 规划器失败必须有安全默认值
        print("策略选择失败，回退到直接检索: %s" % exc)
        return "直接检索"

    strategy = raw.strip()
    if strategy not in STRATEGIES: # 白名单校验，防止模型自由发挥
        print("模型返回了非法策略 %r，回退到直接检索" % strategy)
        return "直接检索"
    return strategy

if __name__ == "__main__":
    for q in [
    "人工智能方向学费是多少？",
    "人工智能在教育领域的应用有哪些？",
    "比较 Milvus 和 Zilliz Cloud 的优缺点。",
    ]:
        print("%s -> %s" % (q, select_strategy(q)))
```

---

## 4. 常见坑

| 现象 | 原因 | 解决 |
| --- | --- | --- |
| 复杂问题只回答了其中一面 | 没有分解，单次检索覆盖率不足 | 用子查询分解，逐个子问题检索后合并 |
| 抽象问题检索不到内容 | 查询用词与知识库表述不匹配 | 改用 HyDE：先生成假设答案再检索 |
| 模型把「策略名」答成一大段解释 | 提示词没限制输出格式 | 明确要求「只返回策略名称，不要输出任何分析过程」，并配 `temperature=0.1` |
| 规划器返回了列表以外的策略 | 没有做输出校验 | 白名单校验 + 失败回退到默认策略（安全默认值） |
| 子查询数量一多，耗时线性上涨 | 每个子查询都做完整混合检索 + 重排 | 限制子查询个数；对无依赖的子查询并发检索；对子查询先做粗召回再统一重排 |
| 合并结果里出现重复段落 | 用对象地址去重，内容相同但对象不同 | 改用文档内容或文档 ID 作 key 去重 |
| 上下文塞进过多文档，答案反而变差 | 没有裁剪候选数量 | 在合并的最后一步统一裁剪（如取前 `CANDIDATE_M` 条） |
| 计划一旦错误，后面步骤全错 | 显式计划缺少中途修订机制 | 每执行一步允许重规划；对关键步骤加人工确认 |

---

## 5. 面试问答

<details><summary>参考答案</summary>

**Q1：Agent 的规划包含哪几个动作？为什么「目标设定」常被低估？**

给出的四个动作是：任务分析（深入分析要完成的任务或问题）、目标设定（确定要达成什么）、搜索（生成可能的解法/路径）、路径规划（确定先后顺序）。「目标设定」常被低估，是因为大家默认「用户说了要什么就是目标」。但在多 Agent 与多步场景里，目标必须被转写成**可验证的终态契约**才有用，例如 CrewAI 的 Task description 以「你最后的答案必须是信息是否已被存储在本地磁盘中」结尾。没有这层契约，Agent 可能在「看起来做完了」时提前结束，或迟迟不肯结束。

</details>

<details><summary>参考答案</summary>

**Q2：HyDE 和「子查询检索」分别解决什么类型的检索困难？能否同时使用？**

HyDE 解决的是**查询表述与文档表述不匹配**的问题：抽象问题的用词与知识库具体段落距离远，直接检索召回率低；先让模型生成一段假设答案（用词更接近文档），再拿它去检索，能显著提升召回。子查询检索解决的是**单一查询覆盖不全**的问题：当查询涉及多个实体或方面（如「比较 A 和 B」），一次检索只能命中其中一侧，拆成多个子查询分别检索再合并才能覆盖。二者可以叠加：先用子查询分解，再对每个抽象化的子查询套 HyDE。代价是 LLM 调用次数和检索次数成倍增加。

</details>

<details><summary>参考答案</summary>

**Q3：为什么说「先产出完整计划再执行」不一定更好？**

因为计划的正确性依赖对环境的准确预期。在环境反馈快、情况易变的场景里，一份详细的初始计划很可能在第 2 步就被现实推翻，后续步骤集体偏航，反而比逐步试探（ReAct）更差。显式计划的真正优势在于可审计、可人工审核、可并行——适合步骤可预先枚举、合规要求高的任务。因此实践中常见的是折中方案：先让模型产出 3–7 步的计划，执行过程中允许根据 Observation 修订，同时对关键节点保留人工确认。

</details>

---

## 6. 自测题

<details><summary>参考答案</summary>

**1. 这里把 Planning 定义为什么？涉及哪几个环节？**

定义：利用 LLM 大模型对要完成的任务或解决的问题进行深入分析，生成可能的解决方案。涉及的环节：对任务的分解、目标的设定、搜索、路径的规划。

</details>

<details><summary>参考答案</summary>

**2. RAG 系统里四种检索策略各自适用于什么查询？各举一例。**

直接检索——意图明确、要检索特定信息（「人工智能方向学费是多少？」）；假设问题检索（HyDE）——查询抽象、直接检索效果不佳（「人工智能在教育领域的应用有哪些？」）；子查询检索——涉及多个实体或方面（「比较 Milvus 和 Zilliz Cloud 的优缺点」）；回溯问题检索——查询复杂需简化（「我有 100 亿条记录想存到 Milvus 查询，可以吗？」→「Milvus 支持的数据规模上限是多少？」）。

</details>

<details><summary>参考答案</summary>

**3. 子查询检索的结果合并阶段，为什么要先把所有子查询的结果收集完再统一裁剪？**

因为去重需要全局视野：不同子查询可能命中同一份文档（重叠命中恰恰说明该文档对整体问题更重要）。如果每个子查询各自裁剪再合并，重叠文档会重复占用上下文名额，且真正重要的重叠文档可能被提前丢弃。先全量收集 → 按内容去重 → 在最后一步统一裁剪到 `CANDIDATE_M`，才能既保证覆盖度又控制 prompt 长度。

</details>

<details><summary>参考答案</summary>

**4. 航班示例中体现了哪种任务依赖？如果用户问「郑州和天津哪个航班便宜」，依赖关系会怎样变化？**

体现的是**串行依赖**：`get_ticket_price` 的 `number` 参数来自 `get_plane_number` 的返回值，必须先执行前者。若改成比较两个目的地，则出现两条**独立并列**的子链（郑州→北京 与 天津→北京），两条链内部仍是串行，但链与链之间可以并行执行，最后一步才是比较合并。

</details>

<details><summary>参考答案</summary>

**5. 规划器（如策略选择器）为什么必须准备兜底默认值？**

因为规划器本身是一次 LLM 调用，可能因网络、额度、限流或模型抖动而失败，也可能返回不在候选集合内的非法值。规划处于流程的最上游，一旦它抛异常或返回乱码，整个下游（检索、生成）都无法进行。因此在 `call_dashscope` 的异常分支返回「直接检索」这种最稳妥的默认策略，并在拿到结果后做白名单校验、非法则回退，是保证系统可用性的必要设计。

</details>

---

## 7. 延伸阅读

- Chain-of-Thought Prompting Elicits Reasoning in Large Language Models —— https://arxiv.org/abs/2201.11903
- Least-to-Most Prompting Enables Complex Reasoning in Large Language Models —— https://arxiv.org/abs/2205.10625
- Plan-and-Solve Prompting —— https://arxiv.org/abs/2305.04091
- Tree of Thoughts: Deliberate Problem Solving with Large Language Models —— https://arxiv.org/abs/2305.10601
- Reflexion: Language Agents with Verbal Reinforcement Learning —— https://arxiv.org/abs/2303.11366
- Precise Zero-Shot Dense Retrieval without Relevance Labels（HyDE） —— https://arxiv.org/abs/2212.10496
- ：《第十章：AI Agents 开发应用》《第四章：基于 Milvus 数据库构建 RAG 问答系统_06-检索策略与 RAG 系统设计》

---

[⬅️ 返回本目录索引](README.md)
