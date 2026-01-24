#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/22 16:51
@Author         : jiayinkong@163.com
@File           : start_node.py
@Description    : 
"""
from typing import Optional

from langchain_core.runnables import RunnableConfig

from internal.core.workflow.entities.node_entity import NodeResult, NodeStatus
from internal.core.workflow.entities.variable_entity import VARIABLE_TYPE_DEFAULT_VALUE_MAP
from internal.core.workflow.entities.workflow_entity import WorkflowState
from internal.core.workflow.nodes import BaseNode
from internal.core.workflow.nodes.start.start_entity import StartNodeData
from internal.exception import FailException


class StartNode(BaseNode):
    # 这里不需要写类型标注，直接赋值即可，它会覆盖基类的 ClassVar
    node_data_cls = StartNodeData

    def invoke(self, state: WorkflowState, config: Optional[RunnableConfig] = None) -> WorkflowState:
        """开始节点执行函数，提取状态中的输入数据并生成节点结果"""
        # node_data = self._node_data_cls(**self.node_data)

        # 提取节点数据中的输入数据
        inputs = self.node_data.inputs

        outputs = {}
        for input in inputs:
            input_value = state["inputs"].get(input.name, None)

            if input_value is None:
                if input.required:
                    raise FailException(f"工作流参数生成出错，{input.name}为必填参数")
                else:
                    input_value = VARIABLE_TYPE_DEFAULT_VALUE_MAP.get(input.type)

            outputs[input.name] = input_value

        return {
            "node_results": [
                NodeResult(
                    node_data=self.node_data,
                    status=NodeStatus.SUCCEEDED,
                    inputs=state["inputs"],
                    outputs=outputs,
                )
            ]
        }
