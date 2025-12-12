#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/11 15:48
@Author         : jiayinkong@163.com
@File           : Document与TextLoader.py
@Description    : 
"""
from langchain_community.document_loaders import TextLoader

# 构建加载器
loader = TextLoader(
    file_path="./电商产品数据.txt",
    encoding="utf-8",
)

# 加载数据
documents = loader.load()
print(len(documents))
