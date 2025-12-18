#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/18 11:37
@Author         : jiayinkong@163.com
@File           : 2-回退处理策略.py
@Description    : 
"""
import os

import dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()


@tool
def complex_tool(int_arg: int, float_arg: float, dict_arg: dict) -> int:
    """使用复杂工具进行复杂计算操作"""
    return int_arg * float_arg


# 创建大语言模型并绑定工具
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
    temperature=0,
).bind_tools([complex_tool])
better_llm = ChatOpenAI(
    model="gpt-4o",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
    temperature=0,
).bind_tools([complex_tool])

# 创建链并执行工具
better_chain = better_llm | (lambda msg: msg.tool_calls[0]["args"]) | complex_tool
chain = (llm | (lambda msg: msg.tool_calls[0]["args"]) | complex_tool).with_fallbacks([better_chain])

# 3.调用链
print(chain.invoke("使用复杂工具，对应参数为5和2.1，不要忘记了dict_arg参数"))
