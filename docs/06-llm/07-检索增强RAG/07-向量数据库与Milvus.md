> **一句话总结**：向量数据库把「非结构化数据 → 嵌入向量 → 近似最近邻检索」这条链路工程化，Milvus 用 Collection/Field/Schema 这套类关系数据库的概念承载向量与标量字段，并通过不同索引类型（FLAT / IVF / HNSW / PQ）在精度、速度与内存之间做取舍。
> **前置知识**：Python 基础、embedding 与余弦相似度的直觉、关系型数据库基本概念（库/表/行/列/主键）。
> **学完能做到**：1. 说清向量数据库与关系型数据库的差异，并完成 Milvus 的建表、插入、索引、检索、标量过滤、删除闭环；2. 根据数据规模与精度要求选择合适的索引类型与 nlist/nprobe 参数；3. 用稠密 + 稀疏双向量做混合检索与重排序，并用 Redis 缓存查询结果。

## 1. 核心概念

### 1.1 从非结构化数据到向量

| 概念 | 说明 |
|---|---|
| 非结构化数据 | 图像、视频、音频和自然语言等信息，不遵循预定义的组织方式；这类数据占世界数据约 **80%** |
| 嵌入向量（embedding） | 对非结构化数据的**特征抽象**，数学上是浮点数或二进制数的数组；现代嵌入技术用于把非结构化数据转成向量 |
| 向量相似度搜索 | 将查询向量与库中向量比较，找出最相似的向量；若两个嵌入向量非常相似，则**原始数据源也很相似** |
| 近似最近邻（ANNS） | 用近似算法加速搜索过程，以少量精度损失换取巨大的速度提升 |

**为什么需要专门的数据库**：传统关系型数据库主要处理**遵循预定义模式的结构化数据**；
Milvus 从底层设计用于处理从非结构化数据转换而来的嵌入向量，能处理**万亿级别**的向量索引。

### 1.2 Milvus 与关系型数据库的概念映射

| Milvus | 关系数据库 | 描述 |
|---|---|---|
| Collection | 表（Table） | 集合，相当于关系数据库中的表，用于组织数据 |
| Field | 列（Column） | 字段，Field Schema 相当于表中的列 |
| Entity | 行（Row） | 实体，Collection 中共享同一 Schema 的数据记录 |
| Primary Key | 主键 | 在 Field Schema 中标记 `is_primary` |
| Partition | （无直接对应） | 分区，用于把数据切成子集以加速检索 |
| Database | 数据库 | 一个 Milvus 集群最多支持 **64 个数据库**，可为用户分配权限管理集合 |

### 1.4 部署形态

| 形态 | 连接方式 | 适用场景 |
|---|---|---|
| Milvus Lite | `MilvusClient(uri="milvus_demo.db")` | 本地开发、单机小数据量（随 `pymilvus` 一起安装） |
| Standalone | `MilvusClient(uri="http://localhost:19530")` | 单机服务，需先启动 Milvus 后台服务 |
| 分布式（Docker/K8s） | 连接集群地址 | 生产环境大规模数据 |

**关键区分**：`uri` 是**文件路径**则代表本地数据库文件；`uri` 是**链接地址**则代表 Milvus 服务，
需要先开启 Milvus 后台服务。

## 2. 关键机制

### 2.1 Field Schema 与 Collection Schema 的可配置项

**Field Schema（字段的逻辑定义）**：

| 属性 | 类型 | 说明 |
|---|---|---|
| `name` | String（必填） | 要创建的集合中的字段名称 |
| `dtype` | 必填 | 字段的数据类型，如 `INT64`、`VARCHAR`、`FLOAT_VECTOR`、`SPARSE_FLOAT_VECTOR` |
| `is_primary` | Boolean | 是否为主键字段（**一个集合仅支持一个主键字段**） |
| `auto_id` | Boolean | 主键字段必填，是否启用自动 ID |
| `max_length` | Integer | `VARCHAR` 字段允许插入的最大长度，范围 `[1, 65535]` |
| `dim` | Integer | 向量维度，范围 `[1, 32768]` |
| `is_partition_key` | Boolean | 该字段是否为分区键 |
| `description` | String | 字段描述（选填） |

**Collection Schema（集合的逻辑定义）**：

| 属性 | 类型 | 说明 |
|---|---|---|
| `field` | 必填 | 集合中要创建的字段 |
| `description` | String | 集合描述（选填） |
| `partition_key_field` | String | 设计用作分区键的字段名（选填） |
| `enable_dynamic_field` | Boolean | 是否启用动态模式 |

**两个重要限制**：① 一个 Collection **最多支持 4 个向量 Field**；
② 定义 Schema 前必须先定义 Field Schema。

**动态字段（`enable_dynamic_field=True`）**：允许插入未定义的字段，这些字段以 JSON 格式存储在名为
`$meta` 的特殊字段中。注意它只对**创建时开启该选项的集合**生效。

### 2.2 相似度度量怎么选

| 度量 | 直觉 | 是否需归一化 | 值的含义 | 适用场景 |
|---|---|---|---|---|
| L2（欧几里得距离） | 直线距离，越小越相似 | 否 | 距离，越小越好 | 图像特征、未归一化的向量 |
| IP（内积） | 方向与模长共同决定 | 否 | 相似度，越大越相似 | 向量已归一化时等价于余弦 |
| COSINE（余弦相似度） | 只看夹角方向 | 不需要（内部归一化） | 相似度，越大越相似 | 文本嵌入（最常用） |

要点：**度量方式必须在建索引时与搜索时一致**。对浮点嵌入，通常使用以上三种；
强调「根据输入数据的形式，选择特定的相似度度量方法可以获得最优的性能」。

### 2.3 索引类型对比

| 索引 | 原理 | 精度 | 速度 | 内存 | 适用场景 |
|---|---|---|---|---|---|
| FLAT | 暴力搜索（brute-force），无近似 | 完全精确 | 慢 | 大 | 小型、百万级数据集，要求完全准确 |
| IVF_FLAT | 聚类（如 k-means）分簇 + 簇内倒排索引，查询只看 `nprobe` 个最近簇 | 高（可调） | 快 | 中 | 大规模数据集上平衡精度与速度 |
| IVF_SQ8 | 在 IVF_FLAT 基础上加**标量量化**：把每个维度 4 字节浮点压成 1 字节整数 | 较高 | 快 | 显著减小 | 内存受限但仍要较高精度 |
| IVF_PQ | 倒排索引 + **乘积量化**：簇内向量再切子向量分别量化编码 | 中（有损） | 很快 | 很小 | 大规模高维数据，存储与速度优先 |
| HNSW | 基于图的索引 | 高 | 很快 | 大（需存图） | 对搜索效率有高要求的场景 |

**默认行为**：索引是数据的组织单位，**在搜索或查询插入的实体之前，必须声明索引类型和相似度度量**；
如果未指定索引类型，Milvus 默认使用暴力搜索。

**IVF 的工作机制（三步）**：

1. **聚类**：用聚类算法把高维空间划分为多个子空间（簇），每簇有一个代表向量（通常是簇中心）；
2. **倒排索引**：每个向量映射到它所属的簇，查询时只需关注与查询向量相似的簇；
3. **查询处理**：只搜索候选簇而不搜索整个高维空间，从而显著降低时间复杂度。

### 2.4 nlist / nprobe / 图参数：精度与速度的旋钮

| 参数 | 含义 | 调大 | 调小 |
|---|---|---|---|
| `nlist`（建索引时） | 划分的簇数量 | 簇更细，单簇数据更少，召回可能提升但索引开销增大 | 簇更粗，搜索范围更大 |
| `nprobe`（查询时） | 访问的簇数量 | 搜索更多簇，返回更多候选，**精确度提高但查询时间增加** | 搜索范围缩小，**速度更快但可能牺牲精度** |
| `ef`（HNSW 查询时） | 候选队列大小 | 召回提升、延迟增加 | 更快、召回下降 |
| `M` / `efConstruction`（HNSW 建索引） | 图的连接度 | 图更密、召回更好、内存与建索引时间增加 | 更省内存 |

**工程直觉**：`nprobe/nlist` 越小越快，越大越准。调参流程是——先在测试集上固定 `nlist`，
逐步提高 `nprobe` 观察召回率与延迟曲线，在可接受的延迟预算内取召回最高点。

### 2.5 标量过滤与混合搜索

**过滤搜索（filter search）**：把标量筛选器应用到向量搜索上，允许根据特定条件优化结果。
例如筛选颜色以红色为前缀的结果：`filter='color like "red%"'`——`like` 运算符支持前缀、中缀、后缀匹配。

**多向量搜索（hybrid_search）**：用 `hybrid_search` 在一次调用中执行多个 ANN 搜索请求，
每个 `AnnSearchRequest` 代表特定向量场上的单个搜索请求（注意与「批量向量搜索」不同：
批量搜索是同一字段多个查询向量，多向量搜索是**多个字段各一个查询**）。
合并多路结果需要**重排序策略**：

| 策略 | 公式/思路 | 适用 |
|---|---|---|
| WeightedRanker | 对每路结果加权，权重范围 `[0,1]`，越接近 1 越重要 | **需要强调某个向量场**时（如多模态中"文字描述比颜色更重要"） |
| RRFRanker（倒数排序融合） | 按结果在各检索列表中的排名位置计分：$score(d)=\sum_{i=1}^{N}\frac{1}{k+rank_i(d)}$ | **没有特定侧重**时的推荐默认，能有效平衡各向量场的重要性 |

RRF 参数说明：$N$ 为检索路径数，$d$ 为文档，$rank_i(d)$ 为文档 $d$ 在第 $i$ 个检索器中的排名（从 0 开始计数），
$k$ 是平滑参数（控制分数随排名增加的下降速度，**默认通常取 60**）。

### 2.7 RAG 项目中的向量存储设计（BGE-M3 + 双向量）

 RAG 项目的 `vector_store.py` 是一个完整的生产级范式，值得单独记住其 Schema 设计：

| 字段 | 类型 | 作用 |
|---|---|---|
| `id` | VARCHAR(100)，主键 | 文本块唯一标识 |
| `text` | VARCHAR(65535) | 文本块原文（检索后送给 LLM 的内容） |
| `dense_vector` | FLOAT_VECTOR | BGE-M3 生成的稠密向量，索引 `IVF_FLAT`，度量 IP |
| `sparse_vector` | SPARSE_FLOAT_VECTOR | BGE-M3 生成的稀疏向量（类似学习到的 BM25 权重），索引 `SPARSE_INVERTED_INDEX`，度量 IP |
| `parent_id` | VARCHAR(100) | 所属父块 ID，支持「小块检索、大块返回」 |
| `parent_content` | VARCHAR(65535) | 父块原文，扩大上下文 |
| `source` | VARCHAR(50) | 来源文件 |
| `timestamp` | VARCHAR(50) | 时间戳 |

### 2.8 Redis 在系统中的角色

Redis（Remote Dictionary Server）是**高性能的键值对数据库**，常用于缓存与会话管理。
核心特性：高性能（数据在内存中，读写极快）、持久化（RDB 与 AOF）、灵活性（多种数据结构与丰富命令）、简单易用。

| 应用场景 | 在 RAG/问答系统中的具体用法 |
|---|---|
| 缓存查询结果 | 以 `answer:{query}` 为 key 缓存问答结果，命中即返回，**省掉一次向量检索 + LLM 生成** |
| 存储用户会话 | 多轮对话历史 |
| 排行榜/计数器 | 热门问题统计、限流计数 |

**为什么 RAG 系统要加 Redis**：一次 RAG 问答的耗时主要在两段——向量检索与 LLM 生成（数百毫秒到数秒）。
对重复问题直接命中缓存，可以把响应降到毫秒级，同时显著降低 LLM 调用成本。
明确的设计是 `get_answer(query)` 先查 `f"answer:{query}"`，未命中再走完整 RAG 流程。

## 3. 可运行示例

### 3.1 Milvus 完整闭环（建集合 → 建索引 → 插入 → 检索 → 过滤 → 删除）

```python
# 依赖：pip install pymilvus
# 本地文件模式（Milvus Lite）无需启动服务；改成 MilvusClient(uri="http://localhost:19530") 即连服务端
from pymilvus import MilvusClient, DataType

client = MilvusClient(uri="milvus_demo.db")
COLLECTION = "demo_v1"

# ---------- 1. 建集合：先定义 Schema ----------
if client.has_collection(COLLECTION):
    client.drop_collection(COLLECTION)

    schema = client.create_schema(auto_id=False, enable_dynamic_field=True)
    schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
    schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=5)
    schema.add_field(field_name="scalar1", datatype=DataType.VARCHAR, max_length=256,
    description="标量字段")

    # ---------- 2. 建索引 ----------
    index_params = client.prepare_index_params()
    index_params.add_index(field_name="vector", index_name="vector_index",
    index_type="IVF_FLAT", metric_type="COSINE",
    params={"nlist": 128})
    # 标量字段的默认索引通常为 INVERTED，用于加速 filter
    index_params.add_index(field_name="scalar1", index_name="scalar_index", index_type="INVERTED")

    client.create_collection(collection_name=COLLECTION, schema=schema, index_params=index_params)
    print("索引列表:", client.list_indexes(collection_name=COLLECTION))
    print("索引详情:", client.describe_index(collection_name=COLLECTION, index_name="vector_index"))

    # ---------- 3. 插入实体（动态字段 color 会自动进 $meta）----------
    data = [
    {"id": 0, "vector": [0.358, -0.602, 0.184, -0.263, 0.903], "color": "pink_8682", "scalar1": "a"},
    {"id": 1, "vector": [0.199, 0.060, 0.698, 0.261, 0.839], "color": "red_7025", "scalar1": "b"},
    {"id": 2, "vector": [0.437, -0.560, 0.646, -0.326, 0.326], "color": "brown_7231", "scalar1": "c"},
    {"id": 3, "vector": [0.317, 0.972, -0.370, -0.486, 0.958], "color": "orange_6781", "scalar1": "d"},
    ]
    print("插入:", client.insert(collection_name=COLLECTION, data=data))
    # upsert：主键已存在则覆盖，不存在则插入（数据级操作）
    # client.upsert(collection_name=COLLECTION, data=data)

    # ---------- 4. 向量检索 ----------
    res = client.search(
    collection_name=COLLECTION,
    data=[[0.358, -0.602, 0.184, -0.263, 0.903]],
    limit=2,
    search_params={"metric_type": "COSINE", "params": {"nprobe": 10}},
    output_fields=["id", "color"], # 指定返回哪些属性
    )
    for hits in res:
        for hit in hits:
            print(f" id={hit['id']} distance={hit['distance']:.4f} color={hit['entity']['color']}")

            # ---------- 5. 带标量过滤的检索 ----------
            res = client.search(
            collection_name=COLLECTION,
            data=[[0.358, -0.602, 0.184, -0.263, 0.903]],
            limit=5,
            search_params={"metric_type": "COSINE", "params": {}},
            filter='color like "red%"', # 只看红色的记录
            output_fields=["color"],
            )
            print("过滤检索命中数:", len(res[0]))

            # ---------- 6. 标量查询（不走向量检索）----------
            print("条件查询:", client.query(collection_name=COLLECTION, filter="id in [0, 1]",
            output_fields=["id", "color"]))

            # ---------- 7. 删除 ----------
            print("按过滤器删除:", client.delete(collection_name=COLLECTION, filter="id in [2, 3]"))
            print("剩余:", client.query(collection_name=COLLECTION, filter="id >= 0", output_fields=["id"]))
```

## 4. 常见坑

| 坑 | 现象 | 原因 | 正确做法 |
|---|---|---|---|
| 建索引与搜索用不同 metric | 检索结果异常或直接报错 | 度量必须一致 | 索引与 `search_params` 的 `metric_type` 保持一致 |
| 未建索引就搜索 | 退化为暴力搜索、速度很慢 | 未指定索引时 Milvus 默认暴力搜索 | 显式 `create_index` 后再 `load_collection` |
| 数据插入后立刻搜不到 | 返回空结果 | 集合未加载到内存 | 搜索前 `load_collection`，或用 `get_load_state` 检查 |
| 把 `nlist` 当查询参数 | 无效或报错 | `nlist` 是**建索引**参数，`nprobe` 是**查询**参数 | 分别在 `add_index(params=...)` 与 `search_params.params` 中设置 |
| `nprobe` 设得过大 | 延迟飙升 | 访问簇数过多，接近暴力搜索 | 按延迟预算调参，一般取 `nlist` 的 1%~10% 起调 |
| 稀疏向量字段写了 `dim` | 建表报错 | 稀疏向量维度由数据决定 | `SPARSE_FLOAT_VECTOR` 不加 `dim` |
| 主键重复插入 | 数据异常或覆盖 | 未用 `auto_id` 或未控制主键 | 明确策略：要覆盖用 `upsert`，要唯一用 `auto_id=True` |
| 忘记一个集合只能有 1 个主键 | 建表失败 | Schema 限制 | 只标记一个 `is_primary=True` |
| 向量字段超过 4 个 | 建表失败 | Collection 最多 4 个向量 Field | 拆分集合或减少向量字段（如用多向量融合降低字段数） |
| `VARCHAR` 内容超长 | 插入报错 | `max_length` 上限 65535 | 截断文本块，或改用更大的 `max_length`（不超上限） |
| `like` 过滤语法写错 | 过滤不生效 | 语法与 SQL 有差异 | 用 `like "red%"` 形式，注意引号与通配符位置 |
| 混合检索结果顺序不符合预期 | 某一路结果被淹没 | 默认权重/排名融合不合场景 | 明确侧重时用 `WeightedRanker`，否则用 `RRFRanker` 并调 `k` |
| 把多向量搜索当批量搜索 | 结果数量对不上 | `hybrid_search` 是**多字段多路**，批量是**同字段多向量** | 按语义区分两个 API |
| Milvus Lite 与 Standalone 混用 | 换环境后数据"消失" | 数据分别在本地文件与服务端 | 明确 `uri` 语义：路径=本地文件，地址=服务端 |
| Redis 缓存不设过期 | 内存持续增长、答案过时 | 未设置 TTL | `set(..., ex=秒数)`，并对知识更新场景主动失效缓存 |
| Redis 存复杂对象不序列化 | 取出来是字符串或报错 | redis 只存字节/字符串 | 用 `json.dumps/loads` 序列化，并配 `decode_responses=True` |

## 5. 面试问答

**Q1：向量数据库和关系型数据库的本质区别是什么？Milvus 里有哪些概念与 MySQL 对应？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

本质区别在**数据形态与检索方式**：关系型数据库处理遵循预定义模式的结构化数据，靠精确匹配（`WHERE` 等值/范围条件）检索；
向量数据库处理由非结构化数据（图像、音视频、自然语言）经嵌入模型转换来的**嵌入向量**，
靠**相似度计算 + 近似最近邻（ANNS）**检索，输出的是「最相似的 Top-K」而非「精确命中的集合」。
为保证可用性，向量库通常还必须支持标量过滤（把结构化条件与向量检索组合成混合搜索）。

Milvus 与关系数据库的概念对应：

| Milvus | 关系数据库 |
|---|---|
| Collection | 表 |
| Field | 列 |
| Entity | 行 |
| Primary Key | 主键 |
| Database | 数据库（一个集群最多 64 个） |

多出来的概念是 **Partition（分区）**——关系库里没有直接对应物，它用于把集合切分成子集以缩小搜索范围。

</details>

**Q2：FLAT、IVF_FLAT、IVF_SQ8、IVF_PQ、HNSW 怎么选？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

按「精度优先 → 速度/内存优先」排序选择：

| 索引 | 取舍 | 选择依据 |
|---|---|---|
| FLAT | 精确但慢、内存大 | 小型或百万级数据集，要求完全精确结果 |
| IVF_FLAT | 精度可调、速度较快 | 大规模数据集的默认平衡选择 |
| IVF_SQ8 | 精度略降、内存显著减小 | 内存受限（标量量化把 4 字节浮点压成 1 字节） |
| IVF_PQ | 精度有损、内存最小、速度很快 | 超大规模高维数据，存储与吞吐优先 |
| HNSW | 精度高、速度快、内存较大 | 对搜索效率有高要求的场景 |

决策顺序：先看**数据规模**（小于百万级直接用 FLAT），再看**内存预算**（紧张就上量化 PQ/SQ8），
最后看**延迟要求**（苛刻就 HNSW）。选定后通过 `nprobe`/`ef` 在召回与延迟之间微调。

</details>

**Q3：混合检索为什么要重排序？WeightedRanker 与 RRFRanker 怎么选？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

因为稠密向量擅长语义相似、稀疏向量擅长关键词精确匹配，两路检索各自会返回一批候选，
但**两路的分数不可直接比较**（量纲与分布不同），无法简单相加。因此需要一个重排序策略把多路结果融合成一个统一排序。

- **WeightedRanker**：给每个向量场分配权重（范围 `[0,1]`，越接近 1 越重要）。
 当**明确知道哪个字段更重要**时使用——例如多模态检索中「图片的文字描述比颜色更重要」，
 或 RAG 中的 `WeightedRanker(0.7, 1.0)` 表示更信任稠密语义匹配。
- **RRFRanker（倒数排序融合）**：不用分数，只用**排名**，按 $1/(k+rank_i(d))$ 累加计分，
 $k$ 为平滑参数（默认 60，越大则靠前排名之间的差距被压缩得越平缓）。

选择原则：**没有特定侧重时用 RRFRanker**（明确推荐），因为它天然平衡各路的贡献，
且对分数尺度不敏感、更鲁棒；需要突出某一路时才用 WeightedRanker。

</details>

## 6. 自测题

**1. 写出 Milvus 中 Field Schema 至少 5 个可配置属性及其含义。**

<details markdown="1">
<summary markdown="1">参考答案</summary>

- `name`（String，必填）：字段名称；
- `dtype`（必填）：数据类型，如 INT64 / VARCHAR / FLOAT_VECTOR / SPARSE_FLOAT_VECTOR；
- `is_primary`（Boolean）：是否为主键（一个集合只能有一个主键）；
- `auto_id`（Boolean，主键必填）：是否启用自动递增 ID；
- `max_length`（Integer）：VARCHAR 字段允许的最大长度，范围 `[1, 65535]`；
- `dim`（Integer）：向量维度，范围 `[1, 32768]`；
- `is_partition_key`（Boolean）：是否作为分区键；`description`（String，选填）：字段描述。

</details>

**2. IVF_FLAT 的三步工作机制是什么？`nlist` 和 `nprobe` 分别在哪一步起作用？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

① **聚类**：用 k-means 之类的算法把高维空间划分为多个子空间（簇），每簇有一个代表向量（簇中心），
这一步由 `nlist`（簇数量）控制；
② **倒排索引**：为每个簇建立倒排索引，把每个向量映射到它所属的簇；
③ **查询处理**：查询向量先被分配到最近的簇中心，然后只在该簇内做精确的线性搜索。

`nprobe` 在查询阶段起作用，控制搜索时考察的簇数量：增大则搜索更多簇、精度提高但耗时增加；
减小则更快但可能牺牲精度。

</details>

**3. 用 Milvus 做一个「子块检索、父块返回」的设计，Schema 该怎么写？为什么这样做？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

Schema（参考 RAG 的 `vector_store.py`）至少包含：

```python
schema.add_field(field_name="id", datatype=DataType.VARCHAR, is_primary=True, max_length=100)
schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)
schema.add_field(field_name="dense_vector", datatype=DataType.FLOAT_VECTOR, dim=dense_dim)
schema.add_field(field_name="sparse_vector", datatype=DataType.SPARSE_FLOAT_VECTOR)
schema.add_field(field_name="parent_id", datatype=DataType.VARCHAR, max_length=100)
schema.add_field(field_name="parent_content", datatype=DataType.VARCHAR, max_length=65535)
```

`id/text/dense_vector/sparse_vector` 用于**小块的检索**（小块语义聚焦、向量表示更准），
`parent_id/parent_content` 记录它属于哪个大块；检索命中后按 `parent_id` 返回父块原文交给 LLM。

原因：切片粒度存在两难——切得太细，单块语义清晰但上下文被割裂，LLM 回答缺依据；
切得太粗，上下文完整但向量会把多个主题平均掉，检索精度下降。
「子块检索 + 父块返回」同时拿到两者的好处。

</details>

**4. RAG 系统里为什么要引入 Redis？缓存 key 怎么设计？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

引入 Redis 的目的是**缓存问答结果**：一次完整 RAG 问答要经过「向量检索 + 大模型生成」，
耗时从数百毫秒到数秒不等，而重复问题在实际业务中占比很高。把结果缓存后，命中即返回，可把响应降到毫秒级，
同时显著降低 LLM 调用成本。Redis 还能顺带承担会话历史、热门问题计数等职责。

缓存 key 设计：采用 `answer:{query}` 的形式（原问题直接入 key）。
工程上建议：① 对 query 做归一化（去空格、统一大小写）以避免同一问题不同写法漏命中；
② 对超长 query 取哈希（如 `answer:{sha1(query)}`）避免 key 过长；
③ 设置 TTL（`set(..., ex=...)`），并在知识库更新时主动失效（可按来源打标签批量删除）；
④ 把命中的答案与引用来源一起缓存，保证可追溯。

</details>

## 7. 延伸阅读

- [Milvus 官方文档](https://milvus.io/docs)
- [Redis 官方文档](https://redis.io/docs/latest/)
- [MySQL 官方文档](https://dev.mysql.com/doc/)
- [LangChain 官方文档](https://python.langchain.com/docs/introduction/)

---

[⬅️ 返回本目录索引](README.md)
