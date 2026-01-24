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
from internal.core.workflow.entities.variable_entity import VariableEntity, VariableValueType, \
    VariableTypeDefaultValueMap
from internal.core.workflow.entities.workflow_entity import WorkflowState
from internal.core.workflow.nodes import BaseNode
from .template_transform_entity import templateTransformNodeData


class TemplateTransformNode(BaseNode):
    node_data_cls = templateTransformNodeData

    def invoke(self, state: WorkflowState, config: Optional[RunnableConfig] = None) -> WorkflowState:
        """模板转换节点执行函数"""
        inputs: list[VariableEntity] = self.node_data.inputs

        input_dict = {}
        for input in inputs:
            # 判断input的值类型
            if input.value.type == VariableValueType.LITERAL:
                input_dict[input.name] = input.value.content
            else:
                # input 的值是引用类型
                # 循环上一个节点的node_results
                for node_result in state["node_results"]:
                    # 寻找当前input所对应的引用节点
                    if input.value.content.ref_node_id == node_result.node_data.id:
                        input_dict[input.name] = node_result.outputs.get(
                            input.value.content.ref_var_name,
                            VariableTypeDefaultValueMap.get(input.type)
                        )

        # 使用jinja2格式模板信息
        template = Template(self.node_data.template)
        template_value = template.render(**input_dict)

        outputs = {}
        if self.node_data.outputs:
            outputs[self.node_data.outputs[0].name] = template_value
        else:
            outputs["output"] = template_value

        return {
            "node_results": [
                NodeResult(
                    node_data=self.node_data,
                    inputs=input_dict,
                    outputs=outputs,
                    status=NodeStatus.SUCCEEDED,
                )
            ]
        }
