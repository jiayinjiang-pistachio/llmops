#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/31 20:21
@Author         : jiayinkong@163.com
@File           : dataset_service.py
@Description    : 
"""
from dataclasses import dataclass
from uuid import UUID

from injector import inject
from sqlalchemy import desc

from internal.entity.dataset_entity import DEFAULT_DATASET_DESCRIPTION
from internal.exception import ValidationException, NotFoundException
from internal.lib.helper import datetime_to_timestamp
from internal.model import Dataset, Segment, DatasetQuery
from internal.schema import CreateDatasetReq, UpdateDatasetReq, GetDatasetsWithPageReq, HitReq
from pkg.paginator import Paginator
from pkg.sqlalchemy import SQLAlchemy
from .base_service import BaseService
from .retrieval_service import RetrievalService


@inject
@dataclass
class DatasetService(BaseService):
    """知识库服务"""
    db: SQLAlchemy
    retrieval_service: RetrievalService

    def create_dataset(self, req: CreateDatasetReq):
        """根据传递的请求信息创建知识库"""
        # todo:待完善授权
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        # 1. 检测该账号下是否存在同名的知识库
        dataset = self.db.session.query(Dataset).filter_by(
            account_id=account_id,
            name=req.name.data
        ).one_or_none()

        if dataset:
            raise ValidationException(f"该知识库{req.name.data}已存在")

        # 2.检测是否传递了描述信息，如果没有传递需要补上
        if req.description.data is None or req.description.data.strip() == "":
            req.description.data = DEFAULT_DATASET_DESCRIPTION.format(name=req.name.data)

        # 3. 创建知识库记录并返回
        return self.create(
            Dataset,
            account_id=account_id,
            name=req.name.data,
            icon=req.icon.data,
            description=req.description.data,
        )

    def get_dataset(self, dataset_id: UUID):
        """根据传递的知识库id获取知识库记录"""
        # todo:待完善授权
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        dataset = self.get(Dataset, dataset_id)
        if dataset is None or str(dataset_id) != str(dataset.id):
            raise ValidationException("该知识库不存在")

        return dataset

    def update_dataset(self, dataset_id: UUID, req: UpdateDatasetReq):
        """根据传递的知识库id+数据更新知识库"""
        # todo:待完善授权
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        # 1.检测知识库是否存在并校验
        dataset = self.get(Dataset, dataset_id)
        if dataset is None or str(dataset_id) != str(dataset.id):
            raise ValidationException("该知识库不存在")

        # 2. 检验描述信息是否为空，如果为空则人为设置
        if req.description.data is None or req.description.data.strip() == "":
            req.description.data = DEFAULT_DATASET_DESCRIPTION.format(name=req.name.data)

        # 4. 更新数据
        self.update(
            dataset,
            name=req.name.data,
            icon=req.icon.data,
            description=req.description.data,
        )

        return dataset

    def get_datasets_with_page(self, req: GetDatasetsWithPageReq):
        """根据传递的信息获取知识库列表分页数据"""
        # todo:待完善授权
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        # 1. 构建分页器
        paginator = Paginator(db=self.db, req=req)

        # 2. 构建筛选器
        filters = [Dataset.account_id == account_id]
        if req.search_word.data:
            filters.append(Dataset.name.ilike(f"%{req.search_word.data}%"))

        # 3. 执行分页并获取数据
        datasets = paginator.paginate(
            self.db.session.query(Dataset).filter(*filters).order_by(desc("created_at"))
        )

        return datasets, paginator

    def hit(self, dataset_id: UUID, req: HitReq) -> list[dict]:
        """根据传递的知识库id+请求执行召回测试"""
        # todo:待完善授权
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        # 1. 检测知识库是否存在并校验
        dataset = self.get(Dataset, dataset_id)
        if dataset is None or str(dataset.account_id) != account_id:
            raise NotFoundException("该知识库不存在")

        # 2. 调用检索服务执行检索
        lc_documents = self.retrieval_service.search_in_datasets(
            dataset_ids=[dataset_id],
            **req.data
        )
        lc_document_dict = {
            str(lc_document.metadata["segment_id"]): lc_document
            for lc_document in lc_documents
        }

        # 3. 根据检索到的数据查询对应的片段信息
        segments = self.db.session.query(Segment).filter(
            Segment.id.in_([
                str(lc_document.metadata["segment_id"])
                for lc_document in lc_documents
            ])
        ).all()
        segment_dict = {
            str(segment.id): segment
            for segment in segments
        }

        # 4. 排序片段数据
        sorted_segments = [
            segment_dict[str(lc_document.metadata["segment_id"])]
            for lc_document in lc_documents
            if str(lc_document.metadata["segment_id"]) in segment_dict
        ]

        # 5. 组装响应数据
        hit_result = []
        for segment in sorted_segments:
            document = segment.document
            upload_file = document.upload_file
            hit_result.append({
                "id": segment.id,
                "document": {
                    "id": document.id,
                    "name": document.name,
                    "extension": upload_file.extension,
                    "mime_type": upload_file.mime_type,
                },
                "dataset_id": segment.dataset_id,
                "score": lc_document_dict[str(segment.id)].metadata["score"],
                "position": segment.position,
                "content": segment.content,
                "keywords": segment.keywords,
                "character_count": segment.character_count,
                "token_count": segment.token_count,
                "hit_count": segment.hit_count,
                "enabled": segment.enabled,
                "disabled_at": datetime_to_timestamp(segment.disabled_at),
                "status": segment.status,
                "error": segment.error,
                "updated_at": datetime_to_timestamp(segment.updated_at),
                "created_at": datetime_to_timestamp(segment.created_at),
            })

        return hit_result

    def get_dataset_queries(self, dataset_id: UUID) -> list[DatasetQuery]:
        """根据传递的知识库id获取最近的10条查询记录"""
        # todo:待完善授权
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        # 1. 获取知识库并校验权限
        dataset: Dataset = self.get(Dataset, dataset_id)
        if dataset is None or str(dataset.account_id) != account_id:
            raise NotFoundException("该知识库不存在")

        # 2. 调用知识库查询模型查找最近的10条记录
        dataset_queries = self.db.session.query(DatasetQuery).filter(
            DatasetQuery.dataset_id == dataset_id
        ).order_by(desc("created_at")).limit(10).all()

        return dataset_queries
