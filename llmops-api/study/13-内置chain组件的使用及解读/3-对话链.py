# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/7 20:57
@Author         : jiayinkong@163.com
@File           : 3-对话链.py
@Description    : 
"""
import os

import dotenv
from langchain.chains.conversation.base import ConversationChain
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)
chain = ConversationChain(llm=llm)

content = chain.invoke({"input": "你好，我叫幕小课，我喜欢篮球和游泳，你喜欢什么？"})
print(content)

content = chain.invoke({"input": "根据上下文信息，请统计我的爱好有什么？"})
print(content)
