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

    def get_pricing(self) -> tuple[float, float, float]:
        """获取LLM对应的价格信息，返回数据格式为：（输入价格、输出价格、单位）"""

        # 1. 计算获取输入价格、输出价格、单位
        input_price = self.metadata.get("pricing", {}).get("input", 0.0)
        output_price = self.metadata.get("pricing", {}).get("output", 0.0)
        unit = self.metadata.get("pricing").get("unit", 0.0)

        return input_price, output_price, unit
