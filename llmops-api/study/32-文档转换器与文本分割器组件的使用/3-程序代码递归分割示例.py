#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/12 20:29
@Author         : jiayinkong@163.com
@File           : 3-程序代码递归分割示例.py
@Description    : 
"""
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language

loader = UnstructuredFileLoader("./demo.py")
documents = loader.load()

text_spliter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=500,
    chunk_overlap=50,
    add_start_index=True,
)
chunks = text_spliter.split_documents(documents)

for chunk in chunks:
    print(f"块的大小：{len(chunk.page_content)}，块元数据：{chunk.metadata}")
