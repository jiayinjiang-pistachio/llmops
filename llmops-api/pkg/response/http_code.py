#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/17 21:46
@Author         : jiayinkong@163.com
@File           : http_code.py
@Description    : 
"""
from enum import Enum


class HttpCode(str, Enum):
    """http基础业务状态码"""
    SUCCESS = "success"  # 成功状态码
    FAIL = "fail"  # 失败状态码
    NOT_FOUND = "not_found"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    VALIDATE_ERROR = "validate_error"
