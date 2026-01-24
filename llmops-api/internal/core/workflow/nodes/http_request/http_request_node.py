#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/24 11:30
@Author         : jiayinkong@163.com
@File           : http_request_node.py
@Description    : 
"""
from typing import Optional

import requests
from langchain_core.runnables import RunnableConfig

from internal.core.workflow.entities.node_entity import NodeResult, NodeStatus
from internal.core.workflow.entities.variable_entity import VariableEntity, VariableValueType, \
    VariableTypeDefaultValueMap
from internal.core.workflow.entities.workflow_entity import WorkflowState
from internal.core.workflow.nodes import BaseNode
from internal.core.workflow.nodes.http_request.http_request_entity import HttpRequestNodeData, HttpRequestInputType, \
    HttpRequestMethod


class HttpRequestNode(BaseNode):
    node_data_cls = HttpRequestNodeData

    def invoke(self, state: WorkflowState, config: Optional[RunnableConfig] = None) -> WorkflowState:
        """http request 节点执行函数"""
        inputs: list[VariableEntity] = self.node_data.inputs

        _input_dict = {}
        for input in inputs:
            # 判断input的值类型
            if input.value.type == VariableValueType.LITERAL:
                _input_dict[input.name] = input.value.content
            else:
                # input 的值是引用类型
                # 循环上一个节点的node_results
                for node_result in state["node_results"]:
                    # 寻找当前input所对应的引用节点
                    if input.value.content.ref_node_id == node_result.node_data.id:
                        _input_dict[input.name] = node_result.outputs.get(
                            input.value.content.ref_var_name,
                            VariableTypeDefaultValueMap.get(input.type)
                        )

        inputs_dict = {
            HttpRequestInputType.PARAMS: {},
            HttpRequestInputType.HEADERS: {},
            HttpRequestInputType.BODY: {},
        }
        for input in inputs:
            inputs_dict[input.meta.get("type")][input.name] = _input_dict.get(input.name)

        # 请求方法映射
        request_methods = {
            HttpRequestMethod.GET: requests.get,
            HttpRequestMethod.POST: requests.post,
            HttpRequestMethod.PUT: requests.put,
            HttpRequestMethod.PATCH: requests.patch,
            HttpRequestMethod.DELETE: requests.delete,
            HttpRequestMethod.HEAD: requests.head,
            HttpRequestMethod.OPTIONS: requests.options,
        }

        # 根据传递的method+URL发起请求
        request_method = request_methods[self.node_data.method]
        if self.node_data.method == HttpRequestMethod.GET:
            response = request_method(
                self.node_data.url,
                headers=inputs_dict[HttpRequestInputType.HEADERS],
                params=inputs_dict[HttpRequestInputType.PARAMS],
            )

        else:
            # 其他请求方法需携带body参数
            response = request_method(
                self.node_data.url,
                headers=inputs_dict[HttpRequestInputType.HEADERS],
                params=inputs_dict[HttpRequestInputType.PARAMS],
                data=inputs_dict[HttpRequestInputType.BODY],
            )

        # 获取相应文本和状态码
        text = response.text
        status_code = response.status_code

        # 构建输出结构
        outputs = {"text": text, "status_code": status_code}

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
