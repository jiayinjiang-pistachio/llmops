#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/12 12:25
@Author         : jiayinkong@163.com
@File           : 4-UnstructuredFileLoader示例.py
@Description    : 
"""
from langchain_community.document_loaders import UnstructuredFileLoader

loader = UnstructuredFileLoader("./员工考勤表.xlsx")
documents = loader.load()
print(documents)
print(len(documents))
print(documents[0].metadata)
