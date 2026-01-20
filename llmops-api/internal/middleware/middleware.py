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
from internal.service import AccountService, JwtService, ApiKeyService


@inject
@dataclass
class Middleware:
    """应用中间件，可以重写request_loader与unauthorized_handler"""
    jwt_service: JwtService
    account_service: AccountService
    api_key_service: ApiKeyService

    def request_loader(self, request: Request) -> Optional[Account]:
        """登录管理器的请求加载器"""
        # 1. 单独为llmops蓝图创建请求加载器
        if request.blueprint == "llmops":
            # 2. 校验获取access_token
            access_token = self._validate_credential(request)

            # 3. 解析token信息得到用户信息并返回
            payload = self.jwt_service.parse_token(access_token)
            account_id = payload.get("sub")
            return self.account_service.get_account(account_id)

        elif request.blueprint == "openapi":
            # 4. 校验获取access_token
            access_token = self._validate_credential(request)

            # 5. 解析得到API密钥记录
            api_key_record = self.api_key_service.get_api_by_credential(access_token)

            # 6. 判断Api密钥记录是否存在，不存在则抛出错误
            if not api_key_record or not api_key_record.is_active:
                raise UnAuthorizationException("该密钥不存在或未激活")

            return api_key_record.account

        else:
            return None

    @classmethod
    def _validate_credential(cls, request: Request) -> str:
        """校验请求头中的凭证信息，涵盖access_token和api_key"""
        # 1. 提取请求头headers中的信息
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise UnAuthorizationException("该接口需要授权才能访问，请登录后重试")

        # 3. 请求信息中没有空格符，则校验失败，Authorization: Bearer access_token
        if " " not in auth_header:
            raise UnAuthorizationException("该接口需要授权才能访问，验证格式失败")

        # 4. 分割信息必须符合格式：Bearer access_token
        access_schema, credential = auth_header.split(None, 1)
        if access_schema.lower() != "bearer":
            raise UnAuthorizationException("该接口需要授权才能访问，验证格式失败")

        return credential
