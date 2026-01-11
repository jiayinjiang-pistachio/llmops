#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/18 21:59
@Author         : jiayinkong@163.com
@File           : module.py
@Description    : 
"""
from flask_login import LoginManager
from flask_migrate import Migrate
from injector import Module, Binder, Injector
from redis import Redis

from internal.extension.database_extension import db
from internal.extension.login_extension import login_manager
from internal.extension.migrate_extension import migrate
from internal.extension.redis_extension import redis_client
from pkg.sqlalchemy import SQLAlchemy


class ExtensionModule(Module):
    """扩展模块的依赖注入"""

    def configure(self, binder: Binder) -> None:
        # 把 SQLAlchemy 绑定到 db
        binder.bind(SQLAlchemy, to=db)
        binder.bind(Migrate, to=migrate)
        binder.bind(Redis, to=redis_client)
        binder.bind(LoginManager, to=login_manager)


# 传入 [ExtensionModule] 表示使用这个模块的配置
injector = Injector([ExtensionModule])
