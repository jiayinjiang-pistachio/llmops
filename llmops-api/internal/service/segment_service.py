#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/3 18:22
@Author         : jiayinkong@163.com
@File           : segment_service.py
@Description    : 
"""
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from injector import inject
from langchain_core.documents import Document as LCDocument
from redis import Redis
from sqlalchemy import asc, func

from internal.entity.cache_entity import LOCK_SEGMENT_UPDATE_ENABLED, LOCK_EXPIRE_TIME
from internal.entity.dataset_entity import SegmentStatus, DocumentStatus
from internal.exception import NotFoundException, ForbiddenException, FailException, ValidationException
from internal.model import Document, Segment
from internal.schema import GetSegmentsWithPageReq
from pkg.paginator import Paginator
from pkg.sqlalchemy import SQLAlchemy
from .base_service import BaseService
from .embeddings_service import EmbeddingsService
from .jieba_service import JiebaService
from .keyword_table_service import KeywordTableService
from .vector_database_service import VectorDatabaseService
from ..lib.helper import generate_text_hash


@inject
@dataclass
class SegmentService(BaseService):
    """文档片段服务"""
    db: SQLAlchemy
    redis_client: Redis
    keyword_table_service: KeywordTableService
    vector_database_service: VectorDatabaseService
    embeddings_service: EmbeddingsService
    jieba_service: JiebaService

    def get_segments_with_page(self, dataset_id: UUID, document_id: UUID, req: GetSegmentsWithPageReq) -> tuple[
        list[Segment], Paginator]:
        """根据传递的知识库id+文档id获取文档片段分页列表数据"""
        # todo:待完善
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        document: Document = self.get(Document, document_id)
        if document is None or document.dataset_id != dataset_id or str(document.account_id) != account_id:
            raise NotFoundException("该知识库文档不存在，或无权限查看，请核实后重试")

        # 构建分页器
        paginator = Paginator(db=self.db, req=req)

        # 构建过滤器
        filters = [Segment.document_id == document_id]
        if req.search_word.data:
            filters.append(Segment.content.ilike(f"%{req.search_word.data}%"))

        # 执行分页并获取数据
        segments = paginator.paginate(
            self.db.session.query(Segment).filter(*filters).order_by(asc("position"))
        )

        return segments, paginator

    def get_segment(self, dataset_id: UUID, document_id: UUID, segment_id: UUID) -> Segment:
        """根据传递的知识库id+文档id+片段id获取片段详情信息"""
        # todo:待完善
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        segment: Segment = self.get(Segment, segment_id)

        if (
                segment is None
                or segment.document_id != document_id
                or segment.dataset_id != dataset_id
                or str(segment.account_id) != account_id
        ):
            raise NotFoundException("该文档片段不存在，或无权限查看，请核实后重试")

        return segment

    def update_segment_enabled(self, dataset_id: UUID, document_id: UUID, segment_id: UUID, enabled: bool):
        """根据传递的知识库id+文档id+片段id更新片段状态"""
        # todo:待完善
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        # 获取片段信息并校验
        segment: Segment = self.get(Segment, segment_id)

        if (
                segment is None
                or segment.document_id != document_id
                or segment.dataset_id != dataset_id
                or str(segment.account_id) != account_id
        ):
            raise NotFoundException("该文档片段不存在，或无权限查看，请核实后重试")

        # 2. 判断文档是否处于可以修改的状态，只有构建完成才可以修改enabled
        if segment.status != SegmentStatus.COMPLETED:
            raise ForbiddenException("当前片段处于不可修改状态，请稍后重试")

        if segment.enabled == enabled:
            raise FailException(f"片段状态修改错误，当前已是{'启用' if enabled else '禁用'}状态")

        # 4. 获取更新文档启用状态的缓存键并检测是否上锁
        cache_key = LOCK_SEGMENT_UPDATE_ENABLED.format(segment_id=segment_id)
        cache_result = self.redis_client.get(cache_key)
        if cache_result is not None:
            raise FailException("当前文档片段正在修改启用状态，请稍后再次尝试")

        # 5. 上锁并更新对应的数据，涵盖postgres记录、weaviate、关键词表
        with self.redis_client.lock(cache_key, LOCK_EXPIRE_TIME):
            try:
                # 6. 修改postgres数据库里的文档片段
                self.update(
                    segment,
                    enabled=enabled,
                    disabled_at=None if enabled else datetime.now(),
                )
                # 7. 更新关键词表的对应信息，有可能新增，也有可能删除
                document = segment.document
                if enabled is True and document.enabled is True:
                    self.keyword_table_service.add_keyword_table_from_ids(dataset_id, [segment_id])
                else:
                    self.keyword_table_service.delete_keyword_table_from_ids(dataset_id, [segment_id])

                # 8. 同步处理weaviate向量数据库里的数据
                self.vector_database_service.collection.data.update(
                    uuid=segment.node_id,
                    properties={"segment_enabled": enabled}
                )

            except Exception as e:
                logging.exception(f"更改文档片段启用状态出现异常, segment_id: {segment_id}, 错误信息: {str(e)}")
                self.update(
                    segment,
                    error=str(e),
                    status=SegmentStatus.ERROR,
                    enabled=False,
                    disabled_at=datetime.now(),
                    stopped_at=datetime.now(),
                )
                raise FailException("更新文档片段启用状态失败，请稍后重试")

    def create_segment(self, dataset_id, document_id, req):
        """根据传递的信息新增文档片段信息"""
        # todo:待完善
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        # 1. 校验上传的内容的token长度总数，不能超过1000
        token_count = self.embeddings_service.calculate_token_count(req.content.data)
        if token_count > 1000:
            raise ValidationException("片段内容长度不能超过1000 token")

        # 2. 获取文档信息并校验
        document = self.get(Document, document_id)
        if (
                document is None
                or str(document.account_id) != account_id
                or document.dataset_id != dataset_id
        ):
            raise NotFoundException("该知识库文档不存在，或无权限新增，请核实后重试")

        # 3. 判断文档的状态是否可以新增片段数据，只有completed才可以新增
        if document.status != DocumentStatus.COMPLETED:
            raise FailException("当前文档不可新增片段，请稍后重试")

        # 4. 提取文档片段的最大位置
        position = self.db.session.query(func.coalesce(func.max(Segment.position), 0)).filter(
            Segment.document_id == document_id
        ).scalar()

        # 5. 检测是否传递了keywords，如果没有传递的话，调用jieba服务生成关键词
        if req.keywords.data is None or len(req.keywords.data) == 0:
            req.keywords.data = self.jieba_service.extract_keywords(req.content.data, 10)

        # 6. 往Postgres数据库中新增记录
        segment = None
        try:
            # 7. 位置+1并且新增segment记录
            position += 1
            segment = self.create(
                Segment,
                account_id=account_id,
                dataset_id=dataset_id,
                document_id=document_id,
                node_id=uuid.uuid4(),
                position=position,
                content=req.content.data,
                character_count=len(req.content.data),
                token_count=token_count,
                keywords=req.keywords.data,
                hash=generate_text_hash(req.content.data),
                enabled=True,
                processing_started_at=datetime.now(),
                indexing_completed_at=datetime.now(),
                completed_at=datetime.now(),
                status=SegmentStatus.COMPLETED,
            )

            # 8. 往向量数据库中新增数据
            self.vector_database_service.vector_store.add_documents(
                [LCDocument(
                    page_content=req.content.data,
                    metadata={
                        "account_id": str(document.account_id),
                        "dataset_id": str(document.dataset_id),
                        "document_id": str(document.id),
                        "segment_id": str(segment.id),
                        "node_id": str(segment.node_id),
                        "document_enabled": document.enabled,
                        "segment_enabled": True,
                    }
                )],
                ids=[str(segment.node_id)],
            )

            # 9. 重新计算片段的字符总数以及token总数
            document_character_count, document_token_count = self.db.session.query(
                func.coalesce(func.sum(Segment.character_count), 0),
                func.coalesce(func.sum(Segment.token_count), 0),
            ).first()

            # 10 .更新文档的对应信息
            self.update(
                document,
                character_count=document_character_count,
                token_count=document_token_count,
            )

            # 11. 更新关键词表信息
            if document.enabled is True:
                self.keyword_table_service.add_keyword_table_from_ids(dataset_id, [segment.id])
        except Exception as e:
            logging.exception(f"新增文档片段内容发生异常, 错误信息: {str(e)}")
            if segment:
                self.update(
                    segment,
                    error=str(e),
                    status=SegmentStatus.ERROR,
                    enabled=False,
                    disabled_at=datetime.now(),
                    stopped_at=datetime.now(),
                )
            raise FailException("新增文档片段失败，请稍后重试")
