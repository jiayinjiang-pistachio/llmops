#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/18 11:49
@Author         : jiayinkong@163.com
@File           : 3-携带错误信息的重试.py
@Description    : 
"""
import os
from typing import Any

import dotenv
from langchain_core.messages import ToolCall, AIMessage, ToolMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()


class CustomToolException(Exception):
    def __init__(self, tool_call: ToolCall, exception: Exception):
        super().__init__()
        self.tool_call = tool_call
        self.exception = exception


def tool_custom_exception(msg: AIMessage, config: RunnableConfig) -> Any:
    try:
        return complex_tool.invoke(msg.tool_calls[0]["args"], config=config)
    except Exception as e:
        raise CustomToolException(msg.tool_calls[0], e)


@tool
def complex_tool(int_arg: int, float_arg: float, dict_arg: dict) -> int:
    """使用复杂工具进行复杂计算操作"""
    return int_arg * float_arg


def exception_to_message(inputs: dict) -> dict:
    exception = inputs.pop("exception")

    messages = [
        AIMessage(content="", tool_calls=[exception.tool_call]),  # 把工具传给AIMessage,工具调用回放
        ToolMessage(tool_call_id=exception.tool_call["id"], content=str(exception.exception)),
        HumanMessage(content="最后一次工具调用引发了异常，请尝试使用更正的参数再次调用该工具，请不要重复犯错")
    ]

    inputs["last_output"] = messages
    return inputs


# 创建prompt
prompt = ChatPromptTemplate.from_messages([
    ("human", "{query}"),
    ("placeholder", "{last_output}")
])

# 创建大语言模型绑定工具
llm = ChatOpenAI(
    model="gpt-4o",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
    temperature=0,
).bind_tools(tools=[complex_tool], tool_choice="complex_tool")

# 创建链并执行工具
chain = prompt | llm | tool_custom_exception
self_correcting_chain = chain.with_fallbacks(
    [exception_to_message | chain],
    exception_key="exception"
)

# 4.调用自我纠正链完成任务
print(self_correcting_chain.invoke({"query": "使用复杂工具，对应参数为5和2.1"}))

# LangChain 自动做的 3 件事（非常关键）
# 第一步：捕获异常对象
# CustomToolException(
#     tool_call=...,
#     exception=...
# )

# 第二步：把异常“注入到输入字典”
# inputs = {
#     "query": "使用复杂工具，对应参数为5和2.1",
#     "exception": <CustomToolException 对象>
# }
# 重点来了：
#
# exception_key="exception" 就是告诉 LangChain：
#
# “异常对象请放在 inputs["exception"] 里”
# ✅ 第三步：把这个 dict 传给 fallback Runnable
# exception_to_messages(inputs)

# 为什么用 pop 而不是 inputs["exception"]
# ✅ 目的一：把异常“消费掉”
#
# 后续还要把 inputs 继续传下去：
# return inputs
#
#
# 如果你不 pop，那么：
#
# inputs 里会残留 "exception"
#
# 下一轮 prompt / chain 不认识这个字段
#
# 会导致 schema 混乱甚至再次异常


# exception_to_messages 在“链路”中的真实角色
#
# 你可以把它理解为一个 异常适配器（Exception Adapter）：
#
# CustomToolException
#         ↓
# exception_to_messages
#         ↓
# AIMessage + ToolMessage + HumanMessage
#         ↓
# 重新送回 LLM

# exception.tool_call 是什么
# {
#     "id": "call_xxx",
#     "name": "complex_tool",
#     "args": {
#         "int_arg": 5,
#         "float_arg": "2.1",   # ← 注意：这里是字符串，埋雷点
#         "dict_arg": {}
#     }
# }

# 为什么要把exception传给ToolMessage
# 把 exception 传给 ToolMessage，不是为了“记录错误”，
# 而是为了“完成一次合法的工具调用闭环”，让模型“看见失败并对齐到具体那一次调用”。
#
#
# 那 ToolMessage 的 content 是干嘛的？
# 正常情况（工具成功）
# ToolMessage(
#     tool_call_id="call_123",
#     content="10"
# )
#
#
# 语义是：
#
# “刚才 id=call_123 的工具调用，执行结果是 10”
#
#
# 异常情况（工具失败）
# ToolMessage(
#     tool_call_id="call_123",
#     content="float_arg 必须是 float"
# )
#
#
# 语义是：
#
# “刚才 id=call_123 的工具调用，失败了，错误信息是这个”
#
# 为什么一定要把 exception 放进 ToolMessage
# 核心原因只有一个：
#
# 让 LLM“知道这次工具调用失败了，并且知道为什么失败”。

# 为什么不用 HumanMessage 传异常？
# 在模型看来是：
#
# “用户说了一句话”
#
# 而不是：
#
# “工具执行失败”
#
# 这会导致模型：
#
# 把错误当作用户意图
#
# 甚至重新规划而不是修正参数

# 为什么需要把tool_call传给AIMessage
# 1.把 tool_call 传给 AIMessage，是为了“重建模型刚才做过的那一次工具决策”，
# 否则模型会认为：它从来没有调用过这个工具。
# 这个在做的事情不是“提示工程”，而是“状态回放”

# 2.为什么 ToolMessage 一定要“接在” AIMessage 之后
# ToolMessage 必须回应一个已存在的 tool_call

# 3.为什么不能“只用 ToolMessage”
# ToolMessage 不定义调用，它只回应调用

# 4.从模型内部视角看（很关键）
# 模型在生成下一步时，会隐式判断：
#
# “我当前是不是在等待工具结果？”
#
# 这个判断依据是：
#
# 最近一条 AIMessage 是否包含 tool_calls
#
# 如果有：
#
# 模型状态 = waiting_for_tool
#
# ➡️ 它会重点关注 ToolMessage，并据此修正。
#
# 如果没有：
#
# 模型状态 = planning / reasoning
#
# ➡️ ToolMessage 会被当成普通文本，甚至被忽略
