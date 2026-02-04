#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/19 19:17
@Author         : jiayinkong@163.com
@File           : openapi_service.py
@Description    : 
"""
import json
from dataclasses import dataclass
from threading import Thread
from typing import Generator

from flask import current_app
from injector import inject
from langchain_core.messages import HumanMessage

from pkg.response import Response
from pkg.sqlalchemy import SQLAlchemy
from .app_config_service import AppConfigService
from .app_service import AppService
from .base_service import BaseService
from .conversation_service import ConversationService
from .language_model_service import LanguageModelService
from .retrieval_service import RetrievalService
from ..core.agent.agents import FunctionCallAgent
from ..core.agent.entities.agent_entity import AgentConfig
from ..core.agent.entities.queue_entity import AgentThought, QueueEvent
from ..core.memory import TokenBufferMemory
from ..entity.app_entity import AppStatus
from ..entity.conversation_entity import InvokeFrom, MessageStatus
from ..entity.dataset_entity import RetrievalSource
from ..exception import NotFoundException, ForbiddenException
from ..model import Account, EndUser, Conversation, Message
from ..schema import OpenAPIChatReq


@inject
@dataclass
class OpenapiService(BaseService):
    """开放API服务器"""
    db: SQLAlchemy
    app_service: AppService
    app_config_service: AppConfigService
    retrieval_service: RetrievalService
    conversation_service: ConversationService
    language_model_service: LanguageModelService

    def chat(self, req: OpenAPIChatReq, account: Account):
        """根据传递的请求+账号信息发起聊天对话，返回数据为块内容或生成器"""
        # 1. 判断当前应用是否属于当前账号
        app = self.app_service.get_app(req.app_id.data, account)

        # 2. 判断当前应用是否发布
        if app.status != AppStatus.PUBLISHED:
            raise NotFoundException("该应用不存在或未发布，请核实后重试")

        # 3. 判断是否传递了终端用户id，如果传递了则检测终端用户关联的应用
        if req.end_user_id.data:
            end_user: EndUser = self.get(EndUser, req.end_user_id.data)
            if not end_user or end_user.app_id != app.id:
                raise ForbiddenException("当前账号不存在或不属于该应用，请核实后重试")
        else:
            # 4. 如果不存在则创建一个终端用户
            end_user = self.create(EndUser, **{"tenant_id": account.id, "app_id": app.id})

        # 5. 检测是否传递了会话id，如果传递了需要检测会话的归属信息
        if req.conversation_id.data:
            conversation: Conversation = self.get(Conversation, req.conversation_id.data)
            if (
                    not conversation
                    or conversation.app_id != app.id
                    or conversation.invoke_from != InvokeFrom.SERVICE_API
                    or conversation.created_by != end_user.id
            ):
                raise ForbiddenException("该会话不存在，或者不属于该应用/终端用户/调用方式")
        else:
            # 6. 如果不存在则创建会话信息
            conversation: Conversation = self.create(Conversation, **{
                "app_id": app.id,
                "name": "New Conversation",
                "invoke_from": InvokeFrom.SERVICE_API,
                "created_by": end_user.id
            })

        # 7. 获取校验后的运行时配置
        app_config = self.app_config_service.get_app_config(app)

        # 8. 新建一条消息记录
        message: Message = self.create(Message, **{
            "app_id": app.id,
            "conversation_id": conversation.id,
            "invoke_from": InvokeFrom.SERVICE_API,
            "created_by": end_user.id,
            "query": req.query.data,
            "status": MessageStatus.NORMAL,
        })

        # 从大语言模型管理器中加载模型
        llm = self.language_model_service.load_language_model(app_config.get("model_config", {}))

        # 10. 实例化TokenBufferMemory用户提取短期记忆
        token_buffer_memory = TokenBufferMemory(
            db=self.db,
            conversation=conversation,
            model_instance=llm,
        )

        history = token_buffer_memory.get_history_prompt_messages(
            message_limit=app_config["dialog_round"],
        )

        # 11. 将运行时配置的tools转换成LangChain工具
        tools = self.app_config_service.get_langchian_tools_by_tool_config(app_config["tools"])

        # 12. 检测是否关联了知识库
        if app_config["datasets"]:
            # 13. 构建LangChain知识库检索工具
            dataset_retrieval = self.retrieval_service.create_langchain_tool_from_search(
                flask_app=current_app._get_current_object(),
                dataset_ids=[dataset["id"] for dataset in app_config["datasets"]],
                account_id=account.id,
                retrieval_source=RetrievalSource.APP,
                **app_config["retrieval_config"],
            )
            tools.append(dataset_retrieval)

        # todo: 14. 构建Agent智能体，目前暂时使用FunctionCallAgent
        agent = FunctionCallAgent(
            llm=llm,
            agent_config=AgentConfig(
                user_id=account.id,
                invoke_from=InvokeFrom.DEBUGGER,
                enable_long_term_memory=app_config["long_term_memory"]["enable"],
                tools=tools,
                review_config=app_config["review_config"],
                preset_prompt=app_config["preset_prompt"],
            )
        )

        # 15. 定义智能体状态基础数据
        agent_state = {
            "messages": [HumanMessage(req.query.data)],
            "history": history,
            "long_term_memory": conversation.summary,
        }

        # 16. 根据stream类型差异执行不同的代码
        if req.stream.data is True:
            agent_thoughts_dict: dict[str, AgentThought] = {}

            # === 关键修复：提前提取 ID，避免在 yield 时触发数据库查询 ===
            end_user_id_str = str(end_user.id)
            conversation_id_str = str(conversation.id)
            message_id_str = str(message.id)

            def handle_stream() -> Generator:
                """流式事件处理器，在python中只要在函数内部使用了yield关键字，那么这个函数的返回值类型肯定是生成器"""
                for agent_thought in agent.stream(agent_state):
                    # 提取thought以及answer
                    event_id = str(agent_thought.id)

                    # 将数据填充到agent_thought，便于存储到数据库服务中
                    if agent_thought.event != QueueEvent.PING:
                        # 除了agent_message数据为叠加，其他均为覆盖
                        if agent_thought.event == QueueEvent.AGENT_MESSAGE:
                            if event_id not in agent_thoughts_dict:
                                # 初始化智能体消息事件
                                agent_thoughts_dict[event_id] = agent_thought
                            else:
                                # 叠加智能体消息
                                agent_thoughts_dict[event_id] = agent_thoughts_dict[event_id].model_copy(
                                    update={
                                        "thought": agent_thoughts_dict[event_id].thought + agent_thought.thought,
                                        "answer": agent_thoughts_dict[event_id].answer + agent_thought.answer,
                                        "latency": agent_thought.latency,
                                    }
                                )
                        else:
                            # 处理其他类型事件数据
                            agent_thoughts_dict[event_id] = agent_thought

                    data = {
                        **agent_thought.model_dump(include={
                            "event", "thought", "observation", "tool", "tool_input", "answer", "latency",
                        }),
                        "id": event_id,
                        # === 使用提前提取好的变量 ===
                        "end_user_id": end_user_id_str,
                        "conversation_id": conversation_id_str,
                        "message_id": message_id_str,
                        "task_id": str(agent_thought.task_id),
                    }
                    yield f"event: {agent_thought.event.value}\ndata: {json.dumps(data)}\n\n"

            return handle_stream()

        # 17. 块内容输出
        agent_result = agent.invoke(agent_state)

        # 18. 将消息以及推理过车呢个添加到数据库
        thread = Thread(
            target=self.conversation_service.save_agent_thought,
            kwargs={
                "flask_app": current_app._get_current_object(),
                "account_id": account.id,
                "app_id": app.id,
                "app_config": app_config,
                "conversation_id": conversation.id,
                "message_id": message.id,
                "agent_thoughts": agent_result.agent_thoughts,
            }
        )
        thread.start()

        return Response(data={
            "id": str(message.id),
            "end_user_id": str(end_user.id),
            "conversation_id": str(conversation.id),
            "query": req.query.data,
            "answer": agent_result.answer,
            "total_token_count": 0,
            "latency": agent_result.latency,
            "agent_thoughts": [{
                "id": str(agent_thought.id),
                "event": agent_thought.event,
                "thought": agent_thought.thought,
                "observation": agent_thought.observation,
                "tool": agent_thought.tool,
                "tool_input": agent_thought.tool_input,
                "latency": agent_thought.latency,
                "created_at": 0,
            } for agent_thought in agent_result.agent_thoughts],
        })
