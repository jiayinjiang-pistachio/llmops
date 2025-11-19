#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/16 07:59
@Author         : jiayinkong@163.com
@File           : __init__.py.py
@Description    : 存储公用的异常信息
"""
from .exception import (
    CustomException,
    FailException,
    NotFoundException,
    UnAuthorizationException,
    ForbiddenException,
    ValidationException,
)

__all__ = [
    "CustomException",
    "FailException",
    "NotFoundException",
    "UnAuthorizationException",
    "ForbiddenException",
    "ValidationException",
]
