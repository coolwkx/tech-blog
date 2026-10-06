---
article_id: kp-9a983c15d2398231
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-8b0a9bea9dde
learning_sourceId: 8b0a9bea9dde
learning_order: 9
learning_objective: 理解并验证：领域预处理流水线（自包含）
---

# 领域预处理流水线（自包含）

> **学习目标**：能够解释「领域预处理流水线（自包含）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇 TF-IDF、第 05 篇文本分类流水线与评估指标、第 09 篇 BERT 微调、第 11 篇情感分析项目的工程范式。
>
> **所属主题**：NLP 项目实战：医疗文本分类 · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install jieba pandas numpy
import re
import numpy as np
import pandas as pd
import jieba

# 加载医学自定义词典（实际项目从文件加载）
for term in ["肾结石", "输尿管", "心肌梗死", "出血性脑梗死", "肢端纤维角化瘤"]:
    jieba.add_word(term)

    # 通用停用词表
    STOPWORDS = set("的 了 在 是 我 有 和 就 都 也 很 只 要 一个 上 到 说".split())
    # 关键修正：疑问词必须保留！它们是判断意图的核心信号
    QUESTION_WORDS = {"什么", "怎么", "如何", "为啥", "咋", "为什么", "哪", "多久", "多少"}

    class MedicalTextPreprocessor:
        def __init__(self, stopwords=None, keep_english=True):
            self.stopwords = set(stopwords) if stopwords else STOPWORDS
            self.keep_english = keep_english

            def clean_text(self, text):
                if not isinstance(text, str):
                    return ""
                if self.keep_english:
                    # 保留中文 + 英文 + 数字（避免丢掉 CT / MRI / B超 等关键缩写）
                    text = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', ' ', text)
                else:
                    text = re.sub(r'[^\u4e00-\u9fa5]', ' ', text)
                    return re.sub(r'\s+', ' ', text).strip()

                def remove_stopwords(self, words):
                    return [w for w in words
                if w.strip() and (w in QUESTION_WORDS or w not in self.stopwords)]

                def preprocess(self, text):
                    cleaned = self.clean_text(text)
                    segmented = jieba.lcut(cleaned)
                    filtered = self.remove_stopwords(segmented)
                    return ' '.join(filtered)

                def preprocess_dataframe(self, df, text_column='text'):
                    df = df.copy
                    df['cleaned_text'] = [self.preprocess(t) for t in df[text_column]]
                    lengths = [len(t.split()) for t in df['cleaned_text'] if t]
                    if lengths:
                        print("预处理完成，平均长度 {:.1f} 个词，最长 {}，最短 {}".format(
                        float(np.mean(lengths)), max(lengths), min(lengths)))
                        return df

                    if __name__ == "__main__":
                        pre = MedicalTextPreprocessor

                        samples = [
                        "肾结石，输尿管结石一般用什么药呢？而且效果较好！123",
                        "请问出血性脑梗死症状是什么",
                        "睡一觉醒睡不着咋搞的？现在怀孕7个月了",
                        "距骨骨折脱位做啥检查，需要做CT吗",
                        "肢端纤维角化瘤应该看啥医生",
                        ]
                        for s in samples:
                            print(f"原文: {s}")
                            print(f"清洗: {pre.clean_text(s)}")
                            print(f"最终: {pre.preprocess(s)}\n")

                            df = pd.DataFrame({"text": samples, "label_class": ["治疗方法", "临床表现", "病因", "化验/体检方案", "所属科室"]})
                            df = pre.preprocess_dataframe(df)
                            print(df[["cleaned_text", "label_class"]].to_string(index=False))
```

注意输出中「CT」被保留、疑问词「什么 / 咋 / 多久」也被保留——这两点正是对原始实现的两处修正。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/12-NLP项目实战-医疗文本分类.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「领域预处理流水线（自包含）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/12-NLP项目实战-医疗文本分类.md)
