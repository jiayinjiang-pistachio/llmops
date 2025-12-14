#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/14 17:37
@Author         : jiayinkong@163.com
@File           : 3-最大边际相关性示例.py
@Description    : 
"""
import os

import dotenv
import weaviate
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey

dotenv.load_dotenv()

# 1. 构建加载器于分割器
loader = UnstructuredMarkdownLoader("./项目API文档.md")
text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", "。|！|？", "\.\s|\!\s|\?\s", "；|;\s", "，|,\s", " ", "", ],
    is_separator_regex=True,
    chunk_size=500,
    chunk_overlap=50,
    add_start_index=True,
)

# 2. 加载文档并分割
documents = loader.load()
chunks = text_splitter.split_documents(documents)

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

# 4.执行最大边际相关性搜索
# search_documents = db.similarity_search("关于应用配置的接口有哪些？")
search_documents = db.max_marginal_relevance_search("关于应用配置的接口有哪些？")

# 5.打印搜索的结果
# print(list(document.page_content[:100] for document in search_documents))
for document in search_documents:
    print(document.page_content[:100])
    print("===========")
