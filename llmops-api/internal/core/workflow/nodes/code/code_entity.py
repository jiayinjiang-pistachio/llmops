#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/23 16:47
@Author         : jiayinkong@163.com
@File           : code_entity.py
@Description    : 
"""
from langchain_core.pydantic_v1 import Field

from internal.core.workflow.entities.node_entity import BaseNodeData
from internal.core.workflow.entities.variable_entity import VariableEntity


def DefaultCode():
    return """
def main(params):
    return params"""


class CodeNodeData(BaseNodeData):
    """python代码节点信息"""
    code: str = DefaultCode()
    inputs: list[VariableEntity] = Field(default_factory=list)
    outputs: list[VariableEntity] = Field(default_factory=list)
