#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/13 11:32
@Author         : jiayinkong@163.com
@File           : 1-自定义分割器示例.py
@Description    : 
"""
from typing import List

import jieba.analyse
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_text_splitters import TextSplitter


class CustomTextSplitter(TextSplitter):
    def __init__(self, seperator: str, top_k: int = 10, **kwargs):
        """构造函数，传递分割器还有需要提取的关键词数，默认为10"""
        super().__init__(**kwargs)
        self._seperator = seperator
        self._top_k = top_k

    def split_text(self, text: str) -> List[str]:
        """传入对应的文本进行分割并提取分割数据的关键词，组成文档列表返回"""
        # 1. 根据传递的分隔符分割传入的文本
        split_texts = text.split(self._seperator)

        # 2. 提取分割出来的每一段文本的关键词，数量为self._top_k
        text_keywords = []
        for split_text in split_texts:
            text_keywords.append(jieba.analyse.extract_tags(split_text, self._top_k))

        # 3. 将关键词使用逗号进行拼接组成字符串列表并返回
        return [','.join(keywords) for keywords in text_keywords]


# 1. 创建加载器与分割器
loader = UnstructuredFileLoader("./科幻短篇.txt")
text_splitter = CustomTextSplitter("\n\n", 10)

# 2. 加载文档分割器
documents = loader.load()
chunks = text_splitter.split_documents(documents)

# 3.循环遍历文档信息
for chunk in chunks:
    print(chunk.page_content)
