#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/8 11:40
@Author         : jiayinkong@163.com
@File           : function_call_agent.py
@Description    : 
"""
import json
from threading import Thread
from typing import Literal

from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, RemoveMessage, ToolMessage
from langgraph.constants import END
from langgraph.graph.state import CompiledStateGraph, StateGraph

from internal.core.agent.agents.base_agent import BaseAgent
from internal.core.agent.entities.agent_entity import AgentState, AGENT_SYSTEM_PROMPT_TEMPLATE
from internal.exception import FailException


class FunctionCallAgent(BaseAgent):
    def run(self, query: str, history: list[AnyMessage] = None, long_term_memory: str = ""):
        """运行智能体应用，并使用yield关键字返回对应的数据"""
        # 1.预处理传递的数据
        if history is None:
            history = []

        # 2.调用函数构建智能体
        agent = self._build_graph()

        # 3.调用智能体获取数据
        thread = Thread(
            target=agent.invoke,
            args=({
                      "messages": [HumanMessage(content=query)],
                      "history": history,
                      "long_term_memory": long_term_memory,
                  },)
        )
        thread.start()

    def _build_graph(self) -> CompiledStateGraph:
        """构建LangGraph图结构编译程序"""

        # 1. 创建图
        graph = StateGraph(AgentState)

        # 2. 创建节点
        graph.add_node("long_term_memory_recall", self._long_term_memory_recall_node)
        graph.add_node("llm", self._llm_node)
        graph.add_node("tools", self._tools)

        # 添加边并设置起点
        graph.set_entry_point("long_term_memory_recall")
        graph.add_edge("long_term_memory_recall", "llm")
        graph.add_conditional_edges("llm", self._tool_condition)
        graph.add_edge("tools", "llm")

        # 4. 编译应该用并返回
        agent = graph.compile()

        return agent

    def _long_term_memory_recall_node(self, state: AgentState) -> AgentState:
        """长期记忆召回节点"""
        # 1. 根据传递的智能体配置判断是否需要召回长期记忆
        long_term_memory = ""
        if self.agent_config.enable_long_term_memory:
            long_term_memory = state["long_term_memory"]

        # 构建预设消息列表，并将 preset_prompt+long_term_memory填充到系统消息中
        preset_messages = [
            SystemMessage(AGENT_SYSTEM_PROMPT_TEMPLATE.format(
                preset_prompt=self.agent_config.preset_prompt,
                long_term_memory=long_term_memory,
            ))
        ]

        # 将短期历史消息添加到消息列表
        history = state["history"]
        if isinstance(history, list) and len(history) > 0:
            # 4. 校验历史消息是不是复数形式
            if len(history) % 2 != 0:
                raise FailException("智能体历史消息列表格式错误")

            # 5. 拼接历史消息
            preset_messages.extend(history)

        # 6.拼接当前的用户信息
        human_message = state["messages"][-1]
        preset_messages.append(HumanMessage(content=human_message.content))

        # 7.处理预设消息，将预设消息添加到用户消息前，先去删除用户的原始消息，再去补充一个新的代替
        return {
            "messages": [RemoveMessage(id=human_message.id), *preset_messages],
        }

    def _llm_node(self, state: AgentState) -> AgentState:
        """大语言模型节点"""
        # 1. 从智能体配置提取大语言模型
        llm = self.agent_config.llm

        # 2. 检测大语言模型实例是否有bing_tools方法（判断是否为函数），如果没有则不绑定，如果有还需要检测tools是否为空，不为空则绑定
        if hasattr(llm, "bind_tools") and callable(getattr(llm, "bind_tools")) and len(self.agent_config.tools) > 0:
            llm = llm.bind_tools(self.agent_config.tools)
        else:
            print("没有调用工具/没有可调用的工具")

        # 3. 流式调用LLM输出对应内容
        gathered = None

        for chunk in llm.stream(state["messages"]):
            # 聚合处理：LangChain 的 AIMessageChunk 支持通过 + 号自动合并 tool_calls
            if gathered is None:
                gathered = chunk
            else:
                gathered += chunk

        return {"messages": [gathered]}

    def _tools(self, state: AgentState) -> AgentState:
        """工具调用节点"""
        # 1. 将工具列表转换成字典，便于调用指定工具
        tools_to_dict = {
            tool.name: tool
            for tool in self.agent_config.tools
        }

        # 2. 提取数据状态中的tool_calls
        tool_calls = state["messages"][-1].tool_calls

        # 3. 循环执行工具组装工具消息
        messages = []
        for tool_call in tool_calls:
            tool = tools_to_dict[tool_call["name"]]
            tool_result = tool.invoke(tool_call["args"])
            messages.append(ToolMessage(
                tool_call_id=tool_call["id"],
                content=json.dumps(tool_result),
                name=tool_call["name"],
            ))

        return {"messages": messages}

    @classmethod
    def _tool_condition(cls, state: AgentState) -> Literal["__end__", "tools"]:
        """检测下一个节点是执行tools节点，还是直接结束"""
        messages = state["messages"]

        ai_message = messages[-1]

        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"

        return END
