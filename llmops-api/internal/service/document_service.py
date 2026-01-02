#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/1 15:24
@Author         : jiayinkong@163.com
@File           : document_service.py
@Description    : 
"""
import logging
import random
import time
from dataclasses import dataclass
from uuid import UUID

from injector import inject
from sqlalchemy import desc, asc, func

from internal.entity.dataset_entity import ProcessType, SegmentStatus
from internal.model import Document, Dataset, UploadFile, ProcessRule, Segment
from pkg.sqlalchemy import SQLAlchemy
from .base_service import BaseService
from ..entity.upload_file_entity import ALLOWED_DOCUMENT_EXTENSION
from ..exception import ForbiddenException, FailException, NotFoundException
from ..lib.helper import datetime_to_timestamp
from ..task.document_task import build_documents


@inject
@dataclass
class DocumentService(BaseService):
    """文档服务"""
    db: SQLAlchemy

    def create_documents(
            self,
            dataset_id: UUID,
            upload_file_ids: list[UUID],
            process_type: str = ProcessType.AUTOMATIC,
            rule: dict = None,
    ) -> tuple[Document, str]:
        """根据传递的信息创建文档并调用异步任务"""
        # todo: 待完善授权
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        # 1. 检测知识库权限
        dataset: Dataset = self.get(Dataset, dataset_id)
        if dataset is None or str(dataset.account_id) != account_id:
            raise ForbiddenException("当前用户无该知识库权限或知识库不存在")

        # 2. 提取文件并校验文件权限及扩展
        upload_files: list[UploadFile] = self.db.session.query(UploadFile).filter(
            UploadFile.account_id == account_id,
            UploadFile.id.in_(upload_file_ids),
        ).all()

        # 3. 进一步过滤符合格式的文件列表
        upload_files = [upload_file for upload_file in upload_files if
                        upload_file.extension.lower() in ALLOWED_DOCUMENT_EXTENSION]
        if len(upload_files) == 0:
            logging.warning(
                f"上传文件列表未解析到合法文件，account_id: {account_id}, dataset_id: {dataset_id}, upload_file_ids: {upload_file_ids}"
            )
            raise FailException("暂未解析到合法文件，请重新上传")

        # 4. 创建批次与处理规则并记录到数据库中
        batch = time.strftime("%Y%m%d%H%M%S") + str(random.randint(100000, 999999))
        process_rule = self.create(
            ProcessRule,
            account_id=account_id,
            dataset_id=dataset_id,
            mode=process_type,
            rule=rule,
        )
        # 5. 获取当前知识库最新的文档的位置
        position = self.get_latest_document_position(dataset_id)

        # 6. 循环遍历所有合法文件并记录
        documents: list[Document] = []
        for upload_file in upload_files:
            position += 1
            document: Document = self.create(
                Document,
                account_id=account_id,
                dataset_id=dataset_id,
                upload_file_id=upload_file.id,
                process_rule_id=process_rule.id,
                batch=batch,
                name=upload_file.name,
                position=position,
            )
            documents.append(document)

        # 7. 调用异步任务，完成后续操作
        build_documents.delay([document.id for document in documents])

        # 8. 返回
        return documents, batch

    def get_latest_document_position(self, dataset_id):
        """获取当前知识库最新的文档的位置"""
        document: Document = self.db.session.query(Document).filter(
            Document.dataset_id == dataset_id
        ).order_by(desc("position")).first()
        return document.position if document else 0

    def get_document_status(self, dataset_id: UUID, batch: str) -> list[dict]:
        """根据传递的知识库id+处理批次获取文档列表的状态"""
        # todo:等待完善
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        # 1.检测知识库权限
        dataset: Dataset = self.get(Dataset, dataset_id)
        if dataset is None or str(dataset.account_id) != account_id:
            raise ForbiddenException("当前用户无该知识库权限或知识库不存在")

        # 2. 查询当前知识库下该批次的文档列表
        documents = self.db.session.query(Document).filter(
            Document.dataset_id == dataset_id,
            Document.batch == batch,
        ).order_by(asc("position")).all()

        if documents is None or len(documents) == 0:
            raise NotFoundException("该处理批次未发现文档，请核实后重试")

        # 3. 循环遍历文档列表提取文档状态信息
        documents_status = []
        for document in documents:
            # 4. 查询每个文档的总片段数和已构建完成的片段数
            segment_count = self.db.session.query(func.count(Segment.id)).filter(
                Segment.document_id == document.id,
            ).scalar()
            completed_segment_count = self.db.session.query(func.count(Segment.id)).filter(
                Segment.document_id == document.id,
                Segment.status == SegmentStatus.COMPLETED,
            ).scalar()

            upload_file = document.upload_file
            documents_status.append({
                "id": document.id,
                "name": document.name,
                "size": upload_file.size,
                "extension": upload_file.extension,
                "mime_type": upload_file.mime_type,
                "position": document.position,
                "segment_count": segment_count,
                "completed_segment_count": completed_segment_count,
                "error": document.error,
                "status": document.status,
                "processing_started_at": datetime_to_timestamp(document.processing_started_at),
                "parsing_completed_at": datetime_to_timestamp(document.parsing_completed_at),
                "splitting_completed_at": datetime_to_timestamp(document.splitting_completed_at),
                "indexing_completed_at": datetime_to_timestamp(document.indexing_completed_at),
                "completed_at": datetime_to_timestamp(document.completed_at),
                "stopped_at": datetime_to_timestamp(document.stopped_at),
                "created_at": datetime_to_timestamp(document.created_at),
            })

        return documents_status
