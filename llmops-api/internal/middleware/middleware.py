#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/11 14:50
@Author         : jiayinkong@163.com
@File           : middleware.py
@Description    : 
"""
from dataclasses import dataclass
from typing import Optional

from flask import Request
from injector import inject

from internal.exception import UnAuthorizationException
from internal.model import Account
from internal.service import AccountService, JwtService


@inject
@dataclass
class Middleware:
    """应用中间件，可以重写request_loader与unauthorized_handler"""
    jwt_service: JwtService
    account_service: AccountService

    def request_loader(self, request: Request) -> Optional[Account]:
        """登录管理器的请求加载器"""
        # 1. 单独为llmops蓝图创建请求加载器
        if request.blueprint == "llmops":
            # 2. 提取请求头中的header信息
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise UnAuthorizationException("该接口需要授权才能访问，请登录后重试")

            # 3. 请求信息中没有空格符，则校验失败，Authorization: Bearer access_token
            if " " not in auth_header:
                raise UnAuthorizationException("该接口需要授权才能访问，验证格式失败")
            # 4. 分割信息必须符合格式：Bearer access_token
            access_schema, access_token = auth_header.split(None, 1)
            if access_token.lower() != "bearer":
                raise UnAuthorizationException("该接口需要授权才能访问，验证格式失败")

            # 5. 解析token信息得到用户信息并返回
            payload = self.jwt_service.parse_token(access_token)
            account_id = payload.get("sub")
            return self.account_service.get_account(account_id)

        else:
            return None
