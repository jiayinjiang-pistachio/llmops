#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/23 18:13
@Author         : jiayinkong@163.com
@File           : tool_entity.py
@Description    : 
"""
from typing import Any

from langchain_core.pydantic_v1 import Field

from internal.core.workflow.entities.node_entity import BaseNodeData
from internal.core.workflow.entities.variable_entity import VariableEntity, VariableValueType


class ToolNodeData(BaseNodeData):
    """工具节点信息"""
    tool_type: str = Field(alias="type")  # 工具类型
    provider_id: str  # 工具提供者id
    tool_id: str  # 工具id
    params: dict[str, Any] = Field(default_factory=dict)  # 内置工具设置参数
    inputs: list[VariableEntity] = Field(default_factory=list)  # 节点输入列表
    outputs: list[VariableEntity] = Field(
        default_factory=lambda: [
            VariableEntity(name="text", value={"type": VariableValueType.GENERATED})
        ]
    )  # 节点输出列表
