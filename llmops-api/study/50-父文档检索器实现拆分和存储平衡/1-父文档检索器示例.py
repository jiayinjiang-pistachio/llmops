#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/15 20:43
@Author         : jiayinkong@163.com
@File           : 1-父文档检索器示例.py
@Description    : 
"""
import os

import dotenv
import weaviate
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import LocalFileStore
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey

dotenv.load_dotenv()

# 1. 创建加载器与文档列表，并加载文档
loaders = [
    UnstructuredFileLoader("./电商产品数据.txt"),
    UnstructuredFileLoader("./项目API文档.md")
]
docs = []

for loader in loaders:
    docs.extend(loader.load())

# 创建文本分割器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)

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

# 创建Langchain向量数据库实例
vector_store = WeaviateVectorStore(
    client=client,
    index_name="ParentDocument",
    text_key="text",
    embedding=embedding,
)

byte_store = LocalFileStore("./parent-document")

parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

# 4.创建父文档检索器
retriever = ParentDocumentRetriever(
    vectorstore=vector_store,
    byte_store=byte_store,
    parent_splitter=parent_splitter,
    child_splitter=child_splitter,
)

# 5.添加文档
# retriever.add_documents(docs, ids=None)

# 6.检索并返回内容
# search_docs = retriever.vectorstore.similarity_search("分享关于LLMOps的一些应用配置")
search_docs = retriever.invoke("分享关于LLMOps的一些应用配置")
print(search_docs)
print(len(search_docs))
