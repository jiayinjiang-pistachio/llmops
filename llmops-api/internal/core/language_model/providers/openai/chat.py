#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/2/1 11:09
@Author         : jiayinkong@163.com
@File           : chat.py
@Description    : 
"""
from langchain_openai import ChatOpenAI

from internal.core.language_model.entities.model_entity import BaseLanguageModel


class Chat(ChatOpenAI, BaseLanguageModel):
    """OpenAI聊天模型基类"""
    pass
