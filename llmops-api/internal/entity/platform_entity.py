#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/2/20 11:11
@Author         : jiayinkong@163.com
@File           : platform_entity.py
@Description    : 
"""
from enum import Enum


class WechatConfigStatus(str, Enum):
    """微信配置状态"""
    CONFIGURED = "configured"
    UNCONFIGURED = "unconfigured"
