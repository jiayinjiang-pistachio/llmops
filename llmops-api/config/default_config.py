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
    "SQLALCHEMY_ECHO": "True",

    # weaviate默认配置
    "WEAVIATE_HTTP_HOST": "localhost",
    "WEAVIATE_HTTP_PORT": 8080,
    "WEAVIATE_GRPC_HOST": "localhost",
    "WEAVIATE_GRPC_PORT": 50051,
    "WEAVIATE_API_KEY": "",

    "REDIS_HOST": "localhost",
    "REDIS_PORT": 6379,
    "REDIS_USERNAME": "",
    "REDIS_PASSWORD": "",
    "REDIS_DB": 0,
    "REDIS_USE_SSL": "False",

    # Celery默认配置
    "CELERY_BROKER_DB": 1,
    "CELERY_RESULT_BACKEND_DB": 1,
    "CELERY_TASK_IGNORE_RESULT": "False",
    "CELERY_RESULT_EXPIRES": 3600,
    "CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP": "True",

    # 辅助agent智能体应用id
    "ASSISTANT_AGENT_ID": "6463d298-8f66-4447-96cf-cb6d51b6abb8"
}
