#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/6 11:20
@Author         : jiayinkong@163.com
@File           : 1-对话消息组件基础.py
@Description    : 
"""
from langchain_core.chat_history import InMemoryChatMessageHistory

chat_history = InMemoryChatMessageHistory()
chat_history.add_user_message("你好，我是慕小课，你是？")
chat_history.add_ai_message("你好，我是ChatGPT，有什么可以帮到你的？")
print(chat_history)
