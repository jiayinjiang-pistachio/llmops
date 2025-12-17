#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/17 09:54
@Author         : jiayinkong@163.com
@File           : DuckDuckGo搜索.py
@Description    : 
"""
from langchain_community.tools import DuckDuckGoSearchRun

search = DuckDuckGoSearchRun(description="xxx")

print(search.invoke("LangChain的最新版本是什么？"))
print(search.name)
print(search.description)
print(search.args)
print(search.return_direct)
