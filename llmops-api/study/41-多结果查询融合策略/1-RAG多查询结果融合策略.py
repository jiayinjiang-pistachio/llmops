#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/14 19:51
@Author         : jiayinkong@163.com
@File           : 1-RAG多查询结果融合策略.py
@Description    : 
"""
import os
from typing import List

import dotenv
import weaviate
from langchain.retrievers import MultiQueryRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.load import dumps, loads
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

# 创建Langchain向量数据库实例
db = WeaviateVectorStore(
    client=client,
    index_name="DatasetDemo",
    text_key="text",
    embedding=embedding,
)

retriever = db.as_retriever(search_type="mmr")


class RAGFusionRetriever(MultiQueryRetriever):
    """RAG多结果融合策略检索器"""
    k: int = 4

    def retrieve_documents(
            self, queries: List[str], run_manager: CallbackManagerForRetrieverRun
    ) -> List[List]:
        """重写检索文档函数，返回改为一个嵌套的列表"""
        documents = []

        for query in queries:
            docs = self.retriever.invoke(
                query,
                config={"callbacks": run_manager.get_child()}
            )
            documents.append(docs)
        return documents

    def unique_union(self, documents: List[List]) -> List[Document]:
        """使用RRF算法来去重合并对应的文档，参数为嵌套列表，返回值为文档列表"""
        # 1. 定义一个变量，存储每个文档的得分信息
        fused_results = {}

        # 2. 循环两层获取每一个文档信息
        for docs in documents:
            for rank, doc in enumerate(docs):
                # 3. 使用dumps函数将类示例转成字符串
                doc_str = dumps(doc)
                # 判断下该文档的字符串是否已经计算过得分
                if doc_str not in fused_results:
                    fused_results[doc_str] = 0
                # 计算新得分
                fused_results[doc_str] += 1 / (rank + 60)

        # 执行排序操作，获取相应的数据，使用降序
        reranked_results = [
            (loads(doc), score)
            for doc, score in sorted(fused_results.items(), key=lambda x: x[1], reverse=True)
        ]
        return [item[0] for item in reranked_results[:self.k]]


rag_fusion_retriever = RAGFusionRetriever.from_llm(
    retriever=retriever,
    llm=ChatOpenAI(
        model="gpt-4o",
        api_key=os.getenv("GPTSAPI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE"),
        temperature=0
    )
)

# 执行检索
docs = rag_fusion_retriever.invoke("关于LLMOps应用配置的文档有哪些")
print(docs)
print(len(docs))
