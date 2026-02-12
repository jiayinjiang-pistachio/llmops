#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/10 19:52
@Author         : jiayinkong@163.com
@File           : vector_database_service.py
@Description    : 
"""
import os

import weaviate
import weaviate.classes as wvc
from injector import inject
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_weaviate import WeaviateVectorStore
from weaviate import WeaviateClient
from weaviate.collections import Collection
from weaviate.collections.classes.config import Property, DataType

from .embeddings_service import EmbeddingsService


@inject
class VectorDatabaseService:
    """向量数据库服务"""
    client: WeaviateClient
    vector_store: WeaviateVectorStore
    embeddings_service: EmbeddingsService

    def __init__(self, embeddings_service: EmbeddingsService):
        """构造函数，完成向量数据库服务的客户端+Langchain向量数据库实例的创建"""
        # 赋值embeddings_service
        self.embeddings_service = embeddings_service
        # 从环境变量读取，如果没设置则默认为 'DatasetV2'
        self.index_name = os.getenv("WEAVIATE_INDEX_NAME", "DatasetV2")

        # 1. 创建/连接weaviate向量数据库
        self.client = weaviate.connect_to_local(
            host=os.getenv("WEAVIATE_HOST"),
            port=int(os.getenv("WEAVIATE_PORT")),
            grpc_port=50051,
            # 核心修改：跳过初始化检查
            skip_init_checks=True,
            # 或者增加超时时间
            additional_config=wvc.init.AdditionalConfig(
                timeout=wvc.init.Timeout(init=30)
            )
        )

        # 核心：确保这个新名字的 Collection 有正确的类型
        self._ensure_schema_exists()

        # 2. 创建Langchain向量数据库
        self.vector_store = WeaviateVectorStore(
            client=self.client,
            index_name=self.index_name,
            text_key="text",
            embedding=self.embeddings_service.embeddings,
        )

    def get_retriever(self) -> VectorStoreRetriever:
        """获取检索器"""
        return self.vector_store.as_retriever()

    @property
    def collection(self) -> Collection:
        return self.client.collections.get(self.index_name)

    def _ensure_schema_exists(self):
        if not self.client.collections.exists(self.index_name):
            print(f"正在创建新索引: {self.index_name}")
            self.client.collections.create(
                name=self.index_name,
                properties=[
                    Property(name="text", data_type=DataType.TEXT),
                    Property(name="account_id", data_type=DataType.TEXT),  # 保护 UUID
                    Property(name="dataset_id", data_type=DataType.TEXT),
                    Property(name="document_id", data_type=DataType.TEXT),
                    Property(name="segment_id", data_type=DataType.TEXT),
                    Property(name="node_id", data_type=DataType.TEXT),
                ]
            )
