#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/31 21:38
@Author         : jiayinkong@163.com
@File           : embeddings_service.py
@Description    : 
"""
import os
from dataclasses import dataclass

import tiktoken
from injector import inject
from langchain.embeddings import CacheBackedEmbeddings
from langchain_community.storage import RedisStore
from langchain_core.embeddings import Embeddings
# from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from redis import Redis


@inject
@dataclass
class EmbeddingsService:
    """文本嵌入模型服务"""
    _store: RedisStore
    _embeddings: Embeddings
    _cache_backed_embeddings: CacheBackedEmbeddings

    def __init__(self, redis: Redis):
        """构造函数，初始化文本嵌入模型客户端、存储器、缓存客户端"""
        self._store = RedisStore(client=redis)

        # 防御性设置：确保在初始化模型前环境变量已存在
        # if not os.environ.get("HF_ENDPOINT"):
        #     os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

        # 禁用 hf_transfer，使用普通下载方式
        os.environ['HF_HUB_ENABLE_HF_TRANSFER'] = '0'

        # self._embeddings = HuggingFaceEmbeddings(
        #     model_name="sentence-transformers/paraphrase-albert-small-v2",
        #     # 确保这个路径存在，或者库会自动创建它
        #     cache_folder=os.path.join(os.getcwd(), "internal", "core", "embeddings"),
        #     model_kwargs={
        #         "trust_remote_code": True,
        #         # "local_files_only": True,  # 强制只使用本地文件
        #     }
        # )

        self._embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("GPTSAPI_API_KEY"),
            openai_api_base=os.getenv("OPENAI_API_BASE")
        )

        self._cache_backed_embeddings = CacheBackedEmbeddings.from_bytes_store(
            self._embeddings,
            self._store,
            namespace="embeddings",
        )

    @classmethod
    def calculate_token_count(cls, query: str) -> int:
        """计算传入文本的token数"""
        encoding = tiktoken.encoding_for_model("gpt-3.5")
        return len(encoding.encode(query))

    @property
    def store(self) -> RedisStore:
        return self._store

    @property
    def embeddings(self) -> Embeddings:
        return self._embeddings

    @property
    def cache_backed_embeddings(self) -> CacheBackedEmbeddings:
        return self._cache_backed_embeddings
