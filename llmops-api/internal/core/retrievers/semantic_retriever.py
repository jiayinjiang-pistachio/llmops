#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/4 11:44
@Author         : jiayinkong@163.com
@File           : semantic_retriever.py
@Description    : 
"""
from typing import List
from uuid import UUID

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document as LCDocument
from langchain_core.pydantic_v1 import Field
from langchain_core.retrievers import BaseRetriever
from langchain_weaviate import WeaviateVectorStore
from weaviate.classes.query import Filter


class SemanticRetriever(BaseRetriever):
    """相似性检索器/向量检索器"""
    dataset_ids: list[UUID]
    vector_store: WeaviateVectorStore
    search_kwargs: dict = Field(default_factory=dict)

    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> List[LCDocument]:
        """根据传递的query执行相似性搜索"""
        # 1. 提取最大搜索条件k，默认值为4
        k = self.search_kwargs.pop("k", 4)

        # 2. 执行相似性搜素并获取得分信息
        search_result = self.vector_store.similarity_search_with_relevance_scores(
            query=query,
            k=k,
            filters=Filter.all_of([
                Filter.by_property("dataset_id").contains_any([str(dataset_id) for dataset_id in self.dataset_ids]),
                Filter.by_property("document_enabled").equal(True),
                Filter.by_property("segment_enabled").equal(True),
            ]),
            **self.search_kwargs,
        )
        if not search_result:
            return []

        documents: List[LCDocument] = []
        for lc_document, score in search_result:
            lc_document.metadata["score"] = score
            documents.append(lc_document)

        return documents
