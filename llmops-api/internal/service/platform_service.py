#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/2/20 11:36
@Author         : jiayinkong@163.com
@File           : platform_service.py
@Description    : 
"""
from dataclasses import dataclass
from uuid import UUID

from injector import inject

from pkg.sqlalchemy import SQLAlchemy
from .app_service import AppService
from .base_service import BaseService
from ..entity.app_entity import AppStatus
from ..entity.platform_entity import WechatConfigStatus
from ..model import Account, WechatConfig
from ..schema.platform_schema import UpdateWechatConfigReq


@inject
@dataclass
class PlatformService(BaseService):
    """第三方平台服务"""
    db: SQLAlchemy
    app_service: AppService

    def get_wechat_config(self, app_id: UUID, account: Account) -> WechatConfig:
        """根据传递的应用id+账号获取微信发布配置"""
        # 1. 获取应用信息并校验权限
        app = self.app_service.get_app(app_id, account)

        # 2. 获取应用的微信配置信息
        return app.wechat_config

    def update_wechat_config(self, app_id: UUID, req: UpdateWechatConfigReq, account: Account) -> WechatConfig:
        """根据传递的应用id+账号+配置信息更新应用的微信发布配置"""
        # 1. 获取应用信息并校验权限
        app = self.app_service.get_app(app_id, account)

        # 2. 根据传递的请求判断app_id/app_secret/token是否齐全并计算状态
        status = WechatConfigStatus.UNCONFIGURED

        if req.wechat_app_id.data and req.wechat_app_secret.data and req.wechat_token.data:
            status = WechatConfigStatus.CONFIGURED

        # 3. 根据应用的发布状态修正状态数据
        if app.status == AppStatus.DRAFT and status == WechatConfigStatus.CONFIGURED:
            status = WechatConfigStatus.UNCONFIGURED

        # 4. 更新应用微信配置信息
        wechat_config = app.wechat_config
        self.update(wechat_config, **{
            "wechat_app_id": req.wechat_app_id.data,
            "wechat_app_secret": req.wechat_app_secret.data,
            "wechat_token": req.wechat_token.data,
            "status": status
        })

        return wechat_config
