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

from injector import inject

from internal.core.tools.api_tools.entities import OpenAPISchema
from internal.exception import ValidationException
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
