#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/24 11:30
@Author         : jiayinkong@163.com
@File           : http_request_entity.py
@Description    : 
"""
from enum import Enum

from langchain_core.pydantic_v1 import HttpUrl, Field, validator

from internal.core.workflow.entities.node_entity import BaseNodeData
from internal.core.workflow.entities.variable_entity import VariableEntity, VariableType, VariableValueType
from internal.exception import ValidationException


class HttpRequestMethod(str, Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"
    HEAD = "head"
    OPTIONS = "options"


class HttpRequestInputType(str, Enum):
    """http请求输入变量类型"""
    PARAMS = "params"  # query参数
    HEADERS = "headers"  # header请求头
    BODY = "body"  # body参数


class HttpRequestNodeData(BaseNodeData):
    """http请求节点信息"""
    url: HttpUrl = ""  # 请求URL地址
    method: HttpRequestMethod = HttpRequestMethod.GET
    inputs: list[VariableEntity] = Field(default_factory=list)
    outputs: list[VariableEntity] = Field(
        default_factory=lambda: [
            VariableEntity(
                name="status_code",
                type=VariableType.INT,
                value={"type": VariableValueType.GENERATED, "content": 0}
            ),
            VariableEntity(
                name="text",
                value={"type": VariableValueType.GENERATED}
            )
        ]
    )

    @validator("inputs")
    def validate_inputs(cls, inputs: list[VariableEntity]) -> list[VariableEntity]:
        """校验输入列表数据"""
        for input in inputs:
            if input.meta.get("type") not in HttpRequestInputType.__members__.values():
                raise ValidationException("Http请求参数结构出错")
        return inputs
