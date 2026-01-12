#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/11 15:52
@Author         : jiayinkong@163.com
@File           : oauth.py
@Description    : 
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class OAuthUserInfo:
    """oauth用户基信息，只记录id/name/email"""
    id: str
    name: str
    email: str


@dataclass
class OAuth(ABC):
    """第三方OAuth授权认证基础类"""
    client_id: str  # 客户端id
    client_secret: str  # 客户端密钥
    redirect_uri: str  # 重定向uri

    @abstractmethod
    def get_provider(self) -> str:
        """获取服务提供者对应的名字"""
        pass

    @abstractmethod
    def get_authorization_url(self):
        """获取跳转授权认证的URL方法"""

    @abstractmethod
    def get_access_token(self, code: str):
        """根据传递的code代码，获取授权令牌"""
        pass

    @abstractmethod
    def get_raw_user_info(self, token: str):
        """根据传入的token获取OAuth原始信息"""
        pass

    def get_user_info(self, token: str):
        """根据传入的token获取OAuthUserInfo用户信息"""
        raw_info = self.get_raw_user_info(token)
        return self._transform_user_info(raw_info)

    @abstractmethod
    def _transform_user_info(self, raw_info: dict) -> OAuthUserInfo:
        """将OAuth原始信息转成OAuthUserInfo"""
        pass
