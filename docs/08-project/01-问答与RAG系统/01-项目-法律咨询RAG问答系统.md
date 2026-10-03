# 项目实战笔记 01：法律咨询 RAG 问答系统

> **一句话总结**：用 LangChain + BGE-M3 + Milvus 搭一套"MySQL FAQ 精确匹配优先、Milvus 混合检索兜底"的双通道法律咨询 RAG 问答系统，把大模型的幻觉关在知识库的笼子里。
> **前置知识**：Python 工程化基础、向量检索原理（Embedding / 余弦相似度 / ANN）、LangChain 的 Document 与 TextSplitter 抽象、FastAPI 基础、MySQL 与 Redis 基本操作。

> 1. 独立设计一套"分层切分（父块 + 子块）+ 混合检索 + 重排序"的 RAG 检索链路；
> 2. 用 QueryClassifier 做查询路由，把"闲聊/常识"与"专业咨询"分流，省掉无效检索开销；
> 3. 用 RAGAS 的四个指标量化评估自己的 RAG 系统，而不是靠"感觉回答得还行"。

## 1. 项目目标与业务背景

### 1.1 业务痛点

法律咨询长期依赖人工客服：当事人问"劳动合同纠纷的仲裁时效是多久""租房押金不退怎么办""工伤赔偿标准是多少"，客服每天重复回答高度相似的问题。引入 ChatGPT 类大模型后又出现新问题：

- **幻觉**：模型对"我们律所自己的收费标准、办案流程、材料清单"这类私有信息一无所知，会一本正经地编；
- **时效性**：训练数据截止后新增的信息无法感知；
- **成本**：全量微调（SFT/LoRA）要标注数据、要 GPU，信息一变就得重训，迭代成本极高。

### 1.2 两种解法与选择

| 路线 | 做法 | 本项目取舍 |
| --- | --- | --- |
| 垂直领域微调 | 把企业知识灌进模型权重 | 成本高、知识更新要重训，**放弃** |
| RAG | 知识放外部库，检索后再生成 | 知识可热更新、可溯源、可解释，**采用** |

最终形态是 **RAG 融合问答系统**：MySQL 存高频 FQA（命中即返回，快且准）+ Milvus 存文档切片（兜底，覆盖长尾）+ Redis 做热点缓存 + FastAPI/WebSocket 对外提供流式问答。

### 1.3 关键业务指标

- FAQ 通道命中率：BM25+Softmax 相似度 ≥ 0.85 才认，宁可不答也不乱答；
- 知识库通道：Top-K 检索 + 重排序后只取 2 个父块进 Prompt，控制 token 成本；
- 端到端体验：WebSocket 逐 token 流式输出，首字延迟可感知地降低。

## 2. 技术架构

```text
 ┌──────────────────────────────┐
 用户 / WebUI ──────▶│ FastAPI (app.py) │
 │ POST /api/query (非流式) │
 │ WS /api/stream (流式) │
 └───────────────┬──────────────┘
 │
 ┌───────────▼────────────┐
 │ 日常问候正则短路 │
 │ GREETING_PATTERNS │
 └───────────┬────────────┘
 │
 ┌──────────────────▼───────────────────┐
 │ IntegratedQASystem.query │
 │ (生成器：yield (token, is_complete)) │
 └───────┬──────────────────────┬───────┘
 │ ①先走 FAQ │ ②兜底走 RAG
 ┌─────────▼─────────┐ ┌────────▼──────────────────┐
 │ Redis 答案缓存 │ │ QueryClassifier (BERT) │
 │ ↓ miss │ │ 通用知识 → 直接问 LLM │
 │ BM25Okapi + jieba │ │ 专业咨询 → 进入检索 │
 │ Softmax 归一化 │ └────────┬──────────────────┘
 │ 阈值 ≥ 0.85 ? │ │
 └─────────┬─────────┘ ┌────────▼──────────────────┐
 │ hit │ StrategySelector (LLM) │
 │ │ 直接/HyDE/子查询/回溯 │
 │ └────────┬──────────────────┘
 │ │
 │ ┌─────────────▼───────────────┐
 │ │ VectorStore │
 │ │ BGE-M3 → dense+sparse │
 │ │ Milvus hybrid_search │
 │ │ 子块命中→回溯父块→去重 │
 │ │ BGE-Reranker 精排 │
 │ └─────────────┬───────────────┘
 │ │ 父块上下文
 └──────────┬───────────┘
 ▼
 ┌────────────────────────┐
 │ rag_prompt 拼上下文 │
 │ Qwen2.5-7B / qwen-plus │
 │ 无答案→转人工兜底 │
 └────────────┬───────────┘
 ▼
 答案回写 MySQL conversations 表（保留最近 5 轮）
```

### 离线索引管线

```text
data/{statute,judicial,cases,faq,procedure}_data/
 │ load_documents_from_directory 按扩展名选 Loader
 │ .txt→TextLoader .pdf/.docx/.ppt/.jpg→OCR 类 Loader
 │ 同时写入 metadata: source / file_path / timestamp
 ▼
 parent_splitter (chunk=1200) ──▶ 父块，metadata.parent_content = 父块全文
 ▼
 child_splitter (chunk=300, overlap=50) ──▶ 子块，继承 parent_id
 ▼
 BGE-M3 编码 → dense_vector(1024) + sparse_vector(词权重)
 ▼
 Milvus upsert，主键 = md5(子块文本) ← 幂等，重复灌库不会产生脏数据
```

### 检索时的"小块检索、大块喂给 LLM"

```text
query ──▶ BGE-M3 ──▶ dense AnnSearchRequest ─┐
 └▶ sparse AnnSearchRequest ─┴─▶ WeightedRanker(0.7, 1.0)
 ──▶ Top-K 子块（精准但缺上下文）
 ──▶ 按 parent_content 去重，回溯成父块（完整但略粗）
 ──▶ BGE-Reranker 对 (query, 父块) 逐对打分重排
 ──▶ 取 CANDIDATE_M=2 个父块进 Prompt
```

## 3. 关键技术选型与理由

| 方案 | 优点 | 代价 | 本项目为何选它 |
| --- | --- | --- | --- |
| MySQL FQA + BM25 | 高频问题毫秒级命中，答案 100% 可控 | 只能答库里有的问法，同义改写会漏 | 客服场景 80% 流量是高频问题，先拦掉最省钱 |
| BM25Okapi vs BM25L | Okapi 是工业默认，参数语义清晰 | 对长文档需长度归一化调参 | 问题本身很短（<50 字），长度差异小，Okapi 够用 |
| Redis 缓存 | 命中后连 BM25 都不用算 | 多一个组件要运维，缓存要处理失效 | 答案几乎不变，缓存收益远大于成本 |
| BGE-M3（稠密+稀疏一体） | 一次推理同时产出两种向量，中文检索 SOTA 级 | 模型 ~2GB，CPU 推理慢 | 省一套 embedding 服务，混合检索开箱即用 |
| Milvus | 原生支持 hybrid_search + WeightedRanker，稀疏倒排索引成熟 | 需要单独部署，运维成本高于 FAISS | 要同时管稠密+稀疏+标量过滤，FAISS 做不到 |
| 分层切分（父 1200 / 子 300） | 检索用小块保精度，生成用父块保上下文 | 存储放大一倍（父块内容冗余存在每个子块上） | 法律法规与合同文本段落层级强，"小节"是天然的语义单元 |
| BGE-Reranker-large（CrossEncoder） | 精排显著提升 Top-2 命中率 | 每次推理要跑 N 对，是本链路最大延迟源 | 只对最终候选（≤5 个父块）重排，成本可控 |
| 查询路由（BERT 二分类） | 常识题不再白跑一遍向量检索 | 要多训一个小模型，有误分类风险 | 用户大量问"民法是什么"这类题，必须短路 |
| 策略选择交给 LLM | 无需硬编码规则即可适配抽象/复合问题 | 多一次 LLM 调用（~1s），输出可能不规范 | 用 temperature=0.1 + 严格"只输出策略名"约束 |

> **被放弃的方案**：全量 SFT 微调。理由是知识更新频率远高于模型训练频率；另外也没有必要为了"答得准"牺牲"可溯源"。

## 4. 核心实现

### 4.1 分层切分：给子块装上"回溯指针"

这是整个系统的地基。子块只用于**检索**，父块才用于**生成**。

```python
# core/document_processor.py（精简）
def process_documents(directory_path, parent_chunk_size=1200,
child_chunk_size=300, chunk_overlap=50):
    documents = load_documents_from_directory(directory_path) # 已带 source/file_path 元数据
    parent_splitter = ChineseRecursiveTextSplitter(parent_chunk_size, chunk_overlap)
    child_splitter = ChineseRecursiveTextSplitter(child_chunk_size, chunk_overlap)
    child_chunks = []
    for i, doc in enumerate(documents):
        for j, parent_doc in enumerate(parent_splitter.split_documents([doc])):
            parent_id = f"doc_{i}_parent_{j}"
            # 关键：把父块全文塞进每个子块的元数据里，检索后无需二次查库
            parent_doc.metadata["parent_id"] = parent_id
            parent_doc.metadata["parent_content"] = parent_doc.page_content

            for k, sub in enumerate(child_splitter.split_documents([parent_doc])):
                sub.metadata.update(parent_id=parent_id,
                parent_content=parent_doc.page_content,
                id=f"{parent_id}_child_{k}")
                child_chunks.append(sub)
                return child_chunks
```

**为什么这么写**：如果把 `parent_content` 只存下来做 join，检索后就要再查一次 Milvus；直接冗余进子块，一次检索就能拿到完整上下文。代价是存储放大，但文档总量只有 MB 级，完全可接受。

### 4.2 Milvus Schema 与双索引

```python
# core/vector_store.py（精简）
schema = client.create_schema(auto_id=False, enable_dynamic_field=True)
schema.add_field("id", DataType.VARCHAR, is_primary=True, max_length=100)
schema.add_field("text", DataType.VARCHAR, max_length=65535)
schema.add_field("dense_vector", DataType.FLOAT_VECTOR, dim=self.dense_dim)
schema.add_field("sparse_vector", DataType.SPARSE_FLOAT_VECTOR)
schema.add_field("parent_id", ...); schema.add_field("parent_content", ...)
schema.add_field("source", ...); schema.add_field("timestamp", ...)

index_params.add_index("dense_vector", index_type="IVF_FLAT",
metric_type="IP", params={"nlist": 128})
index_params.add_index("sparse_vector", index_type="SPARSE_INVERTED_INDEX",
metric_type="IP", params={"drop_ratio_build": 0.2})
```

- `auto_id=False` + 主键取 `md5(子块文本)`：**天然幂等**。重跑灌库脚本时 `upsert` 会覆盖而不是追加，这点在调试期反复重灌时救命。
- `metric_type="IP"`：BGE 系列输出已归一化，内积等价于余弦且更快。
- `source` 字段支撑"只查 劳动法"的标量过滤，是业务方最常提的需求。

### 4.3 混合检索 + 重排序

```python
def hybrid_search_with_rerank(self, query, k=5, source_filter=None):
    emb = self.embedding_function([query])
    dense_q = emb["dense"][0]
    row = emb["sparse"].getrow(0)
    sparse_q = {int(i): float(v) for i, v in zip(row.indices, row.data)}

    expr = f"source == '{source_filter}'" if source_filter else ""
    reqs = [
    AnnSearchRequest([dense_q], "dense_vector",
    {"metric_type": "IP", "params": {"nprobe": 10}}, limit=k, expr=expr),
    AnnSearchRequest([sparse_q], "sparse_vector",
    {"metric_type": "IP", "params": {}}, limit=k, expr=expr),
    ]
    # 稀疏权重 0.7 / 稠密权重 1.0 —— 业务术语（法条编号、案由名）靠稀疏，语义靠稠密
    hits = self.client.hybrid_search(self.collection_name, reqs,
    ranker=WeightedRanker(0.7, 1.0),
    limit=k,
    output_fields=["text", "parent_id",
    "parent_content", "source", "timestamp"])[0]

    sub_chunks = [self._doc_from_hit(h["entity"]) for h in hits]
    parent_docs = self._get_unique_parent_docs(sub_chunks) # 按 parent_content 去重
    if len(parent_docs) < 2:
        return parent_docs[:conf.CANDIDATE_M] # 候选太少，重排无意义

    scores = self.reranker.predict([[query, d.page_content] for d in parent_docs])
    ranked = [d for _, d in sorted(zip(scores, parent_docs), reverse=True)]
    return ranked[:conf.CANDIDATE_M]
```

**两个容易忽略的工程细节**：
1. `_get_unique_parent_docs` 必须**先回溯父块再去重**：多个子块往往来自同一个父块，若先重排会浪费算力在重复内容上。
2. `len(parent_docs) < 2` 时直接返回：CrossEncoder 对 1 个候选打分纯属浪费，且排序结果无意义。

### 4.4 查询分类：便宜的分流器

```python
class QueryClassifier:
    label_map = {"通用知识": 0, "专业咨询": 1}

    def __init__(self, model_path="bert_query_classifier"):
        self.tokenizer = BertTokenizer.from_pretrained("./bert-base-chinese")
        self.device = torch.device("cuda" if torch.cuda.is_available else "cpu")
        self.model = (BertForSequenceClassification.from_pretrained(model_path)
        if os.path.exists(model_path)
    else BertForSequenceClassification.from_pretrained(
    "bert-base-chinese", num_labels=2))
    self.model.to(self.device)

    def predict_category(self, query):
        if self.model is None:
            return "通用知识" # 兜底：走便宜路径
        enc = self.tokenizer(query, truncation=True, padding=True,
        max_length=128, return_tensors="pt")
        enc = {k: v.to(self.device) for k, v in enc.items}
        with torch.no_grad:
            logits = self.model(**enc).logits
            return "专业咨询" if torch.argmax(logits, 1).item == 1 else "通用知识"
```

训练用 5000 条混合数据集（`training_dataset_hybrid_5000.json`），`bert-base-chinese` 微调 3 epoch、batch=8，验证集准确率约 93%，混淆矩阵 `[[460, 40], [30, 470]]`。**之所以不用规则**：当事人问法太散，"押金不退"和"能不能退押金"要靠语义。

### 4.5 LLM 驱动的检索策略选择

```text
class StrategySelector:
 def select_strategy(self, query):
 # 提示词里给出四种策略的"描述 + 适用场景 + 正例"，并要求"直接返回策略名称"
 try:
 completion = self.client.chat.completions.create(
 model=conf.LLM_MODEL,
 messages=[{"role": "system", "content": "你是一个有用的助手。"},
 {"role": "user", "content": self.strategy_prompt.format(query=query)}],
 temperature=0.1, # 只要分类结果，不要创造性
 )
 return completion.choices[0].message.content or "直接检索"
 except Exception as e:
 logger.error(f"DashScope API 调用失败: {e}")
 return "直接检索" # 失败降级到最稳的策略
```

四种策略与 RAG 核心调度：

```python
def retrieve_and_merge(self, query, source_filter=None, strategy=None):
    strategy = strategy or self.strategy_selector.select_strategy(query)
    if strategy == "回溯问题检索":
        docs = self._retrieve_with_backtracking(query) # 化简后再检索
    elif strategy == "子查询检索":
        docs = self._retrieve_with_subqueries(query) # 拆解 + 各自检索 + 按内容去重
    elif strategy == "假设问题检索":
        docs = self._retrieve_with_hyde(query) # 生成假设答案再检索
    else:
        docs = self.vector_store.hybrid_search_with_rerank(
        query, k=conf.RETRIEVAL_K, source_filter=source_filter)
        return docs[:conf.CANDIDATE_M]

    def generate_answer(self, query, source_filter=None):
        if self.query_classifier.predict_category(query) == "通用知识":
            return self.llm(self.rag_prompt.format(context="", question=query,
        phone=conf.CUSTOMER_SERVICE_PHONE))
        docs = self.retrieve_and_merge(query, source_filter)
        context = "\n\n".join(d.page_content for d in docs) if docs else ""
        return self.llm(self.rag_prompt.format(context=context, question=query,
    phone=conf.CUSTOMER_SERVICE_PHONE))
```

子查询去重那一行曾被写错成基于对象地址去重，正确写法是基于内容：

```python
unique_docs = list({doc.page_content: doc for doc in all_docs}.values)
```

### 4.6 双通道融合 + 流式输出

```python
class IntegratedQASystem:
    def query(self, query, source_filter=None, session_id=None):
        history = self.get_session_history(session_id) if session_id else []
        answer, need_rag = self.bm25_search.search(query, threshold=0.85)
        if answer: # FAQ 命中，一次性返回
            if session_id: self.update_session_history(session_id, query, answer)
            yield answer, True
            return
        if need_rag: # 兜底：流式生成
            collected = ""
            for token in self.rag_system.generate_answer(query, source_filter, history):
                collected += token
                yield token, False
                if session_id: self.update_session_history(session_id, query, collected)
                yield "", True
            else:
                yield "未找到答案", True
```

`conversations` 表按 `session_id` 保留最近 5 轮，超出部分在同一个事务里删除：

```sql
DELETE FROM conversations
WHERE session_id = %s AND id NOT IN (
 SELECT id FROM (
 SELECT id FROM conversations WHERE session_id = %s
 ORDER BY timestamp DESC LIMIT %s
 ) AS sub
)
```

**注意**：MySQL 不允许在 `DELETE` 的子查询里直接引用被删的表，必须再套一层派生表 `AS sub`，这是很多人写会话裁剪时会踩的语法坑。

### 4.7 用 RAGAS 量化评估

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_relevancy, context_recall
from datasets import Dataset

data = json.load(open("rag_evaluation_dataset.json", encoding="utf-8"))
dataset = Dataset.from_dict({
"question": [d["question"] for d in data],
"answer": [d["answer"] for d in data],
"contexts": [d["context"] for d in data], # 必须是 list
"ground_truth": [d["ground_truth"] for d in data],
})

result = evaluate(dataset=dataset,
metrics=[faithfulness, answer_relevancy, context_relevancy, context_recall],
llm=ChatOpenAI(model="gpt-4", openai_api_key=KEY),
embeddings=OpenAIEmbeddings(openai_api_key=KEY))
pd.DataFrame([result]).to_csv("ragas_evaluation_results.csv", index=False)
```

四个指标的语义要分清：`context_relevancy / context_recall` 诊断**检索**，`faithfulness / answer_relevancy` 诊断**生成**。调检索策略时只盯前两个，调 Prompt 时只盯后两个——否则改完不知道是哪一步变好的。

## 5. 踩坑与解决

| 现象 | 根因 | 解决 | 如何预防 |
| --- | --- | --- | --- |
| 评估时报 `KeyError: 1` | `evaluate_model` 把已经是数字的 label 又拿去查 `label_map`（key 是中文） | 直接使用传入的数字标签，只对 `texts` 分词：`true_labels = labels` | 约定"分词只发生在文本上，标签走出参口就已映射完毕"，别在多个方法里重复做同一层转换 |
| 子查询检索结果里有大量重复文档 | 用对象内存地址去重，内容相同但对象不同 | 改成 `{doc.page_content: doc for doc in all_docs}` 按内容去重 | 去重 key 要选**业务上唯一**的东西（文本/ID），不要用 Python 对象身份 |
| 重排序耗时陡增、收益不明显 | 对未去重的子块直接重排，同一父块被打分多次 | 先回溯父块、按 `parent_content` 去重，再对父块重排 | 精排成本 = 候选数 × CrossEncoder 前向，**进精排前先降候选**是通用原则 |
| 重启服务后第一次查询很慢 | Milvus 集合未 load 或 embedding/reranker 模型冷启动 | 集合存在时显式 `client.load_collection(name)`；模型在服务启动时预热 | 上线前跑一次"热身查询"，把懒加载都触发掉 |
| 会话历史裁剪 SQL 报错 | `DELETE ... WHERE id NOT IN (SELECT ... FROM 同一张表)` | 子查询外包一层派生表 `AS sub` | 记住 MySQL 的"不能在子查询里引用正在被修改的表"限制 |
| 相似但问法不同的 FAQ 问答不上 | 纯 BM25 是词面匹配，"多少钱"对不上"退还押金" | 降到 0.85 阈值以下自动走 RAG 兜底；也可做 Query 改写扩展同义词 | 不要试图把 FAQ 阈值调低来"提高命中"，那会把错误答案放出去；兜底链路才是正解 |
| 回答里偶尔出现"根据文档"但没有文档 | Prompt 里写了"如果答案来源于检索到的文档请说明"，模型对空上下文也照说 | 通用知识路径显式传 `context=""`，并在 Prompt 中区分有无上下文 | Prompt 的分支语义要在代码层面**真实**成立，不能只靠模型自觉 |
| 敏感信息（API Key、库密码）进了 Git | 配置直接写死在 `config.py` 默认值里 | 改走 `.env` + `dotenv`，`config.ini` 只留非敏感项 | 默认值一律给"安全的假值"，真值只从环境变量来 |

## 6. 可复用经验

1. **"精确通道 + 语义通道"是所有企业问答系统的通用骨架。** FAQ/规则/词典命中就直接返回，命中不了才进 RAG。这既能守住准确率底线，又能把 LLM 调用量压到最低。阈值宁可高不可低：放出一个错答案的代价远大于多跑一次检索。
2. **检索用小块，生成用大块。** 这是 RAG 里性价比最高的一招：小块提升向量匹配精度，父块保证上下文完整。实现要点是"子块元数据里冗余父块全文"，一次检索拿到全部所需。
3. **混合检索的权重是有业务含义的。** 稀疏权重高 → 偏向术语/编号精确匹配；稠密权重高 → 偏向语义泛化。RAG 取 `(0.7, 1.0)` 是"语义为主、术语兜底"，如果你的场景有大量法条编号、合同编号、案号，就该反过来调。
4. **精排一定要放在召回之后、且召回要先去重。** 任何"重排/重打分/CrossEncoder"环节都应该在候选集最小化之后执行。
5. **LLM 做路由要给它降级方案。** `StrategySelector` 在 API 异常时返回"直接检索"，`QueryClassifier` 在模型缺失时返回"通用知识"——路由器的失败必须导致一个**安全且便宜**的默认行为，而不是抛异常。
6. **日志是 RAG 的可观测性。** 每个环节都记录"用了哪个策略、检索到几个块、最终选了几个、耗时多少"，线上问题才可复盘。RAG 用统一的 `logger` + 文件/控制台双 handler，值得照抄。
7. **评估要有基线。** 先跑一次 RAGAS 存 CSV，之后再改任何策略都对比同一份数据集，否则无法证明改动有效。

## 7. 面试问答

<details>
<summary><b>Q1：RAG 里为什么要做分层切分（父块/子块），直接固定 500 字切不行吗？</b></summary>

固定切分要在两个诉求之间做取舍：块小 → 向量语义集中、检索准，但丢上下文，LLM 容易断章取义；块大 → 上下文完整，但向量被稀释、检索不准，还挤占 token 预算。

分层切分把这两个诉求解耦：**用子块（300 字）做检索，用父块（1200 字）做生成**。工程上通过把 `parent_content` 冗余写进每个子块的元数据实现，检索命中子块后直接回溯父块，无需二次查库。代价是存储放大近一倍，但文档量级通常只有 MB，可忽略。

判断是否值得用：如果文档结构松散（如聊天记录、短评论），父子块差异不大，别硬上；如果是教材、手册、合同这类有明确小节层级的文档，收益非常明显。

</details>

<details>
<summary><b>Q2：你的混合检索权重是怎么定的？WeightedRanker(0.7, 1.0) 有什么依据？</b></summary>

WeightedRanker 的参数是"先稀疏后稠密"的权重，这里表示稀疏 0.7、稠密 1.0——**稠密是主力，稀疏是补丁**。

依据来自业务语料的构成：法律问答里大量是自然语言提问（"租房押金不退怎么办"），语义相似是主要匹配信号；而法条编号、案由名称、专业术语（"《劳动合同法》第八十二条""仲裁时效""工伤保险条例"）这类专有词，BM25 的精确词面匹配比稠密向量更可靠，尤其在稠密模型对生僻术语的表示不够好时。

实践中不是拍脑袋定的，而是**用 RAGAS 的 `context_recall` 做网格搜索**：固定稠密权重 1.0，稀疏权重从 0.3 扫到 1.0，看哪个点在评测集上召回率最高。如果业务里标识符更多（订单号、案号、合同编号），应该把稀疏权重调高甚至接近 1.0。

补充一点：Milvus 除 WeightedRanker 外还有 RRFRanker（倒数排序融合），RRF 不需要调权重、对分数量纲不敏感，如果两个召回通道的分数分布差异极大，RRF 往往更稳。

</details>

<details>
<summary><b>Q3：如果检索到的上下文不足以回答问题，你的系统怎么处理？</b></summary>

三层兜底：

1. **Prompt 层显式约定**：`rag_prompt` 里写明"如果无法回答，请回复：信息不足，无法回答，请联系人工客服，电话：{phone}"。模型有明确的退出通道，比让它自由发挥更可控。
2. **代码层判定**：检索结果为空（`context = ""`）时不再编造，日志里记"未检索到相关文档，上下文为空"，最终仍由 Prompt 兜底回复转人工。
3. **通道层兜底**：`IntegratedQASystem.query` 中若 `need_rag == False`（BI 阈值不够且明确不需要 RAG），直接返回"未找到答案"。

更成熟的做法还可以加一道**忠实度自检**：用 RAGAS 的 `faithfulness` 逻辑（把答案拆成 claim，逐条判断能否由上下文推出），低于阈值就换成人工兜底话术。这个自检的代价是一次额外的 LLM 调用，适合对准确率极其敏感的客服场景。

关键设计原则是：**系统必须有一条"承认自己不知道"的路径**，而且这条路要在 Prompt 和代码里同时存在，不能只靠模型自觉。

</details>

## 8. 延伸阅读

- LangChain 官方文档：Retrievers / Text Splitters / Document Loaders —— 本项目所有组件的抽象来源
- Milvus 官方文档：Multi-Vector Hybrid Search 与 WeightedRanker / RRFRanker
- BGE-M3 论文与 FlagEmbedding 仓库：dense + sparse + multi-vector 三合一的动机
- 本仓库同目录：[02-项目-法律咨询问答机器人](../02-对话与生成系统/02-项目-法律咨询问答机器人.md)、[05-项目-企业内部制度问答助手](05-项目-企业内部制度问答助手.md)
- RAGAS 官方文档与 GitHub：四个核心指标的实现细节与 Prompt 模板

---
[⬅️ 返回本目录索引](README.md)
