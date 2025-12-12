#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/12 12:14
@Author         : jiayinkong@163.com
@File           : 3-URL网页加载器.py
@Description    : 
"""
from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader(["https://www.espn.com/", "https://google.com"])
documents = loader.load()
print(documents)
print(len(documents))
print(documents[0].page_content)
