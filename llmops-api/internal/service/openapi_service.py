#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/19 19:17
@Author         : jiayinkong@163.com
@File           : openapi_service.py
@Description    : 
"""
from dataclasses import dataclass

from injector import inject


@inject
@dataclass
class OpenapiService:
    """开放API服务器"""
