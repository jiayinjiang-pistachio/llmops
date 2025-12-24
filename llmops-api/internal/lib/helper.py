#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/23 19:09
@Author         : jiayinkong@163.com
@File           : helper.py
@Description    : 
"""
import importlib
from typing import Any


def dynamic_import(module_name, symbol_name) -> Any:
    """动态导入特定模块下的特定功能"""
    module = importlib.import_module(module_name)
    return getattr(module, symbol_name)
