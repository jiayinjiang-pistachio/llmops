#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/19 19:06
@Author         : jiayinkong@163.com
@File           : openapi_handler.py
@Description    : 
"""
from dataclasses import dataclass

from injector import inject


@inject
@dataclass
class OpenapiHandler:
    """开放API处理器"""

    def chat(self):
        pass
