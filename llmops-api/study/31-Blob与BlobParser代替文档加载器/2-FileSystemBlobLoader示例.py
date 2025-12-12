#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/12 18:39
@Author         : jiayinkong@163.com
@File           : 2-FileSystemBlobLoader示例.py
@Description    : 
"""
from langchain_community.document_loaders import FileSystemBlobLoader

loader = FileSystemBlobLoader(".", show_progress=True)

for blob in loader.yield_blobs():
    print(blob.as_string())
