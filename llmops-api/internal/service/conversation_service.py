#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/5 20:20
@Author         : jiayinkong@163.com
@File           : conversation_service.py
@Description    : 
"""
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from flask import Flask
from injector import inject
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from sqlalchemy import desc

from internal.core.agent.entities.queue_entity import AgentThought, QueueEvent
from internal.entity.conversation_entity import SUMMARIZER_TEMPLATE, CONVERSATION_NAME_TEMPLATE, ConversationInfo, \
    SUGGESTED_QUESTIONS_TEMPLATE, SuggestedQuestions, InvokeFrom, MessageStatus
from internal.model import Conversation, Message, MessageAgentThought, Account
from pkg.paginator import Paginator
from pkg.sqlalchemy import SQLAlchemy
from .base_service import BaseService
from ..exception import NotFoundException
from ..schema.conversation_schema import GetConversationMessagesWithPageReq


@inject
@dataclass
class ConversationService(BaseService):
    """会话服务"""
    db: SQLAlchemy

    @classmethod
    def summary(cls, human_message: str, ai_message: str, old_summary: str = "") -> str:
        """根据传递的人类消息、AI消息、原始的摘要信息总结生成一段新的摘要"""
        # 1. 创建 prompt
        prompt = ChatPromptTemplate.from_template(SUMMARIZER_TEMPLATE)

        # 2. 构建大语言模型实例，并且将大语言模型的问题调低，降低幻觉的概率
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("GPTSAPI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE"),
            temperature=0.5,
        )

        # 3. 构建链应用
        summary_chain = prompt | llm | StrOutputParser()

        # 4. 调用链并获取新摘要信息
        new_summary = summary_chain.invoke({
            "summary": old_summary,
            "new_lines": f"Human: {human_message}\nAI: {ai_message}",
        })
        return new_summary

    @classmethod
    def generate_conversation_name(cls, query: str) -> str:
        """根据传递的query生成对应的会话名字，并且语言与用户的输入保持一致"""
        # 1. 创建prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", CONVERSATION_NAME_TEMPLATE),
            ("human", "{query}")
        ])

        # 2. 构建大语言模型实例，并且将大语言模型的温度调低，降低幻觉的概率
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("GPTSAPI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE"),
            temperature=0,
        )
        structured_llm = llm.with_structured_output(ConversationInfo)

        # 3. 构建链应用
        chain = prompt | structured_llm

        # 4. 提取并整理query，截取长度过长的部分
        if len(query) > 2000:
            query = query[:300] + "...[TRUNCATED]..." + query[-300:]
        query = query.replace("\n", " ")

        # 5. 调用链并获取会话信息
        conversation_info = chain.invoke({"query": query})

        # 6. 提取会话名称
        name = "新的会话"
        try:
            if conversation_info and hasattr(conversation_info, "subject"):
                name = conversation_info.subject
        except Exception as e:
            logging.exception(f"提取会话名称出错，conversation_info: {conversation_info}, 错误信息：{str(e)}")

        if len(name) > 75:
            name = name[:75] + "..."

        return name

    @classmethod
    def generate_suggested_questions(cls, histories: str) -> list[str]:
        """根据传递的历史消息说呢过程呢个最多不超过3个的建议问题"""
        # 1. 创建prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", SUGGESTED_QUESTIONS_TEMPLATE),
            ("human", "{histories}")
        ])

        # 2. 构建大语言模型实例，并且将大语言模型的温度调低，降低幻觉的概率
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("GPTSAPI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE"),
            temperature=0,
        )
        structured_llm = llm.with_structured_output(SuggestedQuestions)

        # 3. 构建链应用
        chain = prompt | structured_llm

        # 4. 调用链并获取建议问题列表
        suggested_questions = chain.invoke({"histories": histories})

        # 4. 提取建议问题列表
        questions = []
        try:
            if suggested_questions and hasattr(suggested_questions, "questions"):
                questions = suggested_questions.questions
        except Exception as e:
            logging.exception(f"生成建议问题出错，suggested_questions: {suggested_questions}, 错误信息：{str(e)}")

        if len(questions) > 3:
            questions = questions[:3]

        return questions

    def save_agent_thought(
            self,
            flask_app: Flask,
            account_id: UUID,
            app_id: UUID,
            app_config: dict[str, Any],
            conversation_id: UUID,
            message_id: UUID,
            agent_thoughts: list[AgentThought],
    ):
        """存储智能体推理步骤消息"""
        with flask_app.app_context():
            # 1. 定义变量存储推理位置信息
            position = 0
            latency = 0

            # 2. 在子线程中，重新查询conversation和message，确保对象会被子线程管理到
            conversation: Conversation = self.get(Conversation, conversation_id)
            message: Message = self.get(Message, message_id)

            # 3. 循环遍历所有智能体推理过程执行存储操作
            for agent_thought in agent_thoughts:

                # 4. 存储长期记忆召回、推理、消息、动作、知识库检索等步骤
                if agent_thought.event in [
                    QueueEvent.LONG_TERM_MEMORY_RECALL,
                    QueueEvent.AGENT_THOUGHT,
                    QueueEvent.AGENT_MESSAGE,
                    QueueEvent.AGENT_ACTION,
                    QueueEvent.DATASET_RETRIEVAL,
                ]:
                    # 5. 更新位置及总耗时
                    position += 1
                    latency += agent_thought.latency

                    self.create(
                        MessageAgentThought,
                        app_id=app_id,
                        conversation_id=conversation.id,
                        message_id=message.id,
                        invoke_from=InvokeFrom.DEBUGGER,
                        created_by=account_id,
                        position=position,
                        event=agent_thought.event,
                        thought=agent_thought.thought,
                        observation=agent_thought.observation,
                        tool=agent_thought.tool,
                        tool_input=agent_thought.tool_input,
                        # 消息相关数据
                        message=agent_thought.message,
                        message_token_count=agent_thought.message_token_count,
                        message_unit_price=agent_thought.message_unit_price,
                        message_price_unit=agent_thought.message_price_unit,
                        # # 答案相关字段
                        answer=agent_thought.answer,
                        answer_token_count=agent_thought.answer_token_count,
                        answer_unit_price=agent_thought.answer_unit_price,
                        answer_price_unit=agent_thought.answer_price_unit,
                        # agent推理统计
                        total_token_count=agent_thought.total_token_count,
                        total_price=agent_thought.total_price,
                        latency=agent_thought.latency,
                    )

                # 7. 检测事件是否为agent_message
                # 如果是agent_message类型事件，则表明该消息已输出完毕，更新消息内容和耗时
                if agent_thought.event == QueueEvent.AGENT_MESSAGE:
                    # 8. 更新消息
                    self.update(
                        message,
                        # 消息相关字段
                        message=agent_thought.message,
                        message_token_count=agent_thought.message_token_count,
                        message_unit_price=agent_thought.message_unit_price,
                        message_price_unit=agent_thought.message_price_unit,
                        # 答案相关字段
                        answer=agent_thought.answer,
                        answer_token_count=agent_thought.answer_token_count,
                        answer_unit_price=agent_thought.answer_unit_price,
                        answer_price_unit=agent_thought.answer_price_unit,
                        # Agent推理统计相关
                        total_token_count=agent_thought.total_token_count,
                        total_price=agent_thought.total_price,
                        latency=latency,
                    )
                    # 9. 完成了消息的输出，如果开启了会话长期记忆，生成新的总结摘要，并更新长期记忆
                    if app_config["long_term_memory"]["enable"]:
                        # 根据人类消息、AI消息、原始的摘要信息总结生成一段新的摘要
                        new_summary = self.summary(
                            message.query,  # 人类消息
                            agent_thought.answer,  # AI消息
                            conversation.summary,  # 旧的摘要总结
                        )
                        self.update(
                            conversation,
                            summary=new_summary,
                        )

                    # 10. 处理新生成会话名称，如果会话是第一次创建，那么就生成会话名称
                    if conversation.is_new:
                        new_conversation_name = self.generate_conversation_name(message.query)

                        # 更新会话长期记忆、会话名称
                        self.update(
                            conversation,
                            name=new_conversation_name,
                        )

                # 11. 如果是停止或错误，更新消息状态
                if agent_thought.event in [QueueEvent.STOP, QueueEvent.ERROR, QueueEvent.TIMEOUT]:
                    self.update(
                        message,
                        status=agent_thought.event,
                        error=agent_thought.observation,
                    )
                    break

    def get_conversation_messages_with_page(
            self,
            conversation_id: UUID,
            req: GetConversationMessagesWithPageReq,
            account: Account
    ):
        """根据传递的会话id+请求数据，获取当前账号下该会话的消息分页列表数据"""
        # 1. 获取会话并校验权限
        conversation = self.get_conversation(conversation_id, account)

        # 2. 构建分页器并设置游标条件
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
                ~Message.is_deleted,
                *filters,
            ).order_by(desc("created_at"))
        )

        return messages, paginator

    def get_conversation(self, conversation_id: UUID, account: Account) -> Conversation:
        """根据传递的会话id+account，获取指定的会话信息"""
        # 1. 根据conversation_id查询会话记录
        conversation: Conversation = self.get(Conversation, conversation_id)
        if (
                not conversation
                or conversation.created_by != account.id
                or conversation.is_delete
        ):
            raise NotFoundException("该会话不存在或被删除，请核实后重试")

        return conversation

    def update_conversation(self, conversation_id: UUID, account: Account, **kwargs) -> Conversation:
        """根据传递的会话id+账号+kwargs更新胡话信息"""
        # 1. 获取会话记录并校验权限
        conversation = self.get_conversation(conversation_id, account)

        # 2. 更新会话信息
        self.update(conversation, **kwargs)

        return conversation

    def delete_message(self, conversation_id: UUID, message_id: UUID, account: Account) -> Message:
        """根据传递的会话id+消息id删除指定的消息记录"""
        # 1. 获取会话记录并校验权限
        conversation = self.get_conversation(conversation_id, account)

        # 2. 获取消息并校验权限
        message = self.get_message(message_id, account)

        # 3. 判断消息和会话是否关联
        if conversation.id != message.conversation_id:
            raise NotFoundException("该会话下不存在该消息，请核实后重试")

        # 4. 校验通过修改消息is_deleted属性标记删除
        self.update(message, is_deleted=True)

        return message

    def get_message(self, message_id: UUID, account: Account) -> Message:
        """根据传递的消息id+账号，获取指定的消息"""
        # 1. 根据message_id查询消息记录
        message = self.get(Message, message_id)

        if (
                not message
                or message.created_by != account.id
                or message.is_deleted
        ):
            raise NotFoundException("该消息不存在或被删除，请核实后重试")

        # 2. 校验通过返回消息
        return message

    def delete_conversation(self, conversation_id: UUID, account: Account) -> Conversation:
        """根据传递的会话id+账号删除指定的会话记录"""
        # 1. 获取会话记录并校验权限
        conversation: Conversation = self.get_conversation(conversation_id, account)

        # 2. 更新会话的删除状态
        self.update(conversation, is_delete=True)

        return conversation
