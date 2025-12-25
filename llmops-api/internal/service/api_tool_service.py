#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/25 17:33
@Author         : jiayinkong@163.com
@File           : api_tool_service.py
@Description    : 
"""
import json
from dataclasses import dataclass
from uuid import UUID

from injector import inject

from internal.core.tools.api_tools.entities import OpenAPISchema
from internal.exception import ValidationException, NotFoundException
from internal.model import ApiToolProvider, ApiTool
from internal.schema.api_tool_schema import CreateAPIToolReq
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class APiToolService():
    """自定义API插件服务"""
    db: SQLAlchemy

    @classmethod
    def parse_openapi_schema(cls, openapi_schema_str: str) -> OpenAPISchema:
        """解析传递的openapi_schema字符串，如果出错则抛出错误"""
        try:
            data = json.loads(openapi_schema_str.strip())
            if not isinstance(data, dict):
                raise
        except Exception as e:
            raise ValidationException("传递数据必须符合OpenAPI规范的JSON字符串")
        return OpenAPISchema(**data)

    def create_api_tool(self, req: CreateAPIToolReq):
        """根据传递的请求创建自定义API工具"""
        # todo:等待授权认证模块完成进行切换调整
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        # 1. 校验并提取openapi_schema对应的数据
        openapi_schema = self.parse_openapi_schema(req.openapi_schema.data)

        # 2. 查询当前登录的账号是否已经创建了同名的工具提供者，如果是则抛出错误
        api_tool_provider = self.db.session.query(ApiToolProvider).filter_by(
            account_id=account_id,
            name=req.name.data,
        ).one_or_none()

        if api_tool_provider:
            raise ValidationException(f"该工具提供者名字{req.name.data}已存在")

        # 3. 开启数据库的提交
        with self.db.auto_commit():
            # 4. 首先创建工具提供者，并获取工具提供者的id信息，然后再创建工具信息
            api_tool_provider = ApiToolProvider(
                account_id=account_id,
                name=req.name.data,
                icon=req.icon.data,
                description=openapi_schema.description,
                openapi_schema=req.openapi_schema.data,
                headers=req.headers.data,
            )
            self.db.session.add(api_tool_provider)
            self.db.session.flush()  # 刷新

            # 5. 创建API工具并关联api_tool_provider
            for path, path_item in openapi_schema.paths.items():
                for method, method_item in path_item.items():
                    api_tool = ApiTool(
                        account_id=account_id,
                        provider_id=api_tool_provider.id,
                        name=method_item.get("operationId"),
                        description=method_item.get("description"),
                        url=f"{openapi_schema.server}{path}",
                        method=method,
                        parameters=method_item.get("parameters", []),
                    )
                    self.db.session.add(api_tool)
                    self.db.session.flush()

    def get_api_tool_provider(self, provider_id: UUID):
        """根据传递的provider_id获取API工具提供者信息"""
        # todo:等待授权认证完善
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        # 1. 查询数据库获取对应的数据
        api_tool_provider = self.db.session.query(ApiToolProvider).get(provider_id)

        # 2. 校验数据是否为空，并且判断该数据是否属于当前账号
        if api_tool_provider is None or str(api_tool_provider.account_id) != str(account_id):
            raise NotFoundException("该工具提供者不存在")

        return api_tool_provider

    def get_api_tool(self, provider_id: UUID, tool_name: str):
        """根据传递的provider_id+tool_name获取对应工具的参数详情信息"""
        # todo: 等授权完善
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        api_tool = self.db.session.query(ApiTool).filter_by(
            provider_id=provider_id,
            name=tool_name,
        ).one_or_none()

        if api_tool is None or str(api_tool.account_id) != account_id:
            raise NotFoundException("该工具不存在")
        return api_tool
