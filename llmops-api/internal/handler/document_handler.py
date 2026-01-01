#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/1 14:49
@Author         : jiayinkong@163.com
@File           : document_handler.py
@Description    : 
"""
from dataclasses import dataclass
from uuid import UUID

from injector import inject

from internal.schema import CreateDocumentsReq, CreateDocumentsResp
from internal.service import DocumentService
from pkg.response import validate_error_json, success_json


@inject
@dataclass
class DocumentHandler:
    """文档处理器"""
    document_service: DocumentService

    def create_documents(self, dataset_id: UUID):
        """新增文档列表"""
        # 1. 提取请求参数并校验
        req = CreateDocumentsReq()
        if not req.validate():
            return validate_error_json(req.errors)
        # 2. 调用服务并创建文档，返回文档列表和处理批次
        documents, batch = self.document_service.create_documents(dataset_id, **req.data)
        # 3. 生成响应数据结构并返回
        resp = CreateDocumentsResp()

        return success_json(resp.dump(documents, batch))
