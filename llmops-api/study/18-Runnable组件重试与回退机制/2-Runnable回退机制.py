#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/8 17:33
@Author         : jiayinkong@163.com
@File           : 2-Runnable回退机制.py
@Description    : 
"""
import os

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()
# 1. 构建prompt与LLM，并将model切换为gpt-3.5-turbo-18k引发出错
prompt = ChatPromptTemplate.from_template("{query}")
llm = ChatOpenAI(
    model="gpt-3.5-turbo-18k",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
).with_fallbacks([
    ChatOpenAI(
        model="gpt-4o",
        api_key=os.getenv("GPTSAPI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE")
    )
])

# 2. 构建链应用
chain = prompt | llm | StrOutputParser()

# 3. 调用链并输出结果
content = chain.invoke({"query": "你好，你是？"})
print(content)
