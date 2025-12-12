#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/12 12:28
@Author         : jiayinkong@163.com
@File           : 1-自定义文档加载器使用示例.py
@Description    : 
"""
from typing import Iterator, AsyncIterator

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document


class CustomLoader(BaseLoader):
    def __init__(self, file_path: str):
        self.file_path = file_path

    """自定义文档加载器，将文本文件的每一行解析成Document"""

    def lazy_load(self) -> Iterator[Document]:
        # 1. 读取对应文件
        with open(self.file_path, encoding='utf-8') as f:
            line_num = 0
            # 2. 提取文件的每一行
            for line in f:
                # 3. 把每一行生成对应的Document对象
                yield Document(
                    page_content=line,
                    metadata={
                        "source": self.file_path,
                        "line_num": line_num
                    }
                )
                line_num += 1

    async def alazy_load(self) -> AsyncIterator[Document]:
        import aiofiles
        async with aiofiles.open(self.file_path, encoding='utf-8') as f:
            line_num = 0
            # 2. 提取文件的每一行
            async for line in f:
                # 3. 把每一行生成对应的Document对象
                yield Document(
                    page_content=line,
                    metadata={
                        "source": self.file_path,
                        "line_num": line_num
                    }
                )
                line_num += 1


loader = CustomLoader("../31-Blob与BlobParser代替文档加载器/喵喵.txt")
documents = loader.load()
print(documents)
print(len(documents))
print(documents[0].metadata)
