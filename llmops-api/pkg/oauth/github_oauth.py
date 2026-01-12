#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/11 16:12
@Author         : jiayinkong@163.com
@File           : github_oauth.py
@Description    : 
"""
import urllib.parse

import requests

from .oauth import OAuth, OAuthUserInfo


class GithubOAuth(OAuth):
    """GithubOAuth第三方授权认证类"""
    _AUTHORIZE_URL = "https://github.com/login/oauth/authorize"  # 跳转授权接口
    _ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"  # 获取授权令牌接口
    # 修改后 (增加 api. 前缀)
    _USER_INFO_URL = "https://api.github.com/user"
    _EMAIL_INFO_URL = "https://api.github.com/user/emails"

    def get_provider(self) -> str:
        return "github"

    def get_authorization_url(self):
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "user:email",  # 只请求用户的基本信息
        }
        return f"{self._AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"

    def get_access_token(self, code: str):
        # 1. 组装请求数据
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        headers = {"Accept": "application/json"}

        # 2. 发起post请求并获取相应数据
        resp = requests.post(self._ACCESS_TOKEN_URL, data=data, headers=headers)
        resp.raise_for_status()
        resp_json = resp.json()

        # 提取access_token
        access_token = resp_json.get("access_token")
        if not access_token:
            raise ValueError(f"OAuth授权失败：{resp_json}")

        return access_token

    def get_raw_user_info(self, token: str):
        # 1. 组装请求数据
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "ZenSnack-LLMOps",  # GitHub API 强制要求
            "Accept": "application/json"
        }

        # 2. 发起get请求获取用户数据
        resp = requests.get(self._USER_INFO_URL, headers=headers)

        # 如果报错，打印出内容方便调试
        if resp.status_code != 200:
            print(f"GitHub API Error: {resp.text}")

        resp.raise_for_status()
        raw_info = resp.json()

        # 3. 发起get请求获取邮箱数据
        email_resp = requests.get(self._EMAIL_INFO_URL, headers=headers)
        email_resp.raise_for_status()
        email_info = email_resp.json()

        # 4. 提取邮箱数据
        primary_email = next((email for email in email_info if email.get("primary", None)), None)
        return {**raw_info, "email": primary_email.get("email", None)}

    def _transform_user_info(self, raw_info: dict) -> OAuthUserInfo:
        # 1. 提取邮箱，如果不存在设置一个默认邮箱
        email = raw_info.get("email")

        if not email:
            email = f"{raw_info.get('id')}+{raw_info.get('login')}@user.no-reply@github.com"

        # 2. 组装数据
        return OAuthUserInfo(
            id=str(raw_info.get("id")),
            name=str(raw_info.get("name")),
            email=str(email),
        )
