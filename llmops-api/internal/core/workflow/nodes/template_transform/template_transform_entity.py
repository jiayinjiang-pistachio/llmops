#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/23 11:43
@Author         : jiayinkong@163.com
@File           : template_transform_entity.py
@Description    : 
"""
from langchain_core.pydantic_v1 import Field, validator

from internal.core.workflow.entities.node_entity import BaseNodeData
from internal.core.workflow.entities.variable_entity import VariableEntity, VariableValueType


class TemplateTransformNodeData(BaseNodeData):
    template: str  # 需要拼接转换的字符串模板
    inputs: list[VariableEntity] = Field(default=list)
    outputs: list[VariableEntity] = Field(
        default_factory=lambda: [
            VariableEntity(name="output", value={"type": VariableValueType.GENERATED})
        ]
    )

    @validator("outputs", pre=True)
    def validate_outputs(cls, value: list[VariableEntity]) -> list[VariableEntity]:
        return [
            VariableEntity(name="output", value={"type": VariableValueType.GENERATED})
        ]
