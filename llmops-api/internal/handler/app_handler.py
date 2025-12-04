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
from uuid import UUID

from injector import inject
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
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

        # 2. 构建组件
        prompt = ChatPromptTemplate.from_template("{query}")
        llm = ChatOpenAI(
            model="gpt-4",
            api_key=os.getenv("GPTSAPI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE"),
        )
        parser = StrOutputParser()

        # 3. 构建链
        chain = prompt | llm | parser
        content = chain.invoke({"query": req.query.data})

        # 4. 调用链得到结果
        return success_json({"content": content})

    def ping(self):
        raise FailException("数据未找到")
