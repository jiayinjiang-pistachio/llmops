#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/10 19:52
@Author         : jiayinkong@163.com
@File           : vector_database_service.py
@Description    : 
"""
import os
from dataclasses import dataclass

from flask_weaviate import FlaskWeaviate
from injector import inject
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_weaviate import WeaviateVectorStore
from weaviate.collections import Collection
from weaviate.collections.classes.config import Property, DataType

from .embeddings_service import EmbeddingsService


@inject
@dataclass
class VectorDatabaseService:
    """向量数据库服务"""
    # client: WeaviateClient
    # vector_store: WeaviateVectorStore
    weaviate: FlaskWeaviate
    embeddings_service: EmbeddingsService

    # 这是 dataclass 专门用于“在自动生成的 __init__ 运行完之后”执行代码的地方。此时依赖已经注入完成
    def __post_init__(self):
        # 从环境变量读取，如果没设置则默认为 'DatasetV2'
        self.index_name = os.getenv("WEAVIATE_INDEX_NAME", "DatasetV2")

    @property
    def vector_store(self) -> WeaviateVectorStore:
        # 在这里进行静默检查（或者确保调用此属性时已有 context）
        self._ensure_schema_exists()

        return WeaviateVectorStore(
            client=self.weaviate.client,
            index_name=self.index_name,
            text_key="text",
            embedding=self.embeddings_service.cache_backed_embeddings,
        )

    def get_retriever(self) -> VectorStoreRetriever:
        """获取检索器"""
        return self.vector_store.as_retriever()

    @property
    def collection(self) -> Collection:
        return self.weaviate.client.collections.get(self.index_name)

    def _ensure_schema_exists(self):
        # 使用 getattr 防止重复检查 schema 带来的开销
        if getattr(self, "_schema_verified", False):
            return

        if not self.weaviate.client.collections.exists(self.index_name):
            print(f"正在创建新索引: {self.index_name}")
            self.weaviate.client.collections.create(
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
