#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/2 14:30
@Author         : jiayinkong@163.com
@File           : 2-LCEL表达式简化版本.py
@Description    : 
"""
import os

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1. 构建组件
prompt = ChatPromptTemplate.from_template("{query}")
llm = ChatOpenAI(
    model="gpt-4",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
)
parser = StrOutputParser()

# 2. 创建链
chain = prompt | llm | parser

# 3. 调用链
print(chain.invoke({"query": "请讲一个程序员的冷笑话"}))
