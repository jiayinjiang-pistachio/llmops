#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/20 12:21
@Author         : jiayinkong@163.com
@File           : 1-条件边与循环构建工具调用agent.py
@Description    : 
"""
import json
import os
from typing import TypedDict, Annotated, Any, Literal

import dotenv
from langchain_community.tools import GoogleSerperRun
from langchain_community.tools.openai_dalle_image_generation import OpenAIDALLEImageGenerationTool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.messages import ToolMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.constants import END
from langgraph.graph import add_messages, StateGraph

dotenv.load_dotenv()


class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")


class DallEArgsSchema(BaseModel):
    query: str = Field(description="输入应该是生成图片的文本提示(prompt)")


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
    messages: Annotated[list, add_messages]


tools = [google_serper, dalle]

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
)
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State, config: dict) -> Any:
    """聊天机器人函数"""
    # 1.获取状态里存储的消息列表并传递给llm
    ai_message = llm_with_tools.invoke(state["messages"])

    # 2.返回更新/生成的状态
    return {"messages": [ai_message]}


# 在外部先定义好工具映射表，方便快速查找
tools_map = {tool.name: tool for tool in tools}


def tool_executor(state: State, config: dict) -> Any:
    """工具执行节点"""
    # 1.提取数据状态中的tool_calls
    tool_calls = state["messages"][-1].tool_calls  # -1, 倒数第一条

    # 2. 根据找到的tool_calls去获取需要执行什么工具
    # tools_by_name = {tool.name: tool for tool in tool_calls}

    # 3. 执行工具得到结果
    messages = []
    for tool_call in tool_calls:
        # tool = tools_by_name[tool_call.name]
        # 使用工具名称从 tools_map 中获取真正的工具对象
        tool = tools_map[tool_call["name"]]
        messages.append(
            ToolMessage(
                tool_call_id=tool_call["id"],
                content=json.dumps(tool.invoke(tool_call["args"]), ensure_ascii=False),
                name=tool_call["name"]
            )
        )

    # 4. 将工具的执行结果作为工具消息更新到数据状态机
    return {"messages": messages}


def route(state: State, config: dict) -> Literal["tool_executor", "__end__"]:
    """通过路由来检测后续返回的节点是什么，返回的节点两个，一个是工具执行，一个是结束节点"""
    ai_message = state["messages"][-1]
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tool_executor"

    return END


# 1. 创建状态图，并使用GraphState作为状态数据
graph_builder = StateGraph(State)

# 添加节点
graph_builder.add_node("llm", chatbot)
graph_builder.add_node("tool_executor", tool_executor)

# 添加边
graph_builder.set_entry_point("llm")
graph_builder.add_conditional_edges("llm", route)
graph_builder.add_edge("tool_executor", "llm")

# 编译图为Runnable可运行组件
graph = graph_builder.compile()

# 调用图架构应用
state = graph.invoke({"messages": [("human", "2024年北京半程马拉松的前3名成绩是多少")]})

for message in state["messages"]:
    print(f"消息类型：{message.type}")
    if hasattr(message, "tool_calls") and len(message.tool_calls) > 0:
        print(f"工具调用参数：{message.tool_calls}")
    print(f"消息内容：{message.content}")
    print("=" * 20)
