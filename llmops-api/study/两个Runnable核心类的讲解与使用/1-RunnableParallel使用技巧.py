#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/2 14:48
@Author         : jiayinkong@163.com
@File           : 1-RunnableParallel使用技巧.py
@Description    : 
"""
import os

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1. 编排prompt
joke_prompt = ChatPromptTemplate.from_template("请讲一个关于{subject}的冷笑话，尽可能短一些")
poem_prompt = ChatPromptTemplate.from_template("请写一篇关于{subject}的诗")

# 2. 创建大语言模型
llm = ChatOpenAI(
    model="gpt-4",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
)

# 3. 创建输出解析器
parser = StrOutputParser()

# 4. 编排链
joke_chain = joke_prompt | llm | parser
poem_chain = poem_prompt | llm | parser

# 5. 创建并行链
map_chain = RunnableParallel({
    "joke": joke_chain,
    "poem": poem_chain,
})

print(map_chain.invoke({"subject": "程序员"}))
