#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/12 11:13
@Author         : jiayinkong@163.com
@File           : 1-Markdown文档加载器使用示例.py
@Description    : 
"""
from langchain_community.document_loaders import UnstructuredMarkdownLoader

loader = UnstructuredMarkdownLoader(
    "./项目API资料.md"
)

documents = loader.load()
print(documents)
print(len(documents))
print(documents[0].metadata)
print(documents[0].page_content)
