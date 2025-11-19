#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/18 21:36
@Author         : jiayinkong@163.com
@File           : default_config.py
@Description    : 
"""
DEFAULT_CONFIG = {
    # 关闭wtf的csrf保护-默认配置
    "WTF_CSRF_ENABLED": "False",

    # SQLALCHEMY 默认配置
    "SQLALCHEMY_DATABASE_URI": "",
    # 连接池大小
    "SQLALCHEMY_POOL_SIZE": 30,
    # 每个连接最长时间
    "SQLALCHEMY_POOL_RECYCLE": 3600,
    "SQLALCHEMY_ECHO": "True"
}
