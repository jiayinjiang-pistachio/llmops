#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/22 16:14
@Author         : jiayinkong@163.com
@File           : base_node.py
@Description    : 
"""
from abc import ABC
from typing import Any, ClassVar

from langchain_core.runnables import RunnableSerializable

from internal.core.workflow.entities.node_entity import BaseNodeData


class BaseNode(RunnableSerializable, ABC):
    """基础节点类"""
    # node_data_cls: type[BaseNodeData]
    # 关键修改：使用 ClassVar 显式声明这是一个类变量
    node_data_cls: ClassVar[type[BaseNodeData]]
    node_data: BaseNodeData

    def __init__(self, *args, node_data: dict[str, Any], **kwargs: Any):
        # 此时通过类名访问就不会出错了
        cls_data = self.__class__.node_data_cls(**node_data)
        super().__init__(*args, node_data=cls_data, **kwargs)
