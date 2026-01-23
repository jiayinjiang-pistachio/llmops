#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/22 17:30
@Author         : jiayinkong@163.com
@File           : end_entity.py
@Description    : 
"""
from langchain_core.pydantic_v1 import Field

from internal.core.workflow.entities.node_entity import BaseNodeData
from internal.core.workflow.entities.variable_entity import VariableEntity


class EndNodeData(BaseNodeData):
    outputs: list[VariableEntity] = Field(default_factory=list)
