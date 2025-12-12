#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/12 20:42
@Author         : jiayinkong@163.com
@File           : 4-分割中英文场景示例.py
@Description    : 
"""
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

loader = UnstructuredMarkdownLoader("./项目API资料.md")

documents = loader.load()

separators = [
    "\n\n",
    "\n",
    "。|！|？",
    "\.\s|\!\s|\?\s",  # 英文标点符号后面通常需要加空格
    "；|;\s",
    "，|,\s",
    " ",
    ""
]
text_spliter = RecursiveCharacterTextSplitter(
    separators=separators,
    chunk_size=500,
    chunk_overlap=50,
    add_start_index=True,
    is_separator_regex=True,
)

chunks = text_spliter.split_documents(documents)
for chunk in chunks:
    print(f"块大小: {len(chunk.page_content)}, 元数据: {chunk.metadata}")

print(chunks[2].page_content)
