#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/20 11:06
@Author         : jiayinkong@163.com
@File           : 1-基础LangGraph示例.py
@Description    : 
"""
import os
from typing import TypedDict, Annotated, Any

import dotenv
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph

dotenv.load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
)


# 1.创建状态图，并使用GraphState作为状态数据
class State(TypedDict):
    """图结构的状态数据"""
    messages: Annotated[list, add_messages]
    user_name: str


def chatbot(state: State, config: dict) -> Any:
    """聊天机器人节点，使用大语言模型根据传递的消息列表生成内容"""
    ai_message = llm.invoke(state["messages"])
    return {"messages": [ai_message], "user_name": "chatbot"}


graph_builder = StateGraph(State)

# 2. 添加节点
graph_builder.add_node("llm", chatbot)

# 3. 添加边
graph_builder.add_edge(START, "llm")
graph_builder.add_edge("llm", END)

# 4. 编译图为Runnable可运行组件
graph = graph_builder.compile()

# 5. 调用图架构应用
print(graph.invoke({
    "messages": [
        ("human", "你好，你是谁？我是慕小课，我喜欢打篮球")
    ],
    "user_name": "graph"
}))
