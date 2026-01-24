#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/22 16:24
@Author         : jiayinkong@163.com
@File           : variable_entity.py
@Description    : 
"""
from enum import Enum
from typing import Union, Any
from uuid import UUID

from langchain_core.pydantic_v1 import BaseModel, Field


class VariableType(str, Enum):
    STRING = "string"
    INT = "int"
    FLOAT = "float"
    BOOLEAN = "boolean"


VariableTypeMap = {
    VariableType.STRING: str,
    VariableType.INT: int,
    VariableType.FLOAT: float,
    VariableType.BOOLEAN: bool,
}

VariableTypeDefaultValueMap = {
    VariableType.STRING: "",
    VariableType.INT: 0,
    VariableType.FLOAT: 0,
    VariableType.BOOLEAN: False,
}


class VariableValueType(str, Enum):
    Ref = "ref"  # 引用类型
    LITERAL = "literal"  # 直接输入
    GENERATED = "generated"  # 生成的值，一般用在开始节点/output中


class VariableEntity(BaseModel):
    """变量实体信息"""

    class Value(BaseModel):
        """变量的实体值信息"""

        class Content(BaseModel):
            """如果变量值类型是引用类型，则使用Content记录引用节点id+引用节点的变量名"""
            ref_node_id: UUID
            ref_var_name: str

        type: VariableValueType = VariableValueType.LITERAL
        content: Union[Content, str, int, float, bool] = ""

    name: str = ""  # 变量名
    description: str = ""  # 变量描述
    required: bool = True  # 是否必填
    type: VariableType = VariableType.STRING  # 变量类型
    value: Value = Field(default_factory=lambda: {"type": VariableValueType.LITERAL, "content": ""})  # 变量的值
    meta: dict[str, Any] = Field(default_factory=dict)  # 变量元数据，存储一些额外信息
