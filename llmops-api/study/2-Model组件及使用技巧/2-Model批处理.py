#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/30 14:58
@Author         : jiayinkong@163.com
@File           : 2-Model批处理.py
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
ai_messages = llm.batch([
    prompt.invoke({"query": "你好，你是？"}),
    prompt.invoke({"query": "请讲一个关于程序员的冷笑话"}),
])

for message in ai_messages:
    print(message.content)
    print("=" * 20)
