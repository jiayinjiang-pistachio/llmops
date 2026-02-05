#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/2/1 18:17
@Author         : jiayinkong@163.com
@File           : chat.py
@Description    : 
"""
import json
from typing import List

import tiktoken
from langchain_core.messages import BaseMessage
from langchain_openai.chat_models.base import BaseChatOpenAI

from internal.core.language_model.entities.model_entity import BaseLanguageModel


class Chat(BaseChatOpenAI, BaseLanguageModel):
    """deepseek聊天模型基础类"""

    def __init__(self, api_key: str, base_url: str, **kwargs):
        super().__init__(openai_api_key=api_key, openai_api_base=base_url, **kwargs)

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        """手动计算 Token 数量，支持 DeepSeek 的 cl100k_base 编码"""
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
        except Exception:
            # 兜底逻辑：如果无法获取编码器，按字符长度估算
            return sum(len(str(m.content)) // 2 + 3 for m in messages) + 3

        num_tokens = 0
        for message in messages:
            num_tokens += 3  # 每条消息的角色前缀等消耗
            content = message.content or ""
            if isinstance(content, list):
                content = json.dumps(content)
            num_tokens += len(encoding.encode(content))

        num_tokens += 3  # 结束 bonus
        return num_tokens
