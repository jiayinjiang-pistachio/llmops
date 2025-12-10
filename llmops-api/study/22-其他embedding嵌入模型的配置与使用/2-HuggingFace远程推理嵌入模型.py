#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/9 21:40
@Author         : jiayinkong@163.com
@File           : 2-HuggingFace远程推理嵌入模型.py
@Description    : 
"""
import os

import dotenv
from langchain_huggingface import HuggingFaceEndpointEmbeddings

dotenv.load_dotenv()

# 需要设置 HuggingFace API 令牌
HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

model = "sentence-transformers/all-mpnet-base-v2"
embeddings = HuggingFaceEndpointEmbeddings(
    model=model,
    task="feature-extraction",
    huggingfacehub_api_token=HF_TOKEN,
)

# 测试
text = "Hello, world!!"
vector = embeddings.embed_query(text)
print(f"✅ 向量长度: {len(vector)}")
print(f"向量示例: {vector[:5]}")
