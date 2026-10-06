---
article_id: "6f07590fb31d"
learning_kind: "reference"
learning_category: "06-llm"
---

# -RAG系统构建


> **一句话总结**：RAG（检索增强生成）用「先检索、再生成」把企业私有知识与实时信息接进大模型，工程上是一条完整流水线——**文档解析分层切块 → 向量化入库 → Query 改写与意图分类 → 多策略混合检索与重排序 → 受约束的 Prompt 生成**；用物流问答与 RAG 两个项目把这条链路完整落地。
> **前置知识**：LangChain 六大组件（见《08-LangChain基础》）、Milvus 与向量检索（见《07-向量数据库与Milvus》）、embedding 与相似度。
> **学完能做到**：1. 独立搭出一个「加载 → 分层切块 → 入库 → 混合检索 → 生成」的最小 RAG 系统；2. 说清 HyDE、子查询、回溯、Query 改写分别解决什么问题；3. 为 RAG 系统设计模块划分与关键配置项。

## 1. 核心概念

### 1.1 为什么需要 RAG

大模型的根本局限：**模型基于过去的经验数据训练完成，无法获取最新知识，也无法获取各企业私有的知识**。
业界应对企业私有知识的两条路线：

| 路线 | 做法 | 特点 |
|---|---|---|
| 微调 | 利用企业私有知识，基于开源大模型进行微调 | 知识固化进权重；更新成本高、易遗忘、无法溯源 |
| **RAG** | 基于 LangChain 集成向量数据库与 LLM，搭建本地知识库问答 | 知识外置；更新只需重建索引；**可返回引用来源**、可审计 |

**RAG 的本质**：参数化知识（模型权重）与非参数化知识（外部知识库）的结合。检索器负责「找依据」，生成器负责「组织语言」。

### 1.2 RAG 的四步主流程

| 步骤 | 做什么 | 关键组件 |
|---|---|---|
| ① 查询分类 | 判断查询类型（通用知识 / 专业咨询） | `QueryClassifier` |
| ② 策略选择 | 选择检索策略（直接 / HyDE / 子查询 / 回溯） | `StrategySelector` |
| ③ 文档检索 | 从向量库检索相关文档，稠密 + 稀疏混合并重排序 | `VectorStore` |
| ④ 生成回答 | 以检索文档为上下文，结合用户问题调用 LLM | `RAGPrompts` + LLM |

**分类的价值**：通用知识（如「5×9 等于多少」）直接由 LLM 回答，**省掉一次检索**；
专业咨询（如「人工智能方向学费是多少」）才进入检索流程，保证答案有依据。这是「按需检索」的工程优化。

### 1.4 关键配置项一览（来自 `config.ini`）

| 分类 | 配置项 | 默认值 | 作用 |
|---|---|---|---|
| 检索 | `parent_chunk_size` | 1200 | 父块大小 |
| 检索 | `child_chunk_size` | 300 | 子块大小 |
| 检索 | `chunk_overlap` | 50 | 相邻块重叠 |
| 检索 | `retrieval_k` | 5 | 检索返回条数 |
| 检索 | `candidate_m` | 2 | 最终作为上下文的条数 |
| Milvus | `host` / `port` | localhost / 19530 | 向量库地址 |
| Milvus | `database_name` / `collection_name` | / rag_final | 库与集合 |
| LLM | `model` | qwen-plus | 生成模型 |
| LLM | `dashscope_api_key` / `base_url` | — | OpenAI 兼容端点 |
| 应用 | `valid_sources` | `["ai","java","test","ops","bigdata"]` | 有效学科来源（用于过滤） |
| 应用 | `customer_service_phone` | 12345678 | 兜底人工客服电话 |
| 日志 | `log_file` | logs/app.log | 日志路径 |

**读表要点**：`retrieval_k`（召回）与 `candidate_m`（精选）是两个不同阶段的量——
召回阶段宁多勿漏，精选阶段宁精勿滥。这是 RAG 调优最常用的两个旋钮。

## 2. 关键机制

### 2.1 文档解析：多格式 + 分层切分

**多格式支持**：`document_processor.py` 用「扩展名 → 加载器」的字典做分发，扩展只需加一行。

| 扩展名 | 加载器 | 说明 |
|---|---|---|
| `.txt` | `TextLoader` | 需指定 `encoding="utf-8"` |
| `.pdf` | `OCRPDFLoader` | 走 OCR，能识别扫描件 |
| `.docx` | `OCRDOCLoader` | Word 文档 |
| `.ppt` / `.pptx` | `OCRPPTLoader` | 演示文稿 |
| `.jpg` / `.png` | `OCRIMGLoader` | 图片（**图片或表格采用 PaddleOCR 实现识别**） |
| `.md` | `UnstructuredMarkdownLoader` | Markdown |

**为什么需要 OCR 加载器**：、扫描 PDF、图表里的文字**没有文本层**，
普通 `PyPDFLoader` 抽出来是空的；OCR 才能把它们变成可检索的文本。

**元数据注入**（每个 `Document` 都带上）：

| 元数据 | 来源 | 用途 |
|---|---|---|
| `source` | 目录名去掉 `_data`（如 `ai_data` → `ai`） | **学科过滤**（对应 `valid_sources`） |
| `file_path` | 文件完整路径 | 溯源、按格式选切分器 |
| `timestamp` | 处理时刻的 ISO 时间 | 时效管理 |

**分层切分（父块 / 子块）**是整套方案的核心：

| 层级 | 大小 | 切分器 | 作用 |
|---|---|---|---|
| 父块 | `parent_chunk_size=1200` | `ChineseRecursiveTextSplitter` 或 `MarkdownTextSplitter` | 提供完整上下文，交给 LLM |
| 子块 | `child_chunk_size=300` | 同上（更小粒度） | **建立向量索引**、参与检索 |

流程：文档 → 父块（`parent_id = doc_{i}_parent_{j}`，并把父块原文写进 `parent_content` 元数据）
→ 每个父块再切成子块（`id = {parent_id}_child_{k}`，同时带上 `parent_id` 与 `parent_content`）。

**为什么用「子块检索 + 父块返回」**：子块小，向量表示聚焦、检索精度高；父块大，上下文完整、生成质量好。
检索命中的是子块，但送给 LLM 的是它所属的**父块原文**，一举两得。
**Markdown 文件用专用切分器**：按标题层级切，天然贴合文档结构。

### 2.2 Prompt 模板设计：一个类管所有模板

`RAGPrompts` 用 `@staticmethod` 集中提供四个模板：

| 模板 | 输入变量 | 作用 |
|---|---|---|
| `rag_prompt` | `context`、`question`、`phone` | 核心回答模板；有上下文就基于上下文答，没有就直接用知识答；**答案来自检索文档时要说明**；无法回答时兜底「信息不足，请联系人工客服，电话：{phone}」 |
| `hyde_prompt` | `query` | 生成假设答案，供 HyDE 策略使用 |
| `subquery_prompt` | `query` | 把复杂查询分解为多个子查询（**每行一个**） |
| `backtracking_prompt` | `query` | 把复杂查询简化为一个更基础的问题 |

三个设计要点值得记住：
① **兜底话术内置在模板里**（带客服电话），避免模型在信息不足时编造答案；
② **要求说明来源**（「如果答案来源于检索到的文档，请在回答中说明」），提升可追溯性；
③ **子查询模板规定「每行一个」**，让输出可直接 `split("\n")` 解析。

### 2.4 检索策略选择：让 LLM 做「路由」而不是「回答」

`StrategySelector` 用一个 Prompt 让 LLM 从四种策略里挑一个，并且**要求只返回策略名称、不解释过程**。

| 策略 | 描述 | 适用场景 | 示例 |
|---|---|---|---|
| 直接检索 | 对查询直接检索，不做增强 | 意图明确、要检索**特定信息** | 「人工智能方向学费是多少？」「JAVA 的大纲是什么？」 |
| 假设问题检索（HyDE） | 先生成假设答案，再基于假设答案检索 | 查询较为**抽象**，直接检索效果不佳 | 「人工智能在教育领域的应用有哪些？」 |
| 子查询检索 | 把复杂查询拆成多个简单子查询，分别检索再合并 | 查询涉及**多个实体或方面** | 「比较 Milvus 和 Zilliz Cloud 的优缺点」 |
| 回溯问题检索 | 把复杂查询转成更基础、更易检索的问题 | 查询过于复杂，**需要简化**才能有效检索 | 「我有 100 亿条记录的数据集想存进 Milvus 查询，可以吗？」 |

工程细节：
- `temperature=0.1`（要确定性，但留一点容错）；
- **异常兜底返回「直接检索」**——策略选择失败不能让整个链路崩掉；
- 用 `logger` 记录每条查询选中的策略，便于观察与调优。

### 2.5 四种检索策略的实现要点

`rag_system.py` 把策略落到四个方法上：

| 方法 | 实现 | 注意点 |
|---|---|---|
| `_retrieve_with_hyde` | 用 `hyde_prompt` 生成假设答案 → 用**假设答案**去检索 | 注释指出「HyDE 通常只用于生成检索向量，不一定需要 rerank 这一步」 |
| `_retrieve_with_subqueries` | 生成子查询 → 逐个检索 → 合并 → **按 `page_content` 去重** | 每个子查询都做混合检索 + 重排，**开销可能较大** |
| `_retrieve_with_backtracking` | 生成简化问题 → 用简化问题检索 | 降低检索难度 |
| 默认（直接检索） | 用原查询做混合检索，支持 `source_filter` | 按学科过滤 |

**去重的正确做法**：代码里先注释掉了「基于对象内存地址」的思路，改为
`{doc.page_content: doc for doc in all_docs}`——**基于内容去重**。
注释明确指出：如果 Document 内容相同但对象不同，按内存地址无法去重。这是很典型的一课。

**统一收敛**：无论走哪条策略，最终都在 `retrieve_and_merge` 里做 `ranked_sub_chunks[:candidate_m]`，
即**所有策略共用同一个「精选阶段」**，保证送给 LLM 的上下文长度可控。

### 2.7 Query 改写：RAG 的第一步

用户提问方式与期望答案之间存在差距，用户问题通常有两类毛病：

| 问题类型 | 表现 |
|---|---|
| 信息不完整 | 提问没有表达清楚所有关键信息 |
| 噪声问题 | 提问包含了与答案无关的内容 |

**四类信息不完整 + 三类噪声问题的改写手法**：

| 手法 | 解决什么 | 改写示例 |
|---|---|---|
| 历史会话改写 | 多轮对话中 query 缺少上下文（指代消解） | 前文问「华为 meta70 性能怎么样」，用户接着说「摄像头方面具体改进了什么？」 → 改写为「**华为 meta70 手机的摄像头相比 meta60 有哪些具体改进？**」 |
| 关键词改写 | 用户输入的关键词太短、缺上下文，影响**语义（向量）检索**效果 | 「机器学习实践」 → 「机器学习在实际应用中的案例有哪些？哪些工具和方法适用于机器学习实践？」 |
| 伪答案改写 | 通过加入假设性答案增强查询的**语义丰富性** | 「如何提高企业的市场竞争力？」 → 「如何提高企业的市场竞争力？**比如通过创新产品、优化营销策略或提升客户服务等手段。**」 |
| 缩写词改写 | 用户用缩写，文档用全称 | 「VR 技术在教育中的应用」 → 「**虚拟现实（Virtual Reality）**技术在教育中的应用有哪些？可以举一些实际的应用案例吗？」 |
| 去冗余改写 | 去掉无关成分（多余修饰语、模糊表达、无关背景） | 「我最近在准备面试，但对于算法的理解还不太够，能推荐一些有效的学习资源吗？」 → 「有哪些有效的学习资源可以帮助提高算法理解？」 |
| 关键词提取改写 | 提取核心关键词、去停用词与语气词，**特别适合 BM25 类关键词检索** | 「关于 Java 中的线程池，常见的实现方式有哪些？」 → 「Java 线程池常见实现方式」 |
| 子查询改写 | 对比类查询中多个实体相互干扰，需拆分 | 「C++ 和 Go 哪个更适合做系统编程？」 → 「C++ 适合做系统编程的优点有哪些？」；「Go 适合做系统编程的优点有哪些？」 |

**改写质量的边界**：改写后的 query 质量**在很大程度上依赖 prompt 和大模型的能力**。
通常改写能提升召回准确性，但**有时仍会改写失败**。因此工程建议是：
**多次改写，或把查询拆成多个独立查询**，然后把所有召回结果交给**重排序（reranking）模型**精确排序，
最后由大模型生成答案。即：**改写阶段宁可多召回，用重排序阶段来保证精度。**

给出的开源 RAG 改写 Prompt 模板（可复用）：

```text
您是查询扩展方面的专家，能够生成问题的释义。
我无法直接使用用户的问题从知识库中检索相关信息。
您需要通过多种方式扩展或释义用户的问题，例如使用同义词/短语、完整地写出缩写、
添加一些额外的描述或解释、改变表达方式、将原始问题翻译成另一种语言（英语/中文）等。
并返回 5 个版本的问题，其中一个来自翻译。
只需列出问题。不需要其他单词。
```

### 2.8 混合检索与重排序

`VectorStore.hybrid_search_with_rerank(query, k, source_filter)` 是检索侧的统一入口：

| 环节 | 做法 |
|---|---|
| 双路检索 | BGE-M3 同时产出**稠密向量**（语义）与**稀疏向量**（关键词权重），分别走 `IVF_FLAT` 与 `SPARSE_INVERTED_INDEX` |
| 过滤 | 支持 `source_filter` 按学科过滤（对应 `valid_sources`） |
| 融合重排 | `WeightedRanker`（明确侧重时）或 `RRFRanker`（默认） |
| 返回 | **重排后的父文档**（`_doc_from_hit` 把 Milvus 命中结果转成 `Document` 对象） |

**为什么必须重排序**：两路检索的分数不可直接比较，必须先融合排序，再截取 Top-M 作为上下文。
详见《07-向量数据库与Milvus》2.5。

### 2.10 物流行业 RAG 项目：最小可运行版

第五章的物流项目是一个「去掉所有花活」的最小实现，非常适合作为第一个练手项目：

| 步骤 | 做法 |
|---|---|
| 建库 | `PyMuPDFLoader("物流信息.pdf")` → `RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=20)` → `OllamaEmbeddings(model="mxbai-embed-large")` → `FAISS.from_documents(...)` 并 `save_local("./faiss/wuliu")` |
| 问答 | 加载 FAISS → `similarity_search(question, k=2)` → 拼接 `context` → `PromptTemplate` 组装 → `Ollama(model="qwen2.5:7b").invoke` |
| Web | `streamlit` + `ConversationalRetrievalChain.from_llm(llm=..., retriever=db.as_retriever)` |

它的 Prompt 模板极简但把关键约束写清楚了：

```text
基于以下已知信息，简洁和专业的来回答用户的问题。不允许在答案中添加编造成分。
已知内容: {context}
问题: {question}
```

**「不允许在答案中添加编造成分」这句话是 RAG Prompt 的必备约束**——它把模型从「自由发挥」切换为「依据材料作答」。

## 3. 可运行示例

```text
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

docs = TextLoader("data/物流信息.txt", encoding="utf-8").load()

# 1) 分层切块：父块给 LLM，子块建索引（子块携带父块 id 与原文）
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=60, chunk_overlap=10)
children = []
for i, doc in enumerate(docs):
 for j, parent in enumerate(parent_splitter.split_documents([doc])):
 pid = f"doc_{i}_parent_{j}"
 for k, child in enumerate(child_splitter.split_documents([parent])):
 child.metadata.update({"id": f"{pid}_child_{k}", "parent_id": pid,
 "parent_content": parent.page_content})
 children.append(child)

# 2) 向量化入库并持久化
embeddings = OllamaEmbeddings(model="mxbai-embed-large", temperature=0)
db = FAISS.from_documents(children, embeddings)
db.save_local("faiss/wuliu")


# 3) 检索 + 父块返回（命中子块，用父块原文替换以补全上下文）
def retrieve_context(question, k=3):
 parents, seen = [], set()
 for h in db.similarity_search(question, k=k):
 pid = h.metadata.get("parent_id")
 if pid and pid not in seen:
 seen.add(pid)
 parents.append(h.metadata.get("parent_content", h.page_content))
 return parents


# 4) 生成：Prompt 必须约束「不许编造」，并给出兜底话术
TEMPLATE = """基于以下已知信息，简洁和专业的来回答用户的问题。不允许在答案中添加编造成分。
如果已知信息不足以回答，请回答「已知信息不足，无法回答」。

已知内容:
{context}

问题:
{question}
回答:"""
prompt = PromptTemplate(input_variables=["context", "question"], template=TEMPLATE)
llm = Ollama(model="qwen2.5:7b", temperature=0)

for q in ["从上海发往北京用顺丰要多久？", "海运到南美洲需要几天？"]:
 ctx = "\n".join(retrieve_context(q, k=3))
 print("Q:", q)
 print("A:", llm.invoke(prompt.format(context=ctx, question=q)))
```

## 4. 常见坑

| 坑 | 现象 | 原因 | 正确做法 |
|---|---|---|---|
| 只切一种粒度 | 检索不准或上下文残缺 | 粒度两难 | 父块 1200 / 子块 300 分层切分，**子块检索、父块返回** |

## 5. 面试问答

**Q1：请完整描述 RAG 的工作流程，并说明每一步的关键设计决策。**

<details markdown="1">
<summary markdown="1">参考答案</summary>

| 阶段 | 做什么 | 关键决策 |
|---|---|---|
| ① 查询分类 | 判断是「通用知识」还是「专业咨询」 | 通用知识**直接问 LLM**、跳过检索，省一次检索开销；用小 BERT 而非大模型做路由（低延迟、低成本） |
| ② Query 改写 | 补全指代、扩展关键词、扩展缩写、去冗余、拆分对比查询 | 宁可多召回，改写失败时靠重排序兜底；多轮对话必须做历史会话改写 |
| ③ 策略选择 | 让 LLM 从直接检索 / HyDE / 子查询 / 回溯中选一种，只返回策略名 | `temperature` 调低；异常兜底为「直接检索」 |
| ④ 文档检索 | BGE-M3 同时产出稠密与稀疏向量，做混合检索 + 重排序，返回**父块** | `retrieval_k` 放大召回、`candidate_m` 收紧上下文；支持 `source_filter` 按来源过滤 |
| ⑤ 生成回答 | 用模板拼 `context + question`，约束「不许编造、须说明来源、无法回答时给兜底话术」 | 兜底话术内置客服电话；异常时也返回可用回复 |

核心思想：**把「不确定」的环节（改写、策略）放在前面对齐意图，把「要精度」的环节（重排序、精选）放在后面收口**。

</details>

**Q2：RAG 相比微调有什么优势？什么情况下反而应该微调？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

RAG 的优势：
1. **知识与参数解耦**——更新知识只需重建索引，不必重新训练，避免「知识过时」；
2. **可溯源**——能返回引用来源，便于审计与人工复核，这在金融/医疗/教育场景是硬要求；
3. **成本低**——不需要标注大量数据、不需要 GPU 训练；
4. **抗幻觉**——通过「只依据作答」的约束显著降低编造；
5. **支持实时/私有数据**——这正是强调的痛点（模型基于过去数据训练，拿不到企业私有知识）。

应该考虑微调的情况：
① 需要模型掌握**固定的输出风格或领域语言习惯**（如特定格式的医嘱、财报口径）；
② 任务形态稳定、调用量极大，微调后用小模型推理比「大模型 + 长上下文」更便宜；
③ 需要把**领域术语理解能力**内化（检索只能提供材料，理解能力仍取决于模型）；
④ 数据不能出域且必须私有化部署时的性能优化。

实践上二者常**组合**：微调负责「会说话、懂术语」，RAG 负责「有依据、可更新」。

</details>

**Q3：HyDE、子查询、回溯三种策略分别解决什么问题？为什么需要「让 LLM 选策略」？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

- **HyDE（假设问题检索）**：解决「查询过于抽象、与文档用词不匹配」的问题。
 先让 LLM 生成一个假设答案，再用**假设答案**去检索——因为假设答案的用词风格更接近真实文档，
 在向量空间里更容易命中。
- **子查询检索**：解决「一个查询包含多个实体或方面」的问题。
 例如「比较 Milvus 和 Zilliz Cloud 的优缺点」，直接检索会让两个实体的信息互相干扰；
 拆成两个独立子查询分别检索再合并去重，可以各取所需。
- **回溯问题检索**：解决「查询太具体/太复杂，知识库里只有更基础的知识」的问题。
 例如「100 亿条记录能不能存进 Milvus」，先简化为「Milvus 的数据规模上限是多少」再检索。

需要「让 LLM 选策略」的原因是：**不同查询需要不同的检索前置处理，用固定一种策略会顾此失彼**。
直接检索对明确查询最省成本也最准；对抽象查询却很糟。用 LLM 做这个判断成本极低（一次短输出），
却能让每种查询都走最合适的前置处理。工程上必须加**兜底默认值**（选不出来就用直接检索），
并记录所选策略以便观察效果。

</details>

## 6. 自测题

**1. 为什么要做「父子分层切分」？说明父块与子块各自的用途。**

<details markdown="1">
<summary markdown="1">参考答案</summary>

切片粒度存在两难：切得太细，单块语义聚焦、向量表示准、检索精度高，但上下文被割裂，LLM 缺依据；
切得太粗，上下文完整，但一个向量要代表多个主题，检索精度下降。

分层切分同时拿到两者好处：**子块（如 300 字）用于建立向量索引和检索**（精度），
**父块（如 1200 字）原文存在元数据里，命中子块后返回其父块内容**（完整性）。
实现上子块需携带 `parent_id` 与 `parent_content` 元数据；检索后按 `parent_id` 去重、取父块原文拼上下文。

</details>

**2. Query 改写主要解决用户的哪两类问题？各举一种改写手法。**

<details markdown="1">
<summary markdown="1">参考答案</summary>

两类问题是：**信息不完整**（提问没表达清楚所有关键信息）与**噪声问题**（提问包含与答案无关的内容）。

- 针对信息不完整：**历史会话改写**——多轮对话中当前 query 缺少上下文，
 如「摄像头方面具体改进了什么？」改写为「华为 meta70 手机的摄像头相比 meta60 有哪些具体改进？」；
 也可用**缩写词改写**（VR → 虚拟现实 Virtual Reality）、**关键词改写**（「机器学习实践」→ 补充完整语境）。
- 针对噪声问题：**去冗余改写**——去掉无关背景（「我最近在准备面试……」），只留核心意图；
 **关键词提取改写**——去停用词与语气词，输出「Java 线程池常见实现方式」，特别适合 BM25 类关键词检索。

另外**子查询改写**针对对比类查询，把多实体查询拆成多个独立查询。

</details>

**3. RAG 为什么用 BERT 做查询分类而不直接让 LLM 判断？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

因为查询意图分类是**高频、低难度、对延迟敏感**的任务：每条用户查询都要过一次路由。
用 `bert-base-chinese` 微调的二分类器（5000 条数据、3 个 epoch、验证准确率约 93%）在 CPU 上毫秒级完成，
而调用 LLM 需要数百毫秒到数秒且按 token 计费。用 LLM 做这个判断在成本与延迟上都不划算。

原则是：**确定性判断用判别式小模型，开放生成用大模型**。还记录了这个模块的一个真实修复——
`evaluate_model` 中把已经是数字的标签又映射了一次导致 `KeyError: 1`，
修复方式是直接使用数字标签，只对 texts 分词。这提醒我们：标签空间在训练/评估/预测三处必须口径统一。

</details>

**4. 物流 RAG 项目的 Prompt 里为什么要写「不允许在答案中添加编造成分」？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

因为大模型的默认行为是**用参数知识补全**：即使检索到的不包含答案，它也会顺着问题生成一个看起来合理的回答，
这就是 RAG 场景下最常见的幻觉来源。写上这句约束后，模型被限制在「依据给定材料作答」的模式里。

更完整的写法还应包含兜底路径，例如：
「如果已知信息不足以回答，请回答『已知信息不足，无法回答』」，
 RAG 的 `rag_prompt` 更进一步，直接给出「信息不足，无法回答，请联系人工客服，电话：{phone}」，
把「答不出来」也变成一次可用的用户体验。**验收测试**：故意问一个知识库里没有的问题（如「海运到南美洲几天」），
看系统是否老实说不知道。

</details>

## 7. 延伸阅读

- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (arXiv:2005.11401)](https://arxiv.org/abs/2005.11401)
- [REALM (arXiv:2002.08909)](https://arxiv.org/abs/2002.08909)
- [RAG 综述 (arXiv:2312.10997)](https://arxiv.org/abs/2312.10997)
- [LangChain 官方文档](https://python.langchain.com/docs/introduction/)
- [Milvus 官方文档](https://milvus.io/docs)

---

[⬅️ 返回本目录索引](README.md)
