#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/1 18:29
@Author         : jiayinkong@163.com
@File           : document_task.py
@Description    : 
"""
from uuid import UUID

from celery import shared_task


@shared_task
def build_documents(document_ids: list[UUID]) -> None:
    """根据传递的文档id列表，构建文档"""
    from app.http.module import injector
    from internal.service.indexing_service import IndexingService

    indexing_service = injector.get(IndexingService)
    indexing_service.build_documents(document_ids)


@shared_task
def update_document_enabled(document_id: UUID) -> None:
    """根据传递的文档id修改文档的状态"""
    from app.http.module import injector
    from internal.service.indexing_service import IndexingService

    indexing_service = injector.get(IndexingService)
    indexing_service.update_document_enabled(document_id)
