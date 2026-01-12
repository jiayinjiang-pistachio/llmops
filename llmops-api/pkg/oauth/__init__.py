#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/11 15:52
@Author         : jiayinkong@163.com
@File           : __init__.py.py
@Description    : 
"""
from .github_oauth import GithubOAuth, OAuthUserInfo
from .oauth import OAuth

__all__ = [
    "OAuth",
    "GithubOAuth",
    "OAuthUserInfo",
]
