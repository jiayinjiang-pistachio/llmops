#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/22 14:42
@Author         : jiayinkong@163.com
@File           : node_entity.py
@Description    : 
"""
from enum import Enum
from typing import Any
from uuid import UUID

from langchain_core.pydantic_v1 import BaseModel, Field


class NodeType(str, Enum):
    START = "start"
    LLM = "llm"
    TOOL = "tool"
    DATASET_RETRIEVAL = "dataset_retrieval"
    CODE = "code"
    HTTP_REQUEST = "http_request"
    TEMPLATTE_TRANSFORM = "template_transform"
    END = "end"


class BaseNodeData(BaseModel):
    """基础节点数据"""

    class Position(BaseModel):
        """节点坐标基础模型"""
        x: float = 0
        y: float = 0

    class Config:
        allow_population_by_field_name = True  # 允许通过字段名赋值

    id: UUID  # 节点id，数值必须唯一
    node_type: NodeType  # 节点类型
    title: str = ""  # 节点标题，数据也必须唯一
    description: str = ""  # 节点描述信息
    position: Position = Field(default_factory=lambda: {"x": 0, "y": 0})


class NodeStatus(str, Enum):
    """节点运行状态"""
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class NodeResult(BaseModel):
    """节点运行结果"""
    node_data: BaseNodeData  # 节点基础数据
    inputs: dict[str, Any] = Field(default_factory=dict)  # 节点输入数据
    outputs: dict[str, Any] = Field(default_factory=dict)  # 节点的输出数据
    error: str = ""  # 节点运行错误信息
    status: NodeStatus = NodeStatus.RUNNING  # 节点运行状态
    latency: float = 0  # 节点响应耗时
