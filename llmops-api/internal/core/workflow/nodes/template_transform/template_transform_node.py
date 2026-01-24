#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/23 11:47
@Author         : jiayinkong@163.com
@File           : template_transform_node.py
@Description    : 
"""
from typing import Optional

from jinja2 import Template
from langchain_core.runnables import RunnableConfig

from internal.core.workflow.entities.node_entity import NodeResult, NodeStatus
from internal.core.workflow.entities.workflow_entity import WorkflowState
from internal.core.workflow.nodes import BaseNode
from .template_transform_entity import templateTransformNodeData
from ...utils.helper import extract_variables_from_state


class TemplateTransformNode(BaseNode):
    node_data_cls = templateTransformNodeData

    def invoke(self, state: WorkflowState, config: Optional[RunnableConfig] = None) -> WorkflowState:
        """模板转换节点执行函数"""
        inputs_dict = extract_variables_from_state(self.node_data.inputs, state)

        # 使用jinja2格式模板信息
        template = Template(self.node_data.template)
        template_value = template.render(**inputs_dict)

        outputs = {
            "output": template_value
        }

        return {
            "node_results": [
                NodeResult(
                    node_data=self.node_data,
                    inputs=inputs_dict,
                    outputs=outputs,
                    status=NodeStatus.SUCCEEDED,
                )
            ]
        }
