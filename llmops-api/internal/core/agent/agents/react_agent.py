#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/2/4 09:43
@Author         : jiayinkong@163.com
@File           : react_agent.py
@Description    : 
"""
import json
import logging
import re
import time
import uuid

from langchain_core.messages import SystemMessage, messages_to_dict, HumanMessage, RemoveMessage, AIMessage, \
    ToolMessage
from langchain_core.tools import render_text_description_and_args

from internal.exception import FailException
from .function_call_agent import FunctionCallAgent
from ..entities.agent_entity import AgentState, AGENT_SYSTEM_PROMPT_TEMPLATE, REACT_AGENT_SYSTEM_PROMPT_TEMPLATE, \
    MAX_ITERATION_RESPONSE
from ..entities.queue_entity import AgentThought, QueueEvent
from ...language_model.entities.model_entity import ModelFeature


class ReACTAgent(FunctionCallAgent):
    """基于ReACT推理的智能体，继承FunctionCallAgent，并重写long_term_memory_node和llm_node两个节点"""

    def _long_term_memory_recall_node(self, state: AgentState) -> AgentState:
        # 1. 判断是否支持工具调用，如果支持，则直接使用工具智能体的长期记忆召回节点
        if ModelFeature.TOOL_CALL in self.llm.features:
            return super()._long_term_memory_recall_node(state)

        # 2. 根据传递的智能体配置判断是否需要召回长期记忆
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

        # 3. 检测是否支持AGENT_THOUGHT，如果不支持，则使用没有工具描述的prompt
        if ModelFeature.AGENT_THOUGHT not in self.llm.features:
            preset_messages = [
                SystemMessage(AGENT_SYSTEM_PROMPT_TEMPLATE.format(
                    preset_prompt=self.agent_config.preset_prompt,
                    long_term_memory=long_term_memory,
                ))
            ]
        else:
            # 4. 支持ReACTAgent智能体推理，使用系统提示词添加工具描述
            preset_messages = [
                SystemMessage(REACT_AGENT_SYSTEM_PROMPT_TEMPLATE.format(
                    preset_prompt=self.agent_config.preset_prompt,
                    long_term_memory=long_term_memory,
                    tool_description=render_text_description_and_args(self.agent_config.tools),
                ))
            ]

        # 5. 将短期历史消息添加到消息列表中
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
        """重写llm_node节点"""
        print(f"DEBUG: Messages sent to LLM: {state['messages']}")
        # 1. 检测是否支持工具调用
        if ModelFeature.TOOL_CALL in self.llm.features:
            return super()._llm_node(state)

        task_id = state["task_id"]
        current_iteration_count = state["iteration_count"]

        # 2. 检测当前agent迭代次数是否符合需求
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
            # 3. 模拟生成大语言模型
            return {"messages": [AIMessage(MAX_ITERATION_RESPONSE)]}

        # 4. 从智能体配置提取大语言模型
        id = uuid.uuid4()
        start_at = time.perf_counter()
        llm = self.llm

        # 6. 流式调用LLM输出对应内容
        gathered = None

        # 【修复点】检查最后一条消息是否为空
        last_message = state["messages"][-1]
        if not last_message.content or not last_message.content.strip():
            # 如果是空的，可能导致模型不返回任何 chunk 触发 AssertionError
            logging.warning("Detected empty last message content, providing default prompt.")
            # 可以补齐一个空内容或者抛出异常

        # 【修复点】打印当前发送给模型的消息，用于排查
        logging.debug(f"Input Messages: {state['messages']}")

        # 【关键修复】过滤掉 RemoveMessage 标记，并确保消息列表中没有空的 HumanMessage
        # 【增强修复】适配智谱及严格角色校验的模型
        raw_cleaned = []
        for m in state["messages"]:
            if isinstance(m, RemoveMessage): continue

            if isinstance(m, ToolMessage):
                # 转换为 HumanMessage，并带上 call_id 提示，方便模型对应
                raw_cleaned.append(HumanMessage(content=f"[工具调用结果]: {m.content}", id=m.id))
            elif isinstance(m, AIMessage):
                # 关键：智谱不支持消息体带 tool_calls 字典，必须转为纯文本或去掉该属性
                new_ai_msg = AIMessage(content=m.content, id=m.id)
                if m.tool_calls and not m.content:
                    new_ai_msg.content = f"正在调用工具..."  # 兜底内容
                raw_cleaned.append(new_ai_msg)
            elif isinstance(m, (SystemMessage, HumanMessage)):
                if m.content: raw_cleaned.append(m)

        # 【核心逻辑】确保角色交替 (Human/AI/Human/AI...)
        cleaned_messages = []
        for msg in raw_cleaned:
            if not cleaned_messages:
                cleaned_messages.append(msg)
                continue

            # 如果连续两个消息角色相同，进行内容合并
            prev_msg = cleaned_messages[-1]
            if type(prev_msg) is type(msg) and not isinstance(msg, SystemMessage):
                prev_msg.content += f"\n\n{msg.content}"
            else:
                cleaned_messages.append(msg)

        # 如果最后一条是空的（可能由前面的节点产生错误导致），补一个提示
        if not cleaned_messages or cleaned_messages[-1].content == "":
            cleaned_messages.append(HumanMessage(content="Please continue."))

        for i, m in enumerate(cleaned_messages):
            print(f"MSG {i} [{m.__class__.__name__}]: {str(m.content)[:50]}...")

        # 5.流式输出调用LLM，并判断输出内容是否以"```json"为开头，用于区分工具调用和文本生成
        try:
            for chunk in llm.stream(cleaned_messages):
                # 聚合处理：LangChain 的 AIMessageChunk 支持通过 + 号自动合并 tool_calls
                if gathered is None:
                    gathered = chunk
                else:
                    gathered += chunk
            full_content = gathered.content.strip()
            # 2. 使用更宽松的正则寻找 JSON
            # 只要内容里包含 ```json { ... } ``` 就算工具调用
            pattern = r"```json\s*(\{.*?\})\s*```"
            match = re.search(pattern, full_content, re.DOTALL)

            if match:
                # --- 判定为：工具调用 (Thought) ---
                json_str = match.group(1).strip()
                match_json = json.loads(json_str)

                tool_calls = [{
                    "name": match_json.get("name", ""),
                    "args": match_json.get("args", {}),
                    "id": f"call_{uuid.uuid4().hex}",
                    "type": "tool_call",
                }]

                # 发布 Thought 事件（包含 AI 说的那句前言）
                self.agent_queue_manager.publish(state["task_id"], AgentThought(
                    id=id,
                    task_id=state["task_id"],
                    event=QueueEvent.AGENT_THOUGHT,
                    thought=full_content,  # 这里传全量内容，方便前端展示 AI 的思考过程
                    message=messages_to_dict(state["messages"]),
                    latency=(time.perf_counter() - start_at),
                ))

                return {
                    "messages": [AIMessage(content=full_content, tool_calls=tool_calls)],
                    "iteration_count": state["iteration_count"] + 1
                }
            else:
                # --- 判定为：普通文本回复 (Message) ---
                # 如果没有 JSON，就当做普通消息一次性发布
                self.agent_queue_manager.publish(state["task_id"], AgentThought(
                    id=id,
                    task_id=state["task_id"],
                    event=QueueEvent.AGENT_MESSAGE,
                    thought=full_content,
                    message=messages_to_dict(state["messages"]),
                    answer=full_content,
                    latency=(time.perf_counter() - start_at),
                ))
                self.agent_queue_manager.publish(task_id, AgentThought(
                    id=uuid.uuid4(),
                    task_id=state["task_id"],
                    event=QueueEvent.AGENT_END,
                ))
                final_ai_msg = AIMessage(content=gathered.content)
                return {"messages": [final_ai_msg], "iteration_count": state["iteration_count"] + 1}
        except Exception as e:
            logging.exception(f"LLM节点发生错误，错误信息：{str(e)}")
            self.agent_queue_manager.publish_error(task_id, f"LLM节点发生错误，错误信息：{str(e)}")
            raise e
