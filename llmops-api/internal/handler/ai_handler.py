#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/16 19:56
@Author         : jiayinkong@163.com
@File           : ai_handler.py
@Description    : 
"""
from dataclasses import dataclass

from flask_login import login_required, current_user
from injector import inject

from internal.schema.ai_schema import OptimizePromptReq, GenerateSuggestedQuestionsReq
from internal.service import AiService
from pkg.response import validate_error_json, compact_generate_response, success_json


@inject
@dataclass
class AiHandler:
    """AI辅助模块处理器"""
    ai_service: AiService

    @login_required
    def optimize_prompt(self):
        """根据传递的预设prompt进行优化"""
        # 1. 提取请求并校验
        req = OptimizePromptReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2. 掉筒服务优化prompt
        resp = self.ai_service.optimize_prompt(req.prompt.data)

        return compact_generate_response(resp)

    @login_required
    def generate_suggested_questions(self):
        """根据传递的消息id生成建议问题列表"""
        req = GenerateSuggestedQuestionsReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2. 调用服务生成建议问题列表
        suggest_questions = self.ai_service.generate_suggested_questions(
            req.message_id.data,
            current_user
        )

        return success_json(suggest_questions)
