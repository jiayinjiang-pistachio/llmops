#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/7 14:45
@Author         : jiayinkong@163.com
@File           : 1-缓冲窗口记忆示例.py
@Description    : 
"""
import os
from operator import itemgetter

import dotenv
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1. 创建提示模板&记忆
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是OpenAI开发的聊天机器人，请根据对应的上下文回复用户问题"),
        MessagesPlaceholder("history"),
        ("human", "{query}")
    ]
)
memory = ConversationBufferWindowMemory(
    k=2,
    input_key="query",
    return_messages=True
)

# 2. 创建大语言模型
llm = ChatOpenAI(
    model="gpt-4",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
)

# 3. 构建链应用
chain = RunnablePassthrough.assign(
    history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
) | prompt | llm | StrOutputParser()

# 4. 死循环构建对话命令行
while True:
    query = input("Human: ")
    if query == "q":
        exit(0)

    chain_input = {"query": query}

    response = chain.stream(chain_input)
    print("AI: ", flush=True, end="")
    output = ""
    for chunk in response:
        output += chunk
        print(chunk, flush=True, end="")
    memory.save_context(chain_input, {"output": output})
    print("")
    print("history: ", memory.load_memory_variables({}))
