#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/2/1 16:13
@Author         : jiayinkong@163.com
@File           : chat.py
@Description    : 
"""
from langchain_community.chat_models import ChatZhipuAI

from internal.core.language_model.entities.model_entity import BaseLanguageModel


class Chat(ChatZhipuAI, BaseLanguageModel):
    """智谱AI聊天模型"""
    ...
