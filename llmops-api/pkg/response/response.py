#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/17 22:33
@Author         : jiayinkong@163.com
@File           : response.py
@Description    : 
"""
from dataclasses import field, dataclass
from typing import Any, Union, Generator

from flask import jsonify, Response as FlaskResponse, stream_with_context

from .http_code import HttpCode


@dataclass
class Response:
    """基础http接口响应格式"""
    code: HttpCode = HttpCode.SUCCESS
    message: str = ""
    data: Any = field(default_factory=dict)


def json(data: Response = None):
    """基础的响应接口"""
    return jsonify(data), 200


def success_json(data: Any = None):
    """成功数据响应"""
    return json(Response(code=HttpCode.SUCCESS, message="", data=data))


def fail_json(data: Any = None):
    """失败数据响应"""
    return json(Response(code=HttpCode.FAIL, message="", data=data))


def validate_error_json(errors: dict = None):
    """数据验证错误响应"""
    first_key = next(iter(errors))  # next(iterator) 调用迭代器的 __next__() 方法，返回下一个元素
    if first_key is not None:
        msg = errors.get(first_key)[0]
    else:
        msg = ""
    return json(Response(code=HttpCode.VALIDATE_ERROR, message=msg, data=errors))


def message(code: HttpCode = None, msg: str = ""):
    """基础的消息响应，固定返回消息提示，数据返回空字典"""
    return json(Response(code=code, message=msg, data={}))


def success_message(msg: str = ""):
    """成功消息响应"""
    return message(code=HttpCode.SUCCESS, msg=msg)


def fail_message(msg: str = ""):
    """失败消息响应"""
    return message(code=HttpCode.FAIL, msg=msg)


def not_found_message(msg: str = ""):
    """未找到消息响应"""
    return message(code=HttpCode.NOT_FOUND, msg=msg)


def unauthorized_message(msg: str = ""):
    """未授权消息响应"""
    return message(code=HttpCode.UNAUTHORIZED, msg=msg)


def forbidden_message(msg: str = ""):
    """无权限消息响应"""
    return message(code=HttpCode.FORBIDDEN, msg=msg)


def compact_generate_response(response: Union[Response, Generator]) -> FlaskResponse:
    """统一合并处理块输出和流式事件输出"""
    if isinstance(response, Response):
        return json(response)
    else:
        # 2. response 格式为生成器，代表本次响应需要执行流式响应输出
        def generate() -> Generator:
            # 构建generate函数，流式从response中获取数据
            yield from response

        # 返回携带上下文的流式事件输出
        return FlaskResponse(
            stream_with_context(generate()),
            status=200,
            mimetype="text/event-stream",
        )
