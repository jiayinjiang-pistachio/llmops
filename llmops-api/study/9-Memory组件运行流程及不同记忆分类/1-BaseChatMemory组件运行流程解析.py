#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/6 19:02
@Author         : jiayinkong@163.com
@File           : 1-BaseChatMemory组件运行流程解析.py
@Description    : 
"""
from langchain.memory.chat_memory import BaseChatMemory
from langchain_core.memory import BaseMemory

BaseMemory
BaseChatMemory

memory = BaseChatMemory(
    input_key="query",
    output_key="output",
    return_messages=True,
    # chat_history 假设
)

memory_variable = memory.load_memory_variables({})

# content = chain.invoke({"query": "你好，我是慕小课，你是谁？", "chat_history": memory_variable.get("chat_history")})
# memory.save_context({"query": "你好，我是慕小课，你是谁？"}, {"output": "你好我是ChtGPT，有什么可以帮到你的？"})
