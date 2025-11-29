#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/16 09:49
@Author         : jiayinkong@163.com
@File           : __init__.py.py
@Description    : http 应用
"""
from flask import Flask
from flask_migrate import Migrate

from config import Config
from internal.exception import CustomException
from internal.router import Router
from pkg.response import json, Response, HttpCode
from pkg.sqlalchemy import SQLAlchemy


class Http(Flask):
    """Http服务引擎"""

    def __init__(
            self,
            *args,
            conf: Config,
            db: SQLAlchemy,
            migrate: Migrate,
            router: Router,
            **kwargs
    ):
        # 1. 调用父类构造函数初始化
        super().__init__(*args, **kwargs)

        # 2. 初始化应用配置
        self.config.from_object(conf)

        # 3. 注册绑定异常处理
        self.register_error_handler(Exception, self._register_error_handler)

        # 4. 初始化flask扩展
        db.init_app(self)
        migrate.init_app(self, db, directory="internal/migration")

        # 5. 注册应用路由
        router.register_router(self)

    def _register_error_handler(self, error: Exception):
        # 1. 异常信息是不是自定义的异常，如果是，可以提取 msg、data 等信息
        if isinstance(error, CustomException):
            return json(Response(
                code=error.code,
                message=error.msg,
                data=error.data,
            ))
        # 2. 如果不是自定义异常，则可能是数据库、程序抛出的异常，也可以提取信息，设置为FAIL状态码
        if self.debug:
            raise error
        else:
            return json(Response(
                code=HttpCode.FAIL,
                message=str(error),
                data={},
            ))
