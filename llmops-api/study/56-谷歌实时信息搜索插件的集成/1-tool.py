#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/17 15:58
@Author         : jiayinkong@163.com
@File           : 1-tool.py
@Description    : 
"""

import dotenv
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.pydantic_v1 import BaseModel, Field

dotenv.load_dotenv()


class GoogleArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")


google_serper = GoogleSerperRun(
    name="google_serper_tool",
    description=(
        "一个低成本的谷歌搜索API。"
        "当你需要回答有关时事问题时，可以调用该工具。"
        "该工具的输入是搜索查询语句。"
    ),
    args_schema=GoogleArgsSchema,
    api_wrapper=GoogleSerperAPIWrapper(),
)

print(google_serper.invoke("马拉松的世界纪录是多少？"))
