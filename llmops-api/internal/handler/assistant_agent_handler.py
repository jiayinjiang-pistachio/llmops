#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/2/2 16:00
@Author         : jiayinkong@163.com
@File           : assistant_agent_handler.py
@Description    : 
"""
from dataclasses import dataclass
from uuid import UUID

from flask import request
from flask_login import login_required, current_user
from injector import inject

from internal.schema.assistant_agent_schema import AssistantAgentChat, GetAssistantAgentMessagesWithPageReq, \
    GetAssistantAgentMessagesWithPageResp
from internal.service import AssistantAgentService
from pkg.paginator import PageModel
from pkg.response import validate_error_json, compact_generate_response, success_message, success_json


@inject
@dataclass
class AssistantAgentHandler:
    """辅助agent处理器"""
    assistant_agent_service: AssistantAgentService

    @login_required
    def assistant_agent_chat(self):
        """辅助agent聊天"""
        req = AssistantAgentChat()
        if not req.validate():
            return validate_error_json(req.errors)

        resp = self.assistant_agent_service.chat(req.query.data, current_user)

        return compact_generate_response(resp)

    @login_required
    def stop_assistant_agent_chat(self, task_id: UUID):
        """停止辅助agent聊天"""
        self.assistant_agent_service.stop_chat(task_id, current_user)
        return success_message("停止辅助agent会话成功")

    @login_required
    def get_assistant_agent_messages_with_page(self):
        """获取辅助agent消息分页列表"""
        req = GetAssistantAgentMessagesWithPageReq(request.args)
        if not req.validate():
            return validate_error_json(req.errors)

        messages, paginator = self.assistant_agent_service.get_conversation_messages_with_page(req, current_user)

        resp = GetAssistantAgentMessagesWithPageResp(many=True)

        return success_json(PageModel(list=resp.dump(messages), paginator=paginator))

    @login_required
    def delete_assistant_agent_conversation(self):
        """删除与辅助agent的会话记录"""
        self.assistant_agent_service.delete_conversation(current_user)
        return success_message("清空辅助agent会话成功")
