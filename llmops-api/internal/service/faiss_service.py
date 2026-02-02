#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/2/2 19:23
@Author         : jiayinkong@163.com
@File           : faiss_service.py
@Description    : 
"""
import os

from injector import inject
from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain_community.vectorstores import FAISS
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool, tool
from langchain_text_splitters import MarkdownTextSplitter

from .embeddings_service import EmbeddingsService
from ..core.agent.entities.agent_entity import DATASET_RETRIEVAL_TOOL_NAME
from ..lib.helper import combine_documents


@inject
class FaissService:
    """Faiss向量数据库服务器"""
    faiss: FAISS
    embedding_service: EmbeddingsService

    def __init__(self, embedding_service: EmbeddingsService):
        """构造函数，完成faiss向量数据的初始化"""
        self.embedding_service = embedding_service

        # 路径配置
        internal_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.source_docs_path = os.path.join(internal_path, "storage", "vector_store")
        self.faiss_vector_store_path = os.path.join(internal_path, "core", "vector_store")

        # 执行初始化逻辑
        self.faiss = self._initialize_faiss()

    def convert_faiss_to_tool(self) -> BaseTool:
        """将FAISS向量数据库检索器转换成LangChain工具"""
        # 1. 将faiss向量数据库转成检索器
        retrieval = self.faiss.as_retriever(
            search_type="mmr",  # 最大边际相关性搜索
            search_kwargs={"k": 5, "fetch_k": 20},
        )

        # 2. 构建检索链，并将检索的结果合并成字符串
        search_chain = retrieval | combine_documents

        class DatasetRetrievalInput(BaseModel):
            """知识库检索工具输入结构"""
            query: str = Field(description="知识库检索query语句，类型为字符串")

        @tool(DATASET_RETRIEVAL_TOOL_NAME, args_schema=DatasetRetrievalInput)
        def dataset_retrieval(query: str) -> str:
            """如果需要检索扩展的知识库内容，当你觉得用户的提问超出你的知识范围时，可以尝试调用该工具，输入为搜索query语句，返回数据为检索内容字符串"""
            return search_chain.invoke(query)

        return dataset_retrieval

    def _initialize_faiss(self):
        """初始化或加载 FAISS 向量库"""
        index_file = os.path.join(self.faiss_vector_store_path, "index.faiss")

        # 1. 检查索引是否存在
        if os.path.exists(index_file):
            print(f"--- 发现现有索引，正在从 {self.faiss_vector_store_path} 加载 ---")
            return FAISS.load_local(
                folder_path=self.faiss_vector_store_path,
                embeddings=self.embedding_service.embeddings,
                allow_dangerous_deserialization=True,
            )

        # 2. 如果不存在，则进入构建逻辑
        print(f"--- 未发现索引，正在从 {self.source_docs_path} 构建向量库 ---")
        return self._build_from_scratch()

    def _build_from_scratch(self):
        """从 Markdown 源文件构建向量索引"""
        if not os.path.exists(self.source_docs_path):
            os.makedirs(self.source_docs_path)
            raise FileNotFoundError(f"源文档目录不存在，已创建空目录: {self.source_docs_path}")

        # 加载文档
        loader = DirectoryLoader(
            self.source_docs_path,
            glob="**/*.md",
            loader_cls=UnstructuredMarkdownLoader
        )
        documents = loader.load()

        if not documents:
            # 如果没有文档，建议返回一个空的向量库或者报错
            raise ValueError(f"目录 {self.source_docs_path} 下没有可用的 .md 文件")

        # 切分文档
        text_splitter = MarkdownTextSplitter(chunk_size=500, chunk_overlap=50)
        split_docs = text_splitter.split_documents(documents)

        # 生成向量并保存
        faiss_instance = FAISS.from_documents(
            documents=split_docs,
            embedding=self.embedding_service.embeddings
        )

        # 确保目标目录存在
        if not os.path.exists(self.faiss_vector_store_path):
            os.makedirs(self.faiss_vector_store_path)

        faiss_instance.save_local(self.faiss_vector_store_path)
        print(f"--- 向量库构建完成，已保存至 {self.faiss_vector_store_path} ---")

        return faiss_instance
