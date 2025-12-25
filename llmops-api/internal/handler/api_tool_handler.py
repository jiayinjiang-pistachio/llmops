#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/25 17:30
@Author         : jiayinkong@163.com
@File           : api_tool_handler.py
@Description    : 
"""
from dataclasses import dataclass

from injector import inject

from internal.schema import ValidateOpenAPISchemaReq
from internal.service import APiToolService
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
