#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/16 09:21
@Author         : jiayinkong@163.com
@File           : app_handler.py
@Description    : 
"""
import os

from flask import request
from openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from internal.schema.app_schema import CompletionReq


class AppHandler:
    """应用控制器"""

    def completion(self):
        """聊天接口"""
        # 1. 提取从接口中获取的输入
        req = CompletionReq()
        if not req.validate():
            return req.errors

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
        return content

    def ping(self):
        return {"ping": "pong123"}
