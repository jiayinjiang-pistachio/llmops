#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/3 18:01
@Author         : jiayinkong@163.com
@File           : segment_handler.py
@Description    : 
"""
from dataclasses import dataclass
from uuid import UUID

from flask import request
from flask_login import current_user, login_required
from injector import inject

from internal.schema import GetSegmentsWithPageReq, GetSegmentsWithPageResp, GetSegmentResp, UpdateSegmentEnabledReq
from internal.schema.segment_schema import CreateSegmentReq, UpdateSegmentReq
from internal.service import SegmentService
from pkg.paginator import PageModel
from pkg.response import validate_error_json, success_json, success_message


@inject
@dataclass
class SegmentHandler:
    """文档片段处理器"""
    segment_service: SegmentService

    @login_required
    def create_segment(self, dataset_id: UUID, document_id: UUID):
        """根据传递的信息创建知识库文档片段"""
        req = CreateSegmentReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2. 调用服务创建片段记录
        self.segment_service.create_segment(dataset_id, document_id, req, current_user)

        return success_message("新增文档片段成功")

    @login_required
    def delete_segment(self, dataset_id: UUID, document_id: UUID, segment_id: UUID):
        """根据传递的信息删除指定的文档片段信息"""
        self.segment_service.delete_segment(dataset_id, document_id, segment_id, current_user)
        return success_message("删除文档片段成功")

    @login_required
    def update_segment(self, dataset_id: UUID, document_id: UUID, segment_id: UUID):
        """根据传递的信息更新文档片段信息"""
        # 1. 提取请求并校验
        req = UpdateSegmentReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2. 调用服务更新文档片段信息
        self.segment_service.update_segment(dataset_id, document_id, segment_id, req, current_user)

        return success_message("更新文档片段成功")

    @login_required
    def get_segments_with_page(self, dataset_id: UUID, document_id: UUID):
        """根据传递的知识库id+文档id获取片段分页数据"""
        req = GetSegmentsWithPageReq(request.args)
        if not req.validate():
            return validate_error_json(req.errors)

        # 调用服务获取分页数据
        segments, paginator = self.segment_service.get_segments_with_page(dataset_id, document_id, req, current_user)

        resp = GetSegmentsWithPageResp(many=True)
        return success_json(PageModel(list=resp.dump(segments), paginator=paginator))

    @login_required
    def get_segment(self, dataset_id: UUID, document_id: UUID, segment_id: UUID):
        """根据传递的知识库id+文档id+片段id获取片段详情信息"""
        segments = self.segment_service.get_segment(dataset_id, document_id, segment_id, current_user)

        resp = GetSegmentResp()

        return success_json(resp.dump(segments))

    @login_required
    def update_segment_enabled(self, dataset_id: UUID, document_id: UUID, segment_id: UUID):
        """根据传递的知识库id+文档id+片段id更新片段的启用状态"""
        req = UpdateSegmentEnabledReq()

        if not req.validate():
            return validate_error_json(req.errors)

        # 调用服务更新指定片段状态
        self.segment_service.update_segment_enabled(dataset_id, document_id, segment_id, req.enabled.data, current_user)

        return success_message("更改文档片段启用状态成功")
