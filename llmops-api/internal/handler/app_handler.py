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

from flask import request
from injector import inject
from openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

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

    def completion(self):
        """聊天接口"""
        # 1. 提取从接口中获取的输入
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)

        query = request.json.get("query")
        # 2. 构建openai客户端并发起请求
        client = OpenAI(
            api_key=os.getenv("GPTSAPI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE"),
        )

        # 3. 得到请求响应，把响应传给前端
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                ChatCompletionSystemMessageParam(
                    role="system",
                    content="你是OpenAI开发的聊天机器人，请根据用户的输入回复对应的信息",
                ),
                ChatCompletionUserMessageParam(
                    role="user",
                    content=query,
                )
            ]
        )

        content = completion.choices[0].message.content
        return success_json({"content": content})

    def ping(self):
        raise FailException("数据未找到")
