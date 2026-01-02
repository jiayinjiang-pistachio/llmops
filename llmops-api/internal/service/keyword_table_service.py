#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/1 21:08
@Author         : jiayinkong@163.com
@File           : keyword_table_service.py
@Description    : 
"""
from dataclasses import dataclass
from uuid import UUID

from injector import inject
from redis import Redis

from pkg.sqlalchemy import SQLAlchemy
from .base_service import BaseService
from ..model import KeywordTable


@inject
@dataclass
class KeywordTableService(BaseService):
    """知识库关键词表服务"""
    db: SQLAlchemy
    redis_client: Redis

    def get_keyword_table_from_dataset_id(self, dataset_id: UUID) -> KeywordTable:
        """根据传递的知识库id获取关键词表"""
        keyword_table = self.db.session.query(KeywordTable).filter(
            KeywordTable.dataset_id == dataset_id
        ).one_or_none()
        if keyword_table is None:
            keyword_table = self.create(KeywordTable, dataset_id=dataset_id, keyword_table={})

        return keyword_table
