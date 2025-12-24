#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/24 11:43
@Author         : jiayinkong@163.com
@File           : wikipedia_search.py
@Description    : 
"""
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import BaseTool


def wikipedia_search(**kwargs) -> BaseTool:
    """返回危机百科搜索工具"""
    return WikipediaQueryRun(
        api_wrapper=WikipediaAPIWrapper()
    )
