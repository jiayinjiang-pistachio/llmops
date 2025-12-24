#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/24 10:59
@Author         : jiayinkong@163.com
@File           : duckduckgo_search.py
@Description    : 
"""
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import BaseTool


def duckduckgo_search(**kwargs) -> BaseTool:
    """返回DuckDuckGo搜索工具"""
    return DuckDuckGoSearchRun(
        description="一个注重隐私的搜索工具",

    )
