#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/8 11:40
@Author         : jiayinkong@163.com
@File           : function_call_agent.py
@Description    : 
"""
import json
import logging
import re
import time
import uuid
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage, RemoveMessage, ToolMessage, \
    messages_to_dict, AIMessage, BaseMessage
from langgraph.constants import END
from langgraph.graph.state import CompiledStateGraph, StateGraph

from internal.core.agent.agents.base_agent import BaseAgent
from internal.core.agent.entities.agent_entity import AgentState, AGENT_SYSTEM_PROMPT_TEMPLATE, \
    DATASET_RETRIEVAL_TOOL_NAME, MAX_ITERATION_RESPONSE
from internal.core.agent.entities.queue_entity import AgentThought, QueueEvent
from internal.exception import FailException


class FunctionCallAgent(BaseAgent):
    def _built_agent(self) -> CompiledStateGraph:
        """构建LangGraph图结构编译程序"""

        # 1. 创建图
        graph = StateGraph(AgentState)

        # 2. 创建节点
        graph.add_node("preset_operation", self._preset_operation_node)
        graph.add_node("long_term_memory_recall", self._long_term_memory_recall_node)
        graph.add_node("llm", self._llm_node)
        graph.add_node("tools", self._tools)

        # 添加边并设置起点
        graph.set_entry_point("preset_operation")
        graph.add_conditional_edges("preset_operation", self._preset_operation_condition)
        graph.add_edge("long_term_memory_recall", "llm")
        graph.add_conditional_edges("llm", self._tool_condition)
        graph.add_edge("tools", "llm")

        # 4. 编译应该用并返回
        agent = graph.compile()

        return agent

    def _preset_operation_node(self, state: AgentState) -> AgentState:
        """预设操作，涵盖：输入审核、数据预处理、条件边等"""
        # 1. 获取审核配置与用户输入
        review_config = self.agent_config.review_config
        query = state["messages"][-1].content  # 人类消息的内容

        # 2. 检测是否开启审核配置
        if review_config["enable"] and review_config["inputs_config"]["enable"]:
            # 3. 如果包含敏感词则执行后续步骤
            contains_keyword = any(keyword in query for keyword in review_config["keywords"])
            if contains_keyword:
                preset_response = review_config["inputs_config"]["preset_response"]
                task_id = state["task_id"]
                self.agent_queue_manager.publish(task_id, AgentThought(
                    id=uuid.uuid4(),
                    task_id=task_id,
                    event=QueueEvent.AGENT_MESSAGE,
                    thought=preset_response,
                    message=messages_to_dict(state["messages"]),
                    answer=preset_response,
                    latency=0,
                ))

                # 智能体结束事件
                self.agent_queue_manager.publish(task_id, AgentThought(
                    id=uuid.uuid4(),
                    task_id=task_id,
                    event=QueueEvent.AGENT_END,
                ))

                return {"messages": [AIMessage(preset_response)]}

        return {"messages": []}

    def _long_term_memory_recall_node(self, state: AgentState) -> AgentState:
        """长期记忆召回节点"""
        # 1. 根据传递的智能体配置判断是否需要召回长期记忆
        long_term_memory = ""
        task_id = state["task_id"]

        if self.agent_config.enable_long_term_memory:
            long_term_memory = state["long_term_memory"]

            # 添加长期记忆事件到队列
            self.agent_queue_manager.publish(task_id, AgentThought(
                id=uuid.uuid4(),
                task_id=task_id,
                event=QueueEvent.LONG_TERM_MEMORY_RECALL,
                observation=long_term_memory,
            ))

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
                self.agent_queue_manager.publish_error(task_id, "智能体历史消息列表格式错误")
                logging.exception(
                    f"智能体历史消息列表格式错误，len(history)={len(history)}，history={json.dumps(messages_to_dict(history))}")
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
        task_id = state["task_id"]
        current_iteration_count = state["iteration_count"]

        # 1. 检测当前agent迭代次数是否符合需求
        if current_iteration_count > self.agent_config.max_iteration_count:
            self.agent_queue_manager.publish(task_id, AgentThought(
                id=uuid.uuid4(),
                task_id=task_id,
                event=QueueEvent.AGENT_MESSAGE,
                thought=MAX_ITERATION_RESPONSE,
                message=messages_to_dict(state["messages"]),
                answer=MAX_ITERATION_RESPONSE,
                latency=0,
            ))
            self.agent_queue_manager.publish(task_id, AgentThought(
                id=uuid.uuid4(),
                task_id=task_id,
                event=QueueEvent.AGENT_END,
            ))
            # 模拟生成大语言模型
            return {"messages": [AIMessage(MAX_ITERATION_RESPONSE)]}

        # 2. 从智能体配置提取大语言模型
        id = uuid.uuid4()
        start_at = time.perf_counter()
        llm = self.llm

        # 3. 检测大语言模型实例是否有bing_tools方法（判断是否为函数），如果没有则不绑定，如果有还需要检测tools是否为空，不为空则绑定
        if hasattr(llm, "bind_tools") and callable(getattr(llm, "bind_tools")) and len(self.agent_config.tools) > 0:
            llm = llm.bind_tools(self.agent_config.tools)
        else:
            print("没有调用工具/没有可调用的工具")

        # 4. 流式调用LLM输出对应内容
        gathered = None
        generation_type = ""

        # 5. 获取输出内容审核配置是否开启
        review_config = self.agent_config.review_config
        review_config_outputs_open = review_config["enable"] and review_config["outputs_config"]["enable"]

        # 【修复 1】确保发送的消息序列是合法的，过滤 RemoveMessage 和空消息
        cleaned_messages = []
        for m in state["messages"]:
            if isinstance(m, (BaseMessage, AIMessage, HumanMessage, SystemMessage, ToolMessage)):
                # 只有内容不为空，或者是带 tool_calls 的 AIMessage 才放行
                if hasattr(m, "content") and (m.content or (isinstance(m, AIMessage) and m.tool_calls)):
                    cleaned_messages.append(m)

        # 如果清洗后最后一条是空的，补一个提示，防止 API 报错
        if not cleaned_messages or cleaned_messages[-1].content == "":
            cleaned_messages.append(HumanMessage(content="Please continue."))

        try:
            for chunk in llm.stream(state["messages"]):
                # 聚合处理：LangChain 的 AIMessageChunk 支持通过 + 号自动合并 tool_calls
                if gathered is None:
                    gathered = chunk
                else:
                    gathered += chunk

                # 检测生成类型是工具参数还是文本生成
                # if not generation_type:
                if chunk.tool_call_chunks or (chunk.tool_calls and len(chunk.tool_calls) > 0):
                    generation_type = "thought"
                elif chunk.content:
                    generation_type = "message"

                # 如果生成的是消息则提交智能体消息事件
                if generation_type == "message":
                    content = chunk.content
                    # 提取片段内容并检测是否开启输出审核
                    if review_config_outputs_open:
                        for keyword in review_config["keywords"]:
                            content = re.sub(re.escape(keyword), "**", content, flags=re.IGNORECASE)

                    self.agent_queue_manager.publish(task_id, AgentThought(
                        id=id,
                        task_id=task_id,
                        event=QueueEvent.AGENT_MESSAGE,
                        thought=content,
                        message=messages_to_dict(state["messages"]),
                        answer=content,
                        latency=time.perf_counter() - start_at,

                    ))

            # 【修复 2】核心防御：如果 gathered 依然为 None，说明 LLM 什么都没返回
            if gathered is None:
                logging.error("LLM stream returned None. Using fallback message.")
                gathered = AIMessage(content="抱歉，我暂时无法处理您的请求。")
                generation_type = "message"

        except Exception as e:
            logging.exception(f"LLM节点发生错误，错误信息：{str(e)}")
            self.agent_queue_manager.publish_error(task_id, f"LLM节点发生错误，错误信息：{str(e)}")
            raise e

        # 6. 如果类型为推理则添加智能体推理事件
        if generation_type == "thought":
            self.agent_queue_manager.publish(task_id, AgentThought(
                id=id,  # 之所以可以这样写，是因为拿到的uuid不一样，是因为agent_thought与message是if-else的关系（每次执行到_llm_node时）
                task_id=task_id,
                event=QueueEvent.AGENT_THOUGHT,
                message=messages_to_dict(state["messages"]),
                latency=time.perf_counter() - start_at,
                thought=json.dumps(gathered.tool_calls),
            ))
        elif generation_type == "message":
            # 如果LLM直接生成answer，则表示已经拿到最终答案，则停止监听
            self.agent_queue_manager.publish(task_id, AgentThought(
                id=uuid.uuid4(),
                task_id=task_id,
                event=QueueEvent.AGENT_END
            ))

        # 在函数的最后
        # 确保 gathered 是完整的 AIMessage 而不是 AIMessageChunk
        final_message = AIMessage(
            content=gathered.content if hasattr(gathered, 'content') else "",
            tool_calls=getattr(gathered, 'tool_calls', [])
        )

        return {"messages": [final_message], "iteration_count": current_iteration_count + 1}

    def _tools(self, state: AgentState) -> AgentState:
        """工具调用节点"""
        print("----进行tools调用----", state["iteration_count"])
        # 1. 将工具列表转换成字典，便于调用指定工具
        tools_to_dict = {
            tool.name: tool
            for tool in self.agent_config.tools
        }
        task_id = state["task_id"]

        # 2. 提取数据状态中的tool_calls
        tool_calls = state["messages"][-1].tool_calls

        # 3. 循环执行工具组装工具消息
        messages = []
        for tool_call in tool_calls:
            # 4. 创建智能体动作事件id，并记录开始时间
            id = uuid.uuid4()
            start_at = time.perf_counter()

            try:
                # 5. 获取工具并调用工具
                tool = tools_to_dict[tool_call["name"]]
                tool_result = tool.invoke(tool_call["args"])
            except Exception as e:
                # 6. 添加工具出错信息
                tool_result = f"工具执行出错：{str(e)}"

            # 7. 将工具消息添加到列表
            messages.append(ToolMessage(
                tool_call_id=tool_call["id"],
                content=json.dumps(tool_result),
                name=tool_call["name"],
            ))

            # 8. 判断执行工具名字，提交不同事件，涵盖智能体动作及知识库检索
            event = (
                QueueEvent.AGENT_ACTION
                if tool_call["name"] != DATASET_RETRIEVAL_TOOL_NAME
                else QueueEvent.DATASET_RETRIEVAL
            )
            self.agent_queue_manager.publish(task_id, AgentThought(
                id=id,
                task_id=task_id,
                event=event,
                observation=json.dumps(tool_result),
                tool=tool_call["name"],
                tool_input=tool_call["args"],
                latency=time.perf_counter() - start_at,
            ))

        return {"messages": messages}

    @classmethod
    def _tool_condition(cls, state: AgentState) -> Literal["__end__", "tools"]:
        """检测下一个节点是执行tools节点，还是直接结束"""
        messages = state["messages"]

        ai_message = messages[-1]

        print("----ai_message-----", ai_message)

        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"

        return END

    @classmethod
    def _preset_operation_condition(cls, state: AgentState) -> Literal["__end__", "long_term_memory_recall"]:
        """预设操作条件边，用于判断是否触发预设响应"""
        # 1. 提取状态的最后一条消息
        message = state["messages"][-1]

        # 2. 判断消息的类型，如果是AI消息则说明触发了审核机制，直接结束
        if message.type == "ai":
            return END

        return "long_term_memory_recall"
