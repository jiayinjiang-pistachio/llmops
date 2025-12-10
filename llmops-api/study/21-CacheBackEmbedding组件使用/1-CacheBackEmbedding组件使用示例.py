#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/9 19:09
@Author         : jiayinkong@163.com
@File           : 1-CacheBackEmbedding组件使用示例.py
@Description    : 
"""
import os

import dotenv
import numpy as np
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain_openai import OpenAIEmbeddings
from numpy.linalg import norm

dotenv.load_dotenv()


def cosine_similarity(vec1: str, vec2: str) -> float:
    """计算余弦相似度"""
    # 1. 计算两个向量的点积
    dot_product = np.dot(vec1, vec2)

    # 2. 计算两个向量的长度
    vec1_norm = norm(vec1)
    vec2_norm = norm(vec2)

    # 3. 计算余弦相似度
    return dot_product / (vec1_norm * vec2_norm)


# 1. 创建文本嵌入模型
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.getenv("GPTSAPI_API_KEY"),
    openai_api_base=os.getenv("OPENAI_API_BASE")
)
embeddings_with_cache = CacheBackedEmbeddings.from_bytes_store(
    embeddings,
    LocalFileStore("./cache/"),
    namespace=embeddings.model,
    query_embedding_cache=True,
)

# 2. 嵌入文本
query_vector = embeddings_with_cache.embed_query("我是慕小课，我喜欢打篮球")
print(query_vector)
print(len(query_vector))

print("=" * 20)

# 3. 嵌入文档列表/字符串列表
document_vector = embeddings_with_cache.embed_documents([
    "我叫幕小课，我喜欢打篮球",
    "这个喜欢打篮球的人叫幕小课",
    "求知若渴，虚心若愚"
])

print(len(document_vector))

# 4. 计算余弦相似度
print("向量1和向量2的相似度：", cosine_similarity(document_vector[0], document_vector[1]))
print("向量1和向量3的相似度：", cosine_similarity(document_vector[0], document_vector[2]))
