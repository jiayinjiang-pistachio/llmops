#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/9 19:38
@Author         : jiayinkong@163.com
@File           : 1-HuggingFace本地嵌入模型.py
@Description    : 
"""
import os

from langchain_huggingface import HuggingFaceEmbeddings

# from langchain_community.embeddings import HuggingFaceEmbeddings

# 禁用 hf_transfer，使用普通下载方式
os.environ['HF_HUB_ENABLE_HF_TRANSFER'] = '0'

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-albert-small-v2",  # 非常小的模型
    cache_folder="./embeddings"
)

# 测试
text = "Hello, world!"
vector = embeddings.embed_query(text)
print(f"向量长度: {len(vector)}")
