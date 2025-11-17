#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/17 21:21
@Author         : jiayinkong@163.com
@File           : config.py
@Description    : 
"""


class Config:
    def __init__(self):
        # 关闭wtf的csrf保护
        self.WTF_CSRF_ENABLED = False
