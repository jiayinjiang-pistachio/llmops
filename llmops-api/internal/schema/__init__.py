#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/16 08:06
@Author         : jiayinkong@163.com
@File           : __init__.py.py
@Description    : 请求和响应的结构体
"""
from .api_tool_schema import ValidateOpenAPISchemaReq
from .app_schema import CompletionReq

__all__ = ["CompletionReq", "ValidateOpenAPISchemaReq"]
