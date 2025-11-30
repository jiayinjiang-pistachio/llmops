#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/30 14:07
@Author         : jiayinkong@163.com
@File           : 1-LLM与ChatModel使用技巧.py
@Description    : 
"""
import os
from datetime import datetime

import dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1. 编排 prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是Open AI开发的聊天机器人，请回答用户的问题，现在时间是{now}"),
    ("human", "{query}")
]).partial(now=datetime.now())

# 创建大语言模型
llm = ChatOpenAI(
    model="gpt-4",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
)
ai_message = llm.invoke(prompt.invoke({"query": "现在是几点，请讲一个程序员的冷笑话"}))
print(ai_message.content)
print(ai_message.type)
print(ai_message.response_metadata)
