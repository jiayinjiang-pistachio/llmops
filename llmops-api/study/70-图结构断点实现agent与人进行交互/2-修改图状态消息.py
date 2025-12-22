#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/22 19:00
@Author         : jiayinkong@163.com
@File           : 2-修改图状态消息.py
@Description    : 
"""
import os
from typing import TypedDict, Annotated, Literal

import dotenv
from langchain_community.tools import GoogleSerperRun
from langchain_community.tools.openai_dalle_image_generation import OpenAIDALLEImageGenerationTool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.messages import ToolMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.checkpoint import MemorySaver
from langgraph.constants import END, START
from langgraph.graph import add_messages, StateGraph
from langgraph.prebuilt import ToolNode

dotenv.load_dotenv()


class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")


class DallEArgsSchema(BaseModel):
    query: str = Field(description="输入应该是生成图像的文本提示(prompt)")


# 1.定义工具与工具列表
google_serper = GoogleSerperRun(
    name="google_serper",
    description=(
        "一个低成本的谷歌搜索API。"
        "当你需要回答有关时事的问题时，可以调用该工具。"
        "该工具的输入是搜索查询语句。"
    ),
    args_schema=GoogleSerperArgsSchema,
    api_wrapper=GoogleSerperAPIWrapper(),
)
dalle = OpenAIDALLEImageGenerationTool(
    name="openai_dalle",
    api_wrapper=DallEAPIWrapper(
        model="dall-e-3",
        api_key=os.getenv("GPTSAPI_API_KEY"),  # 确保这里使用你可用的 Key
        base_url=os.getenv("OPENAI_API_BASE")  # 确保这里传入中转或自定义地址
    ),
    args_schema=DallEArgsSchema,
)


class State(TypedDict):
    """图状态数据结构，类型为字典"""
    messages: Annotated[list, add_messages]


tools = [google_serper, dalle]
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State, config: dict) -> dict:
    """聊天机器人函数"""
    # 1. 获取状态里的消息列表数据传递给llm
    ai_message = llm_with_tools.invoke(state["messages"])
    # 返回更新/生成的状态
    return {"messages": [ai_message]}


def route(state: State, config: dict) -> Literal["__end__", "tools"]:
    """动态选择工具执行亦或者结束"""
    # 获取最后一条消息
    ai_message = state["messages"][-1]
    # 2.检测消息是否存在tool_calls参数，如果是则执行`工具路由`
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END


graph_builder = StateGraph(State)

graph_builder.add_node("llm", chatbot)
graph_builder.add_node("tools", ToolNode(tools=tools))

graph_builder.add_edge(START, "llm")
graph_builder.add_conditional_edges("llm", route)
graph_builder.add_edge("tools", "llm")

# 编译图为可运行组件
checkpointer = MemorySaver()
graph = graph_builder.compile(checkpointer=checkpointer, interrupt_after=["tools"])

# 5.调用图架构应用
config = {"configurable": {"thread_id": 1}}
state = graph.invoke(
    {"messages": [("human", "2024年北京半程马拉松的前3名成绩是多少")]},
    config=config
)
print(state)

# 更新图的状态，去篡改工具消息
graph_state = graph.get_state(config=config)
tool_message = ToolMessage(
    id=graph_state[0]["messages"][-1].id,  # 最后一条是工具消息
    # 告诉大语言模型工具调用id，这里的工具调用id是让大语言模型知道这条消息是和哪个函数关联
    tool_call_id=graph_state[0]["messages"][-2].tool_calls[0]["id"],
    name=graph_state[0]["messages"][-2].tool_calls[0]["name"],
    content="2024年北京半程马拉松的第一名为慕小课01:59:40，第二名为慕二课成绩为02:04:16，第三名为慕三课02:15:17"
)

print("下一个步骤：", graph_state[1])
graph.update_state(config, {"messages": [tool_message]})
print(graph.invoke(None, config=config)["messages"][-1].content)
