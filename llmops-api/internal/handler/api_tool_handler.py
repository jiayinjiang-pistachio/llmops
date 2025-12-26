#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/25 17:30
@Author         : jiayinkong@163.com
@File           : api_tool_handler.py
@Description    : 
"""
from dataclasses import dataclass
from uuid import UUID

from flask import request
from injector import inject

from internal.schema import ValidateOpenAPISchemaReq, CreateAPIToolReq, GetApiToolProviderResp, GetApiToolResp, \
    GetApiToolProvidersWithPageReq, GetApiToolProvidersWithPageResp, UpdateApiToolProviderReq
from internal.service import APiToolService
from pkg.paginator import PageModel
from pkg.response import validate_error_json, success_json


@inject
@dataclass
class ApiToolHandler:
    """自定义API插件处理器"""
    api_tool_service: APiToolService

    def validate_openapi_schema(self):
        """校验传递的openapi_schema字符串是否正确"""
        req = ValidateOpenAPISchemaReq()

        if not req.validate():
            return validate_error_json(req.errors)

        self.api_tool_service.parse_openapi_schema(req.openapi_schema.data)

        return success_json("数据校验成功")

    def create_api_tool_provider(self):
        """创建自定义API工具"""
        req = CreateAPIToolReq()

        if not req.validate():
            return validate_error_json(req.errors)

        self.api_tool_service.create_api_tool(req)

        return success_json("创建自定义API插件成功")

    def get_api_tool_provider(self, provider_id: UUID):
        """根据传递的provider_id获取工具提供者的原始信息"""
        api_tool_provider = self.api_tool_service.get_api_tool_provider(provider_id)

        resp = GetApiToolProviderResp()

        return success_json(resp.dump(api_tool_provider))

    def get_api_tool(self, provider_id: UUID, tool_name: str):
        """根据传递的provider_id+tool_name获取工具详情信息"""
        api_tool = self.api_tool_service.get_api_tool(provider_id, tool_name)

        resp = GetApiToolResp()

        return success_json(resp.dump(api_tool))

    def delete_api_tool_provider(self, provider_id: UUID):
        """根据传递的provider_id删除对应的工具提供者信息"""
        self.api_tool_service.delete_api_tool_provider(provider_id)

        return success_json("删除自定义API插件成功")

    def get_api_tool_providers_with_page(self):
        """获取API工具提供者列表信息，该接口支持分页"""
        req = GetApiToolProvidersWithPageReq(request.args)
        if not req.validate():
            return validate_error_json(req.errors)

        api_tool_providers, paginator = self.api_tool_service.get_api_tool_providers_with_page(req)

        resp = GetApiToolProvidersWithPageResp(many=True)

        return success_json(
            PageModel(list=resp.dump(api_tool_providers), paginator=paginator),
        )

    def update_api_tool_provider(self, provider_id: UUID):
        """更新自定义API工具提供者信息"""
        req = UpdateApiToolProviderReq()
        if not req.validate():
            return validate_error_json(req.errors)

        self.api_tool_service.update_api_tool_provider(provider_id, req)

        return success_json("更新自定义API插件成功")
