#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/12 12:50
@Author         : jiayinkong@163.com
@File           : 1-Blob解析器示例.py
@Description    : 
"""
from typing import Iterator

from langchain_core.document_loaders import BaseBlobParser, Blob
from langchain_core.documents import Document


class CustomParser(BaseBlobParser):
    """自定义解析器，用于将传入的文本二进制数据的每一行解析成Document组件"""

    def lazy_parse(self, blob: Blob) -> Iterator[Document]:
        with blob.as_bytes_io() as f:
            line_number = 0
            for line in f:
                yield Document(
                    page_content=line,
                    metadata={
                        "source": blob.source,
                        "line_number": line_number,
                    }
                )
                line_number += 1


# 1. 加载blob二进制数据
blob = Blob.from_path("喵喵.txt")
# 2. 解析二进制数据
parser = CustomParser()
documents = list(parser.parse(blob))

print(documents)
print(len(documents))
print(documents[0].metadata)
