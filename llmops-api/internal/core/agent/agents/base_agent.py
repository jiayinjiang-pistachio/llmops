#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/8 11:28
@Author         : jiayinkong@163.com
@File           : base_agent.py
@Description    : 
"""
from abc import ABC, abstractmethod

from langchain_core.messages import AnyMessage

from internal.core.agent.entities.agent_entity import AgentConfig


class BaseAgent(ABC):
    """LLMOps项目基础Agent"""
    agent_config: AgentConfig

    def __init__(self, agent_config: AgentConfig):
        """构造函数，初始化智能体图结构程序"""
        self.agent_config = agent_config

    @abstractmethod
    def run(
            self,
            query: str,  # 用户提的原始问题
            history: list[AnyMessage] = None,  # 短期记忆
            long_term_memory: str = "",  # 长期记忆
    ):
        """智能体运行函数，传递原始提问query、长期记忆、并调用智能体生成相应内容"""
        raise NotImplementedError("Agent智能体的run函数未实现")
