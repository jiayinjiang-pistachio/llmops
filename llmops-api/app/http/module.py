#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/18 21:59
@Author         : jiayinkong@163.com
@File           : module.py
@Description    : 
"""
from flask_migrate import Migrate
from injector import Module, Binder

from internal.extension.database_extension import db
from internal.extension.migrate_extension import migrate
from pkg.sqlalchemy import SQLAlchemy


class ExtensionModule(Module):
    """扩展模块的依赖注入"""

    def configure(self, binder: Binder) -> None:
        # 把 db 绑定到 SQLAlchemy
        binder.bind(SQLAlchemy, to=db)
        binder.bind(Migrate, to=migrate)
