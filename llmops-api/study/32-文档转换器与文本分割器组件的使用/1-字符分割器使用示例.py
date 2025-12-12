#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/12 19:27
@Author         : jiayinkong@163.com
@File           : 1-字符分割器使用示例.py
@Description    : 
"""
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import CharacterTextSplitter

# 1. 加载对应的文档
loader = UnstructuredMarkdownLoader("./项目API资料.md")
documents = loader.load()

# 2. 创建文本分割器
text_spliter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=500,
    chunk_overlap=50,
    add_start_index=True,
)

# 3. 分割文本
chunks = text_spliter.split_documents(documents)

for chunk in chunks:
    print(f"块内容大小：{len(chunk.page_content)}，原数据：{chunk.metadata}")
