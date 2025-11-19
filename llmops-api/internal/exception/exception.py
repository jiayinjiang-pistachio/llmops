#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/18 07:01
@Author         : jiayinkong@163.com
@File           : exception.py
@Description    : 
"""
from dataclasses import field
from typing import Any

from pkg.response import HttpCode


class CustomException(Exception):
    """基础自定义异常"""
    code: HttpCode = HttpCode.FAIL
    msg: str = ""
    data: Any = field(default_factory=dict)

    def __init__(self, msg: str = None, data: Any = None):
        super().__init__()
        self.msg = msg
        self.data = data


class FailException(CustomException):
    """通用失败异常"""
    pass


class NotFoundException(CustomException):
    """未找到数据异常"""
    code = HttpCode.NOT_FOUND


class UnAuthorizationException(CustomException):
    """未授权数据异常"""
    code = HttpCode.UNAUTHORIZED


class ForbiddenException(CustomException):
    """无权限数据异常"""
    code = HttpCode.FORBIDDEN


class ValidationException(CustomException):
    """校验异常"""
    code = HttpCode.VALIDATE_ERROR
