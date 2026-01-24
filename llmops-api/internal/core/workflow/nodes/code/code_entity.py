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

DEFAULT_CODE = """
def main(params):
    return params
"""


class CodeNodeData(BaseNodeData):
    """python代码节点信息"""
    code: str = DEFAULT_CODE  # 需要执行的python代码
    inputs: list[VariableEntity] = Field(default_factory=list)  # 输入变量列表
    outputs: list[VariableEntity] = Field(default_factory=list)  # 输出变量列表
