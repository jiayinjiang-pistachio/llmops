#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/23 14:23
@Author         : jiayinkong@163.com
@File           : dataset_retrieval_node.py
@Description    : 
"""
from typing import Optional, Any
from uuid import UUID

from flask import Flask
from langchain_core.pydantic_v1 import PrivateAttr
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool

from internal.core.workflow.entities.node_entity import NodeResult, NodeStatus
from internal.core.workflow.entities.variable_entity import VariableEntity, VariableValueType, \
    VariableTypeDefaultValueMap
from internal.core.workflow.entities.workflow_entity import WorkflowState
from internal.core.workflow.nodes import BaseNode
from internal.core.workflow.nodes.dataset_retrieval.dataset_retrieval_entity import DatasetRetrievalNodeData


class DatasetRetrievalNode(BaseNode):
    node_data_cls = DatasetRetrievalNodeData
    _retrieval_tool: BaseTool = PrivateAttr(None)

    def __init__(self, *args, flask_app: Flask, account_id: UUID, node_data: dict[str, Any], **kwargs: Any):
        super().__init__(*args, node_data=node_data, **kwargs)

        from app.http.module import injector
        from internal.service.retrieval_service import RetrievalService

        # 导入依赖注入及检索服务
        retrieval_service: RetrievalService = injector.get(RetrievalService)

        # 构建检索服务工具
        self._retrieval_tool = retrieval_service.create_langchain_tool_from_search(
            flask_app=flask_app,
            dataset_ids=self.node_data.dataset_ids,
            account_id=account_id,
            **self.node_data.retrieval_config.dict(),
        )

    def invoke(self, state: WorkflowState, config: Optional[RunnableConfig] = None) -> WorkflowState:
        """知识库检索节点执行函数，得到知识库检索的结果"""
        query_input: VariableEntity = self.node_data.inputs[0]

        inputs_dict = {}
        if query_input.value.type == VariableValueType.LITERAL:
            # 直接输入类型
            inputs_dict[query_input.name] = query_input.value.content
        else:
            # 引用类型
            for node_result in state["node_results"]:
                if query_input.value.content.ref_node_id == node_result.node_data.id:
                    # 找到引用节点
                    inputs_dict[query_input.name] = node_result.outputs.get(
                        query_input.value.content.ref_var_name,
                        VariableTypeDefaultValueMap.get(query_input.type)
                    )

        # 调用知识库检索工具
        combine_documents = self._retrieval_tool.invoke(inputs_dict)

        # 构建输出结构
        outputs = {}
        if self.node_data.outputs:
            outputs[self.node_data.outputs[0].name] = combine_documents
        else:
            outputs["combine_documents"] = combine_documents

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
