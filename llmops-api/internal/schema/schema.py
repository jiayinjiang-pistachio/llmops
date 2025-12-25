#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/25 20:21
@Author         : jiayinkong@163.com
@File           : schema.py
@Description    : 
"""
from wtforms import Field


class ListField(Field):
    """自定义list字段，用于存储列表型数据"""
    data: list = None

    def process_formdata(self, valuelist):
        if valuelist is not None and isinstance(valuelist, list):
            self.data = valuelist

    def _value(self):
        return self.data if self.data else []
