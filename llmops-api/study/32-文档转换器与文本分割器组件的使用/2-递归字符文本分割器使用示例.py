#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/12 19:56
@Author         : jiayinkong@163.com
@File           : 2-递归字符文本分割器使用示例.py
@Description    : 
"""
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

loader = UnstructuredMarkdownLoader("./项目API资料.md")
documents = loader.load()

# 创建文本分割器
text_spliter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    add_start_index=True
)
chunks = text_spliter.split_documents(documents)

for chunk in chunks:
    print(f"块的大小：{len(chunk.page_content)}，块元数据：{chunk.metadata}")
