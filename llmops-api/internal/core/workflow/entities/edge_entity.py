#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/24 20:33
@Author         : jiayinkong@163.com
@File           : edge_entity.py
@Description    : 
"""
from uuid import UUID

from langchain_core.pydantic_v1 import BaseModel

from internal.core.workflow.entities.node_entity import NodeType


class BaseEdgeData(BaseModel):
    """基础边数据"""
    id: UUID
    source: UUID  # 边起点对应的节点id
    source_type: NodeType
    target: UUID  # 边目标点对应的节点id
    target_type: NodeType
