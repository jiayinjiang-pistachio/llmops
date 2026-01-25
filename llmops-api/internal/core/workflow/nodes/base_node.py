#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/22 16:14
@Author         : jiayinkong@163.com
@File           : base_node.py
@Description    : 
"""
from abc import ABC

from langchain_core.runnables import RunnableSerializable

from internal.core.workflow.entities.node_entity import BaseNodeData


class BaseNode(RunnableSerializable, ABC):
    """基础节点类"""
    node_data: BaseNodeData
