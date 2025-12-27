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
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool

from internal.lib.helper import add_attributes


class WikipediaQueryInput(BaseModel):
    """维基百科查询工具的输入内容"""
    query: str = Field(description="这是一个要在维基百科上查找的查询词")


@add_attributes("args_schema", WikipediaQueryInput)
def wikipedia_search(**kwargs) -> BaseTool:
    """返回维基百科搜索工具"""
    return WikipediaQueryRun(
        api_wrapper=WikipediaAPIWrapper(),
        args_schema=WikipediaQueryInput
    )
