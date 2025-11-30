#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/30 15:04
@Author         : jiayinkong@163.com
@File           : 3-Model流式输出.py
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
response = llm.stream(prompt.invoke({"query": "你能简单介绍下LLM和LLMOps吗？"}))

for chunk in response:
    print(chunk.content, flush=True, end="")
