#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/2/2 16:20
@Author         : jiayinkong@163.com
@File           : assistant_agent_service.py
@Description    : 
"""
import json
import os
from dataclasses import dataclass
from datetime import datetime
from threading import Thread
from typing import Generator
from uuid import UUID

from flask import current_app
from injector import inject
from langchain_core.messages import HumanMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool, tool
from langchain_openai import ChatOpenAI
from sqlalchemy import desc

from pkg.paginator import Paginator
from pkg.sqlalchemy import SQLAlchemy
from .base_service import BaseService
from .conversation_service import ConversationService
from .faiss_service import FaissService
from ..core.agent.agents import FunctionCallAgent
from ..core.agent.agents.agent_queue_manager import AgentQueueManager
from ..core.agent.entities.agent_entity import AgentConfig
from ..core.agent.entities.queue_entity import AgentThought, QueueEvent
from ..core.memory import TokenBufferMemory
from ..entity.conversation_entity import InvokeFrom, MessageStatus
from ..model import Account, Message
from ..schema import GetDebugConversationMessagesWithPageReq
from ..task.app_task import auto_create_app


@inject
@dataclass
class AssistantAgentService(BaseService):
    """辅助智能体服务器"""
    db: SQLAlchemy
    conversation_service: ConversationService
    faiss_service: FaissService

    def chat(self, query: str, account: Account) -> Generator:
        """传递query与账号ID，实现与辅助agent进行对话"""
        # 1. 获取辅助agentid
        assistant_agent_id = current_app.config.get("ASSISTANT_AGENT_ID")

        # 2. 获取当前应用的调试会话信息
        conversation = account.assistant_agent_conversation

        # 3. 新建一条消息记录
        message = self.create(
            Message,
            app_id=assistant_agent_id,
            conversation_id=conversation.id,
            query=query,
            status=MessageStatus.NORMAL,
            created_by=account.id,
            invoke_from=InvokeFrom.ASSISTANT_AGENT,
        )

        # 4. 使用GPT模型作为辅助agent的LLM
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("GPTSAPI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE"),
            temperature=0.8,
        )

        # 5. 实例化TokenBufferMemory用于提取短期记忆
        token_buffer_memory = TokenBufferMemory(
            db=self.db,
            conversation=conversation,
            model_instance=llm,
        )
        history = token_buffer_memory.get_history_prompt_messages(
            message_limit=3,
        )

        # 6. 将faiss向量数据库知识库检索工具添加到工具列表
        tools = [
            self.faiss_service.convert_faiss_to_tool(),
            self.convert_create_app_to_tool(account_id=account.id),
        ]

        # 7. 构建Agent智能体，目前暂时使用FunctionCallAgent
        agent = FunctionCallAgent(
            llm=llm,
            agent_config=AgentConfig(
                user_id=account.id,
                invoke_from=InvokeFrom.ASSISTANT_AGENT,
                enable_long_term_memory=True,
                tools=tools,
            ),
        )

        agent_thoughts: dict[str, AgentThought] = {}
        for agent_thought in agent.stream({
            "messages": [HumanMessage(query)],
            "history": history,
            "long_term_memory": conversation.summary,
        }):
            # 8. 提取 thought和answer
            event_id = str(agent_thought.id)
            task_id = str(agent_thought.task_id)

            # 9. 将数据填充到agent_thought，便于存储到数据库中
            if agent_thought.event != QueueEvent.PING:
                # 10. 除了 agent_message 叠加，其他事件一次性返回
                if agent_thought.event == QueueEvent.AGENT_MESSAGE:
                    if event_id not in agent_thoughts:
                        # 11. 初始化智能体事件
                        agent_thoughts[event_id] = agent_thought
                    else:
                        # 12. 叠加智能体消息
                        agent_thoughts[event_id] = agent_thoughts[event_id].model_copy(
                            update={
                                "thought": agent_thoughts[event_id].thought + agent_thought.thought,
                                "answer": agent_thoughts[event_id].answer + agent_thought.answer,
                                "latency": agent_thought.latency,
                            }
                        )
                else:
                    # 13. 处理其他类型事件的消息
                    agent_thoughts[event_id] = agent_thought

            data = {
                **agent_thought.model_dump(
                    include={"event", "thought", "tool", "tool_input", "observation", "answer", "latency"},
                ),
                "id": event_id,
                "conversation_id": str(conversation.id),
                "message_id": str(message.id),
                "task_id": task_id,
            }
            yield f"event: {agent_thought.event.value}\ndata: {json.dumps(data)}\n\n"

        # 22. 循环将消息以及推理过程添加到数据库
        thread = Thread(
            target=self.conversation_service.save_agent_thought,
            kwargs={
                "flask_app": current_app._get_current_object(),
                "account_id": account.id,
                "app_id": assistant_agent_id,
                "app_config": {
                    "long_term_memory": {"enable": True},
                },
                "conversation_id": conversation.id,
                "message_id": message.id,
                "agent_thoughts": [agent_thought for agent_thought in agent_thoughts.values()],
            }
        )
        thread.start()

    @classmethod
    def stop_chat(cls, task_id: UUID, account: Account):
        """根据传递的task_id和账号信息，停止会话"""
        AgentQueueManager.set_stop_flag(task_id, invoke_from=InvokeFrom.ASSISTANT_AGENT, user_id=account.id)

    def get_conversation_messages_with_page(
            self,
            req: GetDebugConversationMessagesWithPageReq,
            account: Account
    ) -> tuple[list[Message], Paginator]:
        """根据传递的账号获取会话消息分页列表数据"""

        # 1. 获取会话记录
        conversation = account.assistant_agent_conversation

        # 2. 构建分页器并构建游标条件
        paginator = Paginator(db=self.db, req=req)
        filters = []
        if req.created_at.data:
            # 3. 将时间戳转换成Datetime
            created_at_datetime = datetime.fromtimestamp(req.created_at.data)
            filters.append(Message.created_at <= created_at_datetime)

        # 4. 执行分页并查询数据
        messages = paginator.paginate(
            self.db.session.query(Message).filter(
                Message.conversation_id == conversation.id,
                Message.status.in_([MessageStatus.STOP, MessageStatus.NORMAL]),
                Message.answer != "",
                *filters,
            ).order_by(desc("created_at"))
        )

        return messages, paginator

    def delete_conversation(self, account: Account) -> None:
        """根据传递的账号清空辅助agent智能体消息列表"""
        self.update(account, assistant_agent_conversation_id=None)

    @classmethod
    def convert_create_app_to_tool(cls, account_id: UUID) -> BaseTool:
        """定义自动创建Agent应用的LangChain工具"""

        class CreateAppInput(BaseModel):
            name: str = Field(description="需要创建的Agent/应用名称，长度不超过50个字符")
            description: str = Field(description="需要创建的Agent/应用描述，请详细概括该应用的功能")

        @tool("create_app", args_schema=CreateAppInput)
        def create_app(name: str, description: str) -> str:
            """如果用户提出了需要创建一个Agent或应用，你可以调用此工具，参数的输入是应用的名称和描述，返回的数据是创建后的成功提示"""
            # 1. 调用celery异步任务在后端创建应用
            auto_create_app.delay(name=name, description=description, account_id=account_id)

            # 2. 返回成功提示
            return f"已调用后端异步任务创建Agent应用。\n应用名称：{name}\n应用描述：{description}"

        return create_app
