#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/7 20:41
@Author         : jiayinkong@163.com
@File           : 2-LCEL文档填充链.py
@Description    : 
"""
import os

import dotenv
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个强大的聊天机器人，能根据用户提供的上下文来回复用户的问题。\n\n<context>{context}</context>"),
    ("human", "{query}")
])
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)
# 创建链应用
chain = create_stuff_documents_chain(prompt=prompt, llm=llm)

# 文档列表
documents = [
    Document(page_content="小明喜欢绿色，不喜欢黄色"),
    Document(page_content="小王喜欢粉色，也有一点喜欢红色"),
    Document(page_content="小泽喜欢蓝色，但更喜欢青色")
]

# 调用链
content = chain.invoke({"query": "请帮我统计下大家都喜欢什么颜色", "context": documents})
print(content)
