#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/31 13:06
@Author         : jiayinkong@163.com
@File           : demo_task.py
@Description    : 
"""
import logging
import time
from uuid import UUID

from celery import shared_task
from flask import current_app


@shared_task
def demo_task(id: UUID) -> str:
    """测试异步任务"""
    logging.info("睡眠5秒")
    time.sleep(5)
    logging.info(f"id的值:{id}")
    logging.info(f"配置信息:{current_app.config}")
    return "鹅百创"
