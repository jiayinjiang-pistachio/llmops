#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/19 22:00
@Author         : jiayinkong@163.com
@File           : app_service.py
@Description    : 
"""
from dataclasses import dataclass
from uuid import UUID

from injector import inject

from internal.entity.app_entity import AppStatus, AppConfigType, DEFAULT_APP_CONFIG
from internal.model import App, Account, AppConfigVersion
from internal.schema import CreateAppReq
from pkg.sqlalchemy import SQLAlchemy
from .base_service import BaseService
from ..exception import NotFoundException, ForbiddenException


@inject
@dataclass
class AppService(BaseService):
    """应用服务逻辑"""
    db: SQLAlchemy

    def create_app(self, req: CreateAppReq, account: Account) -> App:
        """创建Agent应用服务"""
        # 1. 开启数据库自动提交上下文
        with self.db.auto_commit():
            # 2. 创建应用记录，并刷新记录，从而可以拿到应用id
            app = App(
                account_id=account.id,
                name=req.name.data,
                icon=req.icon.data,
                description=req.description.data or "",
                status=AppStatus.DRAFT,
            )
            self.db.session.add(app)
            self.db.session.flush()  # 只有刷新了下方新增草稿记录时才能拿到app_id

            # 3. 添加草稿记录
            app_config_version = AppConfigVersion(
                app_id=app.id,
                version=0,
                config_type=AppConfigType.DRAFT,
                **DEFAULT_APP_CONFIG,
            )
            self.db.session.add(app_config_version)
            self.db.session.flush()

            # 4. 为应用添加草稿配置id
            app.draft_app_config_id = app_config_version.id

        # 5. 返回创建的应用记录
        return app

    def get_app(self, app_id: UUID, account: Account) -> App:
        """根据传递的id获取应用的基础信息"""
        # 1. 查询数据库获取应用基础信息
        app = self.get(App, app_id)

        # 2. 判断应用是否存在
        if not app:
            raise NotFoundException("该应用不存在，请核实后重试")

        # 3. 判断当前账号是否有权限访问该应用
        if app.account_id != account.id:
            raise ForbiddenException("当前账号无权限访问该应用，请核实后重试")

        return app

    def update_app(self, id: UUID) -> App:
        with self.db.auto_commit():
            app = self.get_app(id)
            app.name = "慕课网机器人"
        return app

    def delete_app(self, id: UUID) -> App:
        with self.db.auto_commit():
            app = self.get_app(id)
            self.db.session.delete(app)
        return app
