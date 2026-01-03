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
from injector import inject

from internal.schema import GetSegmentsWithPageReq, GetSegmentsWithPageResp, GetSegmentResp, UpdateSegmentEnabledReq
from internal.service import SegmentService
from pkg.paginator import PageModel
from pkg.response import validate_error_json, success_json, success_message


@inject
@dataclass
class SegmentHandler:
    """文档片段处理器"""
    segment_service: SegmentService

    def get_segments_with_page(self, dataset_id: UUID, document_id: UUID):
        """根据传递的知识库id+文档id获取片段分页数据"""
        req = GetSegmentsWithPageReq(request.args)
        if not req.validate():
            return validate_error_json(req.errors)

        # 调用服务获取分页数据
        segments, paginator = self.segment_service.get_segments_with_page(dataset_id, document_id, req)

        resp = GetSegmentsWithPageResp(many=True)
        return success_json(PageModel(list=resp.dump(segments), paginator=paginator))

    def get_segment(self, dataset_id: UUID, document_id: UUID, segment_id: UUID):
        """根据传递的知识库id+文档id+片段id获取片段详情信息"""
        segments = self.segment_service.get_segment(dataset_id, document_id, segment_id)

        resp = GetSegmentResp()

        return success_json(resp.dump(segments))

    def update_segment_enabled(self, dataset_id: UUID, document_id: UUID, segment_id: UUID):
        """根据传递的知识库id+文档id+片段id更新片段的启用状态"""
        req = UpdateSegmentEnabledReq()

        if not req.validate():
            return validate_error_json(req.errors)

        # 调用服务更新指定片段状态
        self.segment_service.update_segment_enabled(dataset_id, document_id, segment_id, req.enabled.data)

        return success_message("更改文档片段启用状态成功")
