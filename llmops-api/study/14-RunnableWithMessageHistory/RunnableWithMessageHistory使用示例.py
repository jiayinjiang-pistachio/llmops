#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/8 10:04
@Author         : jiayinkong@163.com
@File           : RunnableWithMessageHistory使用示例.py
@Description    : 
"""
import os

import dotenv
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = FileChatMessageHistory(f"./chat_history_{session_id}.txt")
    return store[session_id]


# 1. 构建提示模板与大语言模型
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个强大的聊天机器人，请根据用户的需求回复问题"),
    MessagesPlaceholder("history"),
    ("human", "{query}")
])
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

# 3. 构建链
chain = prompt | llm | StrOutputParser()

# 4. 包装链
with_message_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="query",
    history_messages_key="history",
)

while True:
    # 获取用户输入
    query = input("Human: ")
    if query == "q":
        exit(0)

    # 运行链并配置信息
    response = with_message_chain.stream(
        {
            "query": query,
        },
        config={"configurable": {"session_id": "muxiaoke"}}
    )

    print("AI: ", flush=True, end="")
    for chunk in response:
        print(chunk, flush=True, end="")
    print("")
