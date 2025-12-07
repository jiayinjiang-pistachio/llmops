#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/16 09:21
@Author         : jiayinkong@163.com
@File           : app_handler.py
@Description    : 
"""
import os
import uuid
from dataclasses import dataclass
from operator import itemgetter
from uuid import UUID

from injector import inject
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI

from internal.exception import FailException
from internal.schema.app_schema import CompletionReq
from internal.service import AppService
from pkg.response import success_json, validate_error_json, success_message


@inject
@dataclass
class AppHandler:
    """应用控制器"""
    appService: AppService

    def create_app(self):
        """调用服务创建新的app记录"""
        app = self.appService.create_app()
        return success_message(f"应用创建成功，id是{app.id}")

    def get_app(self, id: uuid.UUID):
        app = self.appService.get_app(id)
        return success_message(f"应用已经成功获取，名称是{app.name}")

    def update_app(self, id: uuid.UUID):
        app = self.appService.update_app(id)
        return success_message(f"应用已经成功修改，修改后的名称是：{app.name}")

    def delete_app(self, id: uuid.UUID):
        app = self.appService.delete_app(id)
        return success_message(f"应用已经成功删除，id为{app.id}")

    def debug(self, app_id: UUID):
        """聊天接口"""
        # 1. 提取从接口中获取的输入
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2. 构建prompt和记忆
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个强大的聊天机器人，能根据用户的提问回复对应的问题"),
            MessagesPlaceholder("history"),
            ("human", "{query}")
        ])
        memory = ConversationBufferWindowMemory(
            k=3,
            input_key="query",
            return_messages=True,
            output_key="output",
            chat_memory=FileChatMessageHistory("./storage/memory/chat_history.txt")
        )

        # 3. 创建llm
        llm = ChatOpenAI(
            model="gpt-4",
            api_key=os.getenv("GPTSAPI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE"),
        )

        # 4. 创建链应用
        chain = RunnablePassthrough.assign(
            history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
        ) | prompt | llm | StrOutputParser()

        # 5. 调用链生成内容
        chain_input = {"query": req.query.data}
        content = chain.invoke(chain_input)
        memory.save_context(chain_input, {"output": content})

        return success_json({"content": content})

    def ping(self):
        raise FailException("数据未找到")
