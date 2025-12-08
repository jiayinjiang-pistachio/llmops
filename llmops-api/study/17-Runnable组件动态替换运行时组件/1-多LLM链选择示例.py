#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/8 16:53
@Author         : jiayinkong@163.com
@File           : 1-多LLM链选择示例.py
@Description    : 
"""
import os

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import ConfigurableField
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1. 创建prompt提示模板并设置默认大语言模型
prompt = ChatPromptTemplate.from_template("{query}")
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
).configurable_alternatives(
    ConfigurableField(id="llm"),
    default_key="gpt-3.5",
    gpt4=ChatOpenAI(
        model="gpt-4",
        api_key=os.getenv("GPTSAPI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE")
    )
)

# 2. 构建链应用
chain = prompt | llm | StrOutputParser()

# 调用链并传递配置信息，并切换到文心一言或者gpt4模型
content = chain.invoke(
    {"query": "你好，你是什么模型呢？"},
    config={"configurable": {"llm": "gpt4"}}
)
print(content)
