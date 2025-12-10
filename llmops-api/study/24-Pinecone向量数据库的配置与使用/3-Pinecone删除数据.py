#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/10 15:04
@Author         : jiayinkong@163.com
@File           : 3-Pinecone删除数据.py
@Description    : 
"""
import os

import dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

dotenv.load_dotenv()
embedding = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.getenv("GPTSAPI_API_KEY"),
    openai_api_base=os.getenv("OPENAI_API_BASE")
)

id = "5e111420-54f8-45f8-9ad8-5478028ab5f1"
db = PineconeVectorStore(
    index_name="llmops",
    embedding=embedding,
    namespace="dataset",
)
db.delete([id], namespace="dataset")
