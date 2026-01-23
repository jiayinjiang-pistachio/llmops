#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/22 16:22
@Author         : jiayinkong@163.com
@File           : start_entity.py
@Description    : 
"""
from langchain_core.pydantic_v1 import Field

from internal.core.workflow.entities.node_entity import BaseNodeData
from internal.core.workflow.entities.variable_entity import VariableEntity


class StartNodeData(BaseNodeData):
    """开始节点信息"""
    inputs: list[VariableEntity] = Field(default_factory=list)
