#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/23 10:23
@Author         : jiayinkong@163.com
@File           : llm_entity.py
@Description    : 
"""
from typing import Any

from langchain_core.pydantic_v1 import Field

from internal.core.workflow.entities.node_entity import BaseNodeData
from internal.core.workflow.entities.variable_entity import VariableEntity, VariableValueType
from internal.entity.app_entity import DEFAULT_APP_CONFIG


class LLMNodeData(BaseNodeData):
    """LLM节点信息"""
    prompt: str = ""  # 大语言模型节点提示词
    language_model_config: dict[str, Any] = Field(
        alias="model_config",
        default_factory=lambda: DEFAULT_APP_CONFIG["model_config"]
    )
    inputs: list[VariableEntity] = Field(default_factory=list)
    outputs: list[VariableEntity] = Field(
        exclude=True,  # 即使外界传入outputs也不改变默认值
        default_factory=lambda: [
            VariableEntity(
                name="output",
                value={"type": VariableValueType.GENERATED}
            )
        ]
    )
