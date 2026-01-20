#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/19 19:06
@Author         : jiayinkong@163.com
@File           : openapi_handler.py
@Description    : 
"""
from dataclasses import dataclass

from flask_login import current_user, login_required
from injector import inject

from internal.schema import OpenAPIChatReq
from internal.service import OpenapiService
from pkg.response import validate_error_json, compact_generate_response


@inject
@dataclass
class OpenapiHandler:
    """开放API处理器"""
    openapi_service: OpenapiService

    @login_required
    def chat(self):
        """开放Chat对话接口"""
        # 1. 提取请求并校验数据
        req = OpenAPIChatReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2. 调用服务创建会话
        resp = self.openapi_service.chat(req, current_user)

        return compact_generate_response(resp)
