#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/14 19:21
@Author         : jiayinkong@163.com
@File           : 1-Multi-Query多查询策略.py
@Description    : 
"""
import os

import dotenv
import weaviate
from langchain.retrievers import MultiQueryRetriever
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey

dotenv.load_dotenv()

# 创建连接客户端
client = weaviate.connect_to_weaviate_cloud(
    cluster_url="leskh5srpsgusmg0hyiyg.c0.asia-southeast1.gcp.weaviate.cloud",
    auth_credentials=AuthApiKey(
        "TUcxREMvQ2VENG1TSEtUL19JaDh6OXVyVG9uZVRoTzJXUnUwc2l2b0w5bVpzcnRRREF3blZXWEJCRHR3PV92MjAw"),
    skip_init_checks=True,  # 添加这个，跳过初始化检查
    additional_config=weaviate.classes.init.AdditionalConfig(
        timeout=weaviate.classes.init.Timeout(init=30, query=60, insert=120)  # 设置超时
    )
)

embedding = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.getenv("GPTSAPI_API_KEY"),
    openai_api_base=os.getenv("OPENAI_API_BASE")
)

# 3.将数据存储到向量数据库
# 创建Langchain向量数据库实例
db = WeaviateVectorStore(
    client=client,
    index_name="DatasetDemo",
    text_key="text",
    embedding=embedding,
)
retriever = db.as_retriever(search_type="mmr")

# 创建多查询检索器
multi_query_retriever = MultiQueryRetriever.from_llm(
    retriever=retriever,
    llm=ChatOpenAI(
        model="gpt-4",
        api_key=os.getenv("GPTSAPI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE"),
        temperature=0
    ),
    include_original=True,
)

# 执行检索
docs = multi_query_retriever.invoke("关于LLMOps应用配置的文档有哪些")
print(docs)
print(len(docs))
