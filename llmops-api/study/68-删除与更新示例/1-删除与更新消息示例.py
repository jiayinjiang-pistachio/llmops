#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/20 19:00
@Author         : jiayinkong@163.com
@File           : 1-删除与更新消息示例.py
@Description    : 
"""
import os
from dataclasses import dataclass
from typing import Any

import dotenv
from langchain_core.messages import AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph


# --- 手动定义 RemoveMessage ---
@dataclass
class RemoveMessage(BaseMessage):
    """手动实现删除消息的类"""
    type: str = "remove"
    content: str = ""  # 必须包含 content 以通过旧版验证

    def __init__(self, id: str, **kwargs):
        super().__init__(id=id, content="", **kwargs)
        self.type = "remove"


dotenv.load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)


def chatbot(state: MessagesState, config: dict) -> Any:
    """聊天机器人节点"""
    return {"messages": [llm.invoke(state["messages"])]}


def delete_human_message(state: MessagesState, config: dict) -> Any:
    """删除状态中的人类消息"""
    human_message = state["messages"][0]
    return {"messages": [RemoveMessage(id=human_message.id)]}
    # 如果没有 RemoveMessage 类，直接返回带有 type: "remove" 的字典
    # return {"messages": [{"id": human_message.id, "type": "remove"}]}


def update_ai_message(state: MessagesState, config: dict) -> Any:
    """更新AI消息，为AI消息添加前缀"""
    ai_message = state["messages"][-1]
    return {"messages": [AIMessage(id=ai_message.id, content="更新后的ai消息" + ai_message.content)]}


graph_builder = StateGraph(MessagesState)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("delete_human_message", delete_human_message)
graph_builder.add_node("update_ai_message", update_ai_message)

graph_builder.set_entry_point("chatbot")
graph_builder.add_edge("chatbot", "delete_human_message")
graph_builder.add_edge("delete_human_message", "update_ai_message")
graph_builder.set_finish_point("update_ai_message")

graph = graph_builder.compile()

print(graph.invoke({"messages": [("human", "你好，你是？")]}))
