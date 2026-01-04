#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/31 19:04
@Author         : jiayinkong@163.com
@File           : dataset_handler.py
@Description    : 
"""
from dataclasses import dataclass
from uuid import UUID

from flask import request
from injector import inject

from internal.core.file_extractor import FileExtractor
from internal.model import UploadFile
from internal.schema import CreateDatasetReq, GetDatasetResp, UpdateDatasetReq, GetDatasetsWithPageReq, \
    GetDatasetsWithPageResp
from internal.schema.dataset_schema import HitReq, GetDatasetQueriesResp
from internal.service import DatasetService, EmbeddingsService, JiebaService, VectorDatabaseService
from pkg.paginator import PageModel
from pkg.response import validate_error_json, success_json, success_message
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class DatasetHandler:
    """知识库处理器"""
    db: SQLAlchemy
    dataset_service: DatasetService
    embeddings_service: EmbeddingsService
    jieba_service: JiebaService
    file_extractor: FileExtractor
    vector_database_service: VectorDatabaseService

    def embeddings_query(self):
        # query = request.args.get("query")
        # vectors = self.embeddings_service.embeddings.embed_query(query)
        # return success_json({"vectors": vectors})
        # keywords = self.jieba_service.extract_keywords(query)
        # return success_json({"keywords": keywords})

        id = request.args.get('id')

        upload_file = self.db.session.query(UploadFile).get(id)
        content = self.file_extractor.load(upload_file, True)
        return success_json({"content": content})

    def hit(self, dataset_id: UUID):
        """根据传递的知识库id+所见参数执行召回测试"""
        # 1. 提取数据并校验
        req = HitReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2. 调用服务执行检索策略
        hit_result = self.dataset_service.hit(dataset_id, req)

        return success_json(hit_result)

    def get_dataset_queries(self, dataset_id: UUID):
        """根据传递的知识库id获取最近的10条查询记录"""
        dataset_queries = self.dataset_service.get_dataset_queries(dataset_id)
        resp = GetDatasetQueriesResp(many=True)
        return success_json(resp.dump(dataset_queries))

    def create_dataset(self):
        """创建知识库"""
        # 1.提取请求校验
        req = CreateDatasetReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2. 调用服务创建知识库
        self.dataset_service.create_dataset(req)

        return success_message("创建知识库成功")

    def get_dataset(self, dataset_id: UUID):
        """根据传递的知识库id获取详情"""
        dataset = self.dataset_service.get_dataset(dataset_id)
        resp = GetDatasetResp()

        return success_json(resp.dump(dataset))

    def update_dataset(self, dataset_id: UUID):
        """更新知识库"""
        # 1.提取请求刹那火速并校验
        req = UpdateDatasetReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2. 调用服务创建知识库
        self.dataset_service.update_dataset(dataset_id, req)

        # 3. 返回成功调用提示
        return success_message("更新知识库成功")

    def delete_dataset(self, dataset_id: UUID):
        """根据传递的知识库id删除知识库"""
        self.dataset_service.delete_dataset(dataset_id)
        return success_message("删除知识库成功")

    def get_datasets_with_page(self):
        """获取知识库分页+搜索列表数据"""
        # 1.提取query数据并校验
        req = GetDatasetsWithPageReq(request.args)
        if not req.validate():
            return validate_error_json(req.errors)

        # 2. 调用服务获取分页数据
        datasets, paginator = self.dataset_service.get_datasets_with_page(req)

        # 3. 构建响应
        resp = GetDatasetsWithPageResp(many=True)

        return success_json(PageModel(list=resp.dump(datasets), paginator=paginator))
