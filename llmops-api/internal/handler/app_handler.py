#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/16 09:21
@Author         : jiayinkong@163.com
@File           : app_handler.py
@Description    : 
"""
from dataclasses import dataclass
from uuid import UUID

from flask_login import current_user, login_required
from injector import inject

from internal.schema import CreateAppReq, GetAppResp
from internal.service import AppService
# from internal.task.demo_task import demo_task
from pkg.response import validate_error_json, success_json


@inject
@dataclass
class AppHandler:
    """应用控制器"""
    app_service: AppService

    @login_required
    def create_app(self):
        """调用服务创建新的app记录"""
        req = CreateAppReq()
        if not req.validate():
            return validate_error_json(req.errors)

        app = self.app_service.create_app(req, current_user)

        return success_json({"id": app.id})

    @login_required
    def get_app(self, app_id: UUID):
        """获取指定的应用基础信息"""
        app = self.app_service.get_app(app_id, current_user)
        resp = GetAppResp()

        return success_json(resp.dump(app))

    @login_required
    def get_draft_app_cconfig(self, app_id: UUID):
        """获取草稿配置信息"""
        draft_config = self.app_service.get_draft_app_config(app_id, current_user)

        return success_json(draft_config)

    def ping(self):
        pass
