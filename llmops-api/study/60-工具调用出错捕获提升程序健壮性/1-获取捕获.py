#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/18 11:24
@Author         : jiayinkong@163.com
@File           : 1-获取捕获.py
@Description    : 
"""
import os
from typing import Any

import dotenv
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()


@tool
def complex_tool(int_arg: int, float_arg: float, dict_arg: dict) -> int:
    """使用复杂工具进行复杂计算操作"""
    return int_arg * float_arg


def try_except_tool(tool_args: dict, config: RunnableConfig) -> Any:
    try:
        complex_tool.invoke(tool_args, config=config)
    except Exception as e:
        return f"工具调用传递的参数是：\n\n{tool_args}\n\n引发以下错误：\n\n{type(e)}: {e}"


# 1. 创建大语言模型并绑定
llm = ChatOpenAI(
    model="gpt-4",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
    temperature=0,
)
llm_with_tools = llm.bind_tools([complex_tool])

# 2. 创建并执行工具
chain = llm_with_tools | (lambda msg: msg.tool_calls[0]["args"]) | try_except_tool

# 3. 调用链
print(chain.invoke("使用复杂工具，对应参数为5和2.1"))
