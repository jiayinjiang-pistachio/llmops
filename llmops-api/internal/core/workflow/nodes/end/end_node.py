#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/22 17:32
@Author         : jiayinkong@163.com
@File           : end_node.py
@Description    : 
"""
import time
from typing import Optional

from langchain_core.runnables import RunnableConfig

from internal.core.workflow.entities.node_entity import NodeResult, NodeStatus
from internal.core.workflow.entities.workflow_entity import WorkflowState
from internal.core.workflow.nodes import BaseNode
from internal.core.workflow.nodes.end.end_entity import EndNodeData
from internal.core.workflow.utils.helper import extract_variables_from_state


class EndNode(BaseNode):
    node_data = EndNodeData

    def invoke(self, state: WorkflowState, config: Optional[RunnableConfig] = None) -> WorkflowState:
        """结束节点执行函数"""
        start_at = time.perf_counter()

        # 提取节点中需要输出的数据
        outputs_dict = extract_variables_from_state(self.node_data.outputs, state)

        return {
            "outputs": outputs_dict,
            "node_results": [
                NodeResult(
                    node_data=self.node_data,
                    inputs={},
                    outputs=outputs_dict,
                    status=NodeStatus.SUCCEEDED,
                    latency=(time.perf_counter() - start_at),
                )
            ]
        }
