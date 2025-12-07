#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/7 17:24
@Author         : jiayinkong@163.com
@File           : 1-实体记忆组件示例.py
@Description    : 
"""
import os

import dotenv
from langchain.chains.conversation.base import ConversationChain
from langchain.memory import ConversationEntityMemory
from langchain.memory.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

chain = ConversationChain(
    llm=llm,
    prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
    memory=ConversationEntityMemory(llm=llm),
)

print(chain.invoke({"input": "你好，我是慕小课，我最近在学习LangChain"}))
print(chain.invoke({"input": "我最喜欢的编程语言是 Python"}))
print(chain.invoke({"input": "我住在广州"}))

# 查询实体中的对话
res = chain.memory.entity_store.store
print(res)
