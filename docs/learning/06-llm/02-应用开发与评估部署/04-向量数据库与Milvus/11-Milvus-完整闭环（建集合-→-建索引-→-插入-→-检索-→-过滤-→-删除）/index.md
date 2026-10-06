---
article_id: kp-11576cf3a134ca0b
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-d0c337577532
learning_sourceId: d0c337577532
learning_order: 10
learning_objective: 理解并验证：Milvus 完整闭环（建集合 → 建索引 → 插入 → 检索 → 过滤 → 删除）
---

# Milvus 完整闭环（建集合 → 建索引 → 插入 → 检索 → 过滤 → 删除）

> **学习目标**：能够解释「Milvus 完整闭环（建集合 → 建索引 → 插入 → 检索 → 过滤 → 删除）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 基础、embedding 与余弦相似度的直觉、关系型数据库基本概念（库/表/行/列/主键）。
>
> **所属主题**：-向量数据库与Milvus · 可运行示例

## 本次只学这一点

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

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/07-检索增强RAG/07-向量数据库与Milvus.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Milvus 完整闭环（建集合 → 建索引 → 插入 → 检索 → 过滤 → 删除）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/07-检索增强RAG/07-向量数据库与Milvus.md)
