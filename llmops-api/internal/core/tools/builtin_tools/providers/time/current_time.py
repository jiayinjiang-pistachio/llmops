#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/24 10:51
@Author         : jiayinkong@163.com
@File           : current_time.py
@Description    : 
"""
from langchain_core.tools import BaseTool


class CurrentTimeTool(BaseTool):
    """一个用于获取当前时间的工具"""
    name = "current_time"
    description = "一个用于获取当前时间的工具"


def current_time(**kwargs) -> BaseTool:
    """返回获取当前时间的LangChain工具"""
    return CurrentTimeTool()
