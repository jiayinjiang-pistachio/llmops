#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/22 12:12
@Author         : jiayinkong@163.com
@File           : workflow_entity.py
@Description    : 
"""
from typing import Any, TypedDict, Annotated

from langchain_core.pydantic_v1 import BaseModel, Field

from internal.core.workflow.entities.node_entity import NodeResult


def _process_dict(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    """工作流状态字典归纳函数"""
    left = left or {}
    right = right or {}

    return {**left, **right}


def _process_node(left: list[NodeResult], right: list[NodeResult]) -> NodeResult:
    left = left or []
    right = right or []

    return left + right


class WorkflowConfig(BaseModel):
    """工作流配置信息"""
    name: str = ""  # 工作流名称
    description: str = ""  # 工作流描述信息
    nodes: list[dict[str, Any]] = Field(default_factory=list)  # 工作流对应的节点
    edges: list[dict[str, Any]] = Field(default_factory=list)  # 工作流对应的边


class WorkflowState(TypedDict):
    """工作流图程序字典"""
    inputs: Annotated[dict[str, Any], _process_dict]  # 工作流的最初始输入，也就是工具输入
    outputs: Annotated[dict[str, Any], _process_dict]  # 工作流的最终结果，也就是工具输出
    node_results: Annotated[list[NodeResult], _process_node]  # 各个节点的运行结果
