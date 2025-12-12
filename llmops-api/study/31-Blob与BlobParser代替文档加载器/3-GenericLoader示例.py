#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/12 18:43
@Author         : jiayinkong@163.com
@File           : 3-GenericLoader示例.py
@Description    : 
"""
from langchain_community.document_loaders.generic import GenericLoader

loader = GenericLoader.from_filesystem(".", glob="*.txt", show_progress=True)

for idx, doc in enumerate(loader.lazy_load()):
    print(f"{idx}: {doc.metadata['source']}")
