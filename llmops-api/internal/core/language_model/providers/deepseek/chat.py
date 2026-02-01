#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/2/1 18:17
@Author         : jiayinkong@163.com
@File           : chat.py
@Description    : 
"""
from langchain_openai.chat_models.base import BaseChatOpenAI

from internal.core.language_model.entities.model_entity import BaseLanguageModel


class Chat(BaseChatOpenAI, BaseLanguageModel):
    """deepseek聊天模型基础类"""

    def __init__(self, api_key: str, base_url: str, **kwargs):
        super().__init__(openai_api_key=api_key, openai_api_base=base_url, **kwargs)
