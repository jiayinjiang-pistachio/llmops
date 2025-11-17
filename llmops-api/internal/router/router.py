#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/16 09:27
@Author         : jiayinkong@163.com
@File           : router.py
@Description    : 
"""
from dataclasses import dataclass

from flask import Blueprint  # 修正：从 flask 直接导入 Blueprint
from flask import Flask
from injector import inject

from internal.handler import AppHandler


@inject
@dataclass
class Router:
    """路由"""
    app_handler: AppHandler

    def register_router(self, app: Flask):
        """注册路由"""
        # 1. 创建蓝图
        print("=" * 20, __name__, "=" * 20)
        bp = Blueprint("llmops", import_name=__name__, url_prefix="")

        # 2. 将url与对应的控制器方法绑定
        bp.add_url_rule("/ping", view_func=self.app_handler.ping)
        bp.add_url_rule("/app/completion", methods=["POST"], view_func=self.app_handler.completion)

        # 3. 在应用上去注册蓝图
        app.register_blueprint(bp)
