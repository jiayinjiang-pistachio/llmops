#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/22 17:32
@Author         : jiayinkong@163.com
@File           : end_node.py
@Description    : 
"""
from typing import Optional

from langchain_core.runnables import RunnableConfig

from internal.core.workflow.entities.node_entity import NodeResult, NodeStatus
from internal.core.workflow.entities.variable_entity import VariableEntity, VariableValueType, \
    VariableTypeDefaultValueMap
from internal.core.workflow.entities.workflow_entity import WorkflowState
from internal.core.workflow.nodes import BaseNode
from internal.core.workflow.nodes.end.end_entity import EndNodeData


class EndNode(BaseNode):
    node_data_cls = EndNodeData

    def invoke(self, state: WorkflowState, config: Optional[RunnableConfig] = None) -> WorkflowState:
        """结束节点执行函数"""
        outputs: list[VariableEntity] = self.node_data.outputs

        outputs_dict = {}
        for output in outputs:

            print("output: ", output)

            if output.value.type == VariableValueType.LITERAL:
                # 直接输入类型，直接输出
                outputs_dict[output.name] = output.value.content
                print("直接类型", output.name)
            else:
                # 引用类型
                for node_result in state["node_results"]:
                    # 找到当前输出内容节点所引用的上一层节点
                    if output.name == "youdao_suggest_result":
                        print("youdao_suggest_result: ", output.value.content.ref_node_id == node_result.node_data.id)
                    if output.value.content.ref_node_id == node_result.node_data.id:
                        print("output_name: ", output.name, node_result.node_data.id)
                        outputs_dict[output.name] = node_result.outputs.get(
                            output.value.content.ref_var_name,
                            VariableTypeDefaultValueMap.get(output.type)
                        )

        print("outputs_dict: ", outputs_dict)

        return {
            "outputs": outputs_dict,
            "node_results": [
                NodeResult(
                    node_data=self.node_data,
                    inputs={},
                    outputs=outputs_dict,
                    status=NodeStatus.SUCCEEDED,
                )
            ]
        }
