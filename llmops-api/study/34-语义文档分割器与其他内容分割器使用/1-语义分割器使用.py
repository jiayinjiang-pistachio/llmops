#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/12 20:51
@Author         : jiayinkong@163.com
@File           : 1-语义分割器使用.py
@Description    : 
"""
import os
import warnings

# 忽略所有警告
warnings.filterwarnings('ignore')

# 设置环境变量禁用 simsimd
os.environ["USE_SIMSIMD"] = "0"


# 直接复制原函数并修改
def fixed_calculate_cosine_distances(sentences):
    """修复的 calculate_cosine_distances 函数"""
    import numpy as np

    distances = []
    for i in range(len(sentences) - 1):
        # 这里 sentences 应该是 (text, embedding) 元组列表
        # 但根据错误，可能已经是纯文本列表了
        # 让我们安全地处理

        if isinstance(sentences[i], tuple) and len(sentences[i]) >= 2:
            # 如果是元组，提取嵌入
            embedding_current = sentences[i][1]
            embedding_next = sentences[i + 1][1]
        elif hasattr(sentences[i], 'embedding'):
            # 如果有 embedding 属性
            embedding_current = sentences[i].embedding
            embedding_next = sentences[i + 1].embedding
        else:
            # 如果已经是嵌入向量
            embedding_current = sentences[i]
            embedding_next = sentences[i + 1]

        # 确保是 numpy 数组
        embedding_current = np.array(embedding_current, dtype=np.float32).reshape(1, -1)
        embedding_next = np.array(embedding_next, dtype=np.float32).reshape(1, -1)

        # 计算余弦距离（不使用有问题的 cosine_similarity）
        # 直接计算余弦距离: 1 - (A·B)/(||A||·||B||)
        dot_product = np.dot(embedding_current, embedding_next.T)[0][0]
        norm_current = np.linalg.norm(embedding_current)
        norm_next = np.linalg.norm(embedding_next)

        if norm_current == 0 or norm_next == 0:
            similarity = 0
        else:
            similarity = dot_product / (norm_current * norm_next)

        distance = 1 - similarity
        distances.append(distance)

    distances = np.array(distances)

    # 提取文本部分
    if isinstance(sentences[0], tuple):
        sentences_text = [s[0] for s in sentences]
    else:
        # 假设 sentences 已经是纯文本列表
        sentences_text = sentences

    return distances, sentences_text


# 现在导入 langchain 相关模块
import dotenv
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

# 替换原函数
import langchain_experimental.text_splitter as experimental_splitter

experimental_splitter.calculate_cosine_distances = fixed_calculate_cosine_distances

dotenv.load_dotenv()

# 1. 构建加载器与文本分割器
loader = UnstructuredFileLoader("./科幻短篇.txt")
text_spliter = SemanticChunker(
    embeddings=OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("GPTSAPI_API_KEY"),
        openai_api_base=os.getenv("OPENAI_API_BASE")
    ),
    number_of_chunks=10,
    add_start_index=True,
    sentence_split_regex=r"(?<=[。？！.?!])",
)

# 2. 加载文本与分割
documents = loader.load()
chunks = text_spliter.split_documents(documents)

# 3. 循环打印
for chunk in chunks:
    print(f"块大小: {len(chunk.page_content)}, 元数据: {chunk.metadata}")
