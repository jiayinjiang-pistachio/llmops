#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/17 21:21
@Author         : jiayinkong@163.com
@File           : config.py
@Description    : 
"""
import os
from typing import Any

from config.default_config import DEFAULT_CONFIG


def _get_env(key) -> Any:
    # 从环境变量中获取配置项，如果找不到就返回默认值
    return os.getenv(key, DEFAULT_CONFIG.get(key))


def _get_bool_env(key) -> bool:
    value: str = os.getenv(key)
    return value.lower() == "true" if value is not None else False


class Config:
    def __init__(self):
        # 关闭wtf的csrf保护
        self.WTF_CSRF_ENABLED = _get_bool_env("WTF_CSRF_ENABLED")

        # 配置数据库配置
        self.SQLALCHEMY_DATABASE_URI = _get_env("SQLALCHEMY_DATABASE_URI")
        self.SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_size": int(_get_env("SQLALCHEMY_POOL_SIZE")),
            "pool_recycle": int(_get_env("SQLALCHEMY_POOL_RECYCLE")),
        }
        self.SQLALCHEMY_ECHO = _get_bool_env("SQLALCHEMY_ECHO")

        # redis 数据库配置
        self.REDIS_HOST = _get_env("REDIS_HOST")
        self.REDIS_PORT = _get_env("REDIS_PORT")
        self.REDIS_USERNAME = _get_env("REDIS_USERNAME")
        self.REDIS_PASSWORD = _get_env("REDIS_PASSWORD")
        self.REDIS_DB = _get_env("REDIS_DB")
        self.REDIS_USE_SSL = _get_bool_env("REDIS_USE_SSL")
