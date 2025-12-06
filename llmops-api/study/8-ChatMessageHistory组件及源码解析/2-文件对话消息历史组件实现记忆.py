#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/6 16:02
@Author         : jiayinkong@163.com
@File           : 2-文件对话消息历史组件实现记忆.py
@Description    :
"""
import os

import dotenv
from langchain_community.chat_message_histories import FileChatMessageHistory
from openai import OpenAI

dotenv.load_dotenv()

# 1. 创建客户端&记忆
client = OpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("GPTSAPI_API_KEY"),
)
chat_history = FileChatMessageHistory("./memory.txt")

# 2. 循环对话
while True:
    # 3. 获取用户的输入
    query = input("Human: ")

    # 4. 检测用户是否退出输入
    if query == "q":
        exit(0)

    # 5. 发起聊天对话
    print("AI: ", flush=True, end="")
    system_prompt = (
        "你是OpenAI开发的ChatGPT聊天机器人，可以根据响应的上下文回复用户信息，上下文里存放的是人类与你对话的信息列表\n\n"
        f"<context>{chat_history}</context>\n\n"
    )
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        stream=False,
    )
    ai_content = response.choices[0].message.content
    print(ai_content)
    chat_history.add_user_message(query)
    chat_history.add_ai_message(ai_content)
    print("")
