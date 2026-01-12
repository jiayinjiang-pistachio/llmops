#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/11 11:57
@Author         : jiayinkong@163.com
@File           : jwt_service.py
@Description    : 
"""
import os
from dataclasses import dataclass
from typing import Any

import jwt
from injector import inject

from internal.exception import UnAuthorizationException


@inject
@dataclass
class JwtService:
    """jwt服务"""

    @classmethod
    def generate_token(cls, payload: dict[str, Any]) -> str:
        """根据传递的载荷信息生成token信息"""
        secret_key = os.getenv("JWT_SECRET_KEY")
        return jwt.encode(payload, secret_key, algorithm="HS256")

    @classmethod
    def parse_token(cls, token: str) -> dict[str, Any]:
        """解析传入的token信息得到载荷"""

        # # 【新增】强制清洗 token，确保不带 Bearer 前缀
        # if token and token.startswith("Bearer "):
        #     token = token.replace("Bearer ", "", 1).strip()

        secret_key = os.getenv("JWT_SECRET_KEY")

        try:
            return jwt.decode(token, secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise UnAuthorizationException("授权认证凭证已过期，请重新登录")
        except jwt.InvalidTokenError as e:
            # 打印具体的错误原因，比如 'Signature verification failed'
            print(f"DEBUG: JWT Error Detail: {str(e)}")
            raise UnAuthorizationException("解析token出错，请重新登录")
        except Exception as e:
            raise e
